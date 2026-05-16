from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
from pathlib import Path

from fastapi import UploadFile

from app.core.settings import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

DEMO_RESULTS = {
    "토마토": ("토마토잎곰팡이병 의심", 84),
    "고추": ("고추탄저병 의심", 78),
    "상추": ("추가 확인 필요", 60),
    "딸기": ("딸기잿빛곰팡이병 의심", 67),
}


def sanitize_filename(filename: str | None) -> str:
    name = Path(filename or "uploaded-image").name[:120]
    return re.sub(r"[^0-9A-Za-z가-힣._ -]", "_", name) or "uploaded-image"


def normalize_crop_name(crop_name: str) -> str:
    crop = crop_name.strip()
    aliases = {
        "토마토": "토마토",
        "방울토마토": "토마토",
        "고추": "고추",
        "딸기": "딸기",
        "참외": "참외",
        "포도": "포도",
        "상추": "상추",
    }
    return aliases.get(crop, crop)


def resolve_model_path() -> Path:
    path = Path(settings.diagnosis_model_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def validate_upload(file: UploadFile, content: bytes) -> dict | None:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        return {
            "ok": False,
            "message": "JPG, PNG, WEBP 형식의 작물 이미지만 업로드할 수 있습니다.",
        }
    if len(content) > settings.max_image_upload_bytes:
        max_mb = settings.max_image_upload_bytes // (1024 * 1024)
        return {"ok": False, "message": f"이미지 파일은 {max_mb}MB 이하로 업로드해 주세요."}
    if not content:
        return {"ok": False, "message": "이미지 파일을 다시 선택해 주세요."}
    return None


def demo_prediction(crop_name: str, filename: str, size_kb: float, reason: str = "") -> dict:
    disease, confidence = DEMO_RESULTS.get(crop_name, ("추가 확인 필요", 60))
    result = {
        "ok": True,
        "crop": crop_name,
        "filename": filename,
        "size_kb": size_kb,
        "disease": disease,
        "confidence": confidence,
        "next_action": "NCPMS 병해충 정보와 현장 증상을 함께 확인한 뒤 방제 여부를 결정하세요.",
        "model_mode": "demo",
    }
    if reason:
        result["model_note"] = reason
    return result


def run_model_worker(crop_name: str, filename: str, size_kb: float, content: bytes) -> dict:
    model_path = resolve_model_path()
    worker_path = Path(__file__).with_name("diagnosis_worker.py")
    if not model_path.exists() or not worker_path.exists():
        return demo_prediction(crop_name, filename, size_kb, "모델 파일을 찾지 못해 데모 결과를 표시했습니다.")

    payload = {
        "crop": crop_name,
        "filename": filename,
        "size_kb": size_kb,
        "model_path": str(model_path),
        "image_base64": base64.b64encode(content).decode("ascii"),
    }

    try:
        completed = subprocess.run(
            [sys.executable, str(worker_path)],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=settings.diagnosis_timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return demo_prediction(crop_name, filename, size_kb, "모델 추론 시간이 길어 데모 결과를 표시했습니다.")
    except Exception:
        return demo_prediction(crop_name, filename, size_kb, "모델 워커 실행에 실패해 데모 결과를 표시했습니다.")

    if completed.returncode != 0:
        return demo_prediction(crop_name, filename, size_kb, "모델 추론 프로세스가 종료되어 데모 결과를 표시했습니다.")

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return demo_prediction(crop_name, filename, size_kb, "모델 응답을 해석하지 못해 데모 결과를 표시했습니다.")

    if not result.get("ok") and "모델 추론" in result.get("message", ""):
        return demo_prediction(crop_name, filename, size_kb, result.get("message", "모델 추론 오류로 데모 결과를 표시했습니다."))
    if not result.get("ok"):
        return result
    result["model_mode"] = result.get("model_mode") or "pytorch"
    return result


async def predict_disease(crop_name: str, file: UploadFile) -> dict:
    """Run crop disease prediction without persisting uploaded images."""

    content = await file.read()
    upload_error = validate_upload(file, content)
    if upload_error:
        return upload_error

    normalized_crop = normalize_crop_name(crop_name)
    filename = sanitize_filename(file.filename)
    size_kb = round(len(content) / 1024, 1)

    return run_model_worker(normalized_crop, filename, size_kb, content)
