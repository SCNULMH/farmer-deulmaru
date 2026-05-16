from __future__ import annotations

import io
import re
from functools import lru_cache
from pathlib import Path

from fastapi import UploadFile

from app.core.settings import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

CLASS_LABELS = {
    0: "정상",
    1: "고추탄저병",
    2: "고추마일드모틀바이러스병",
    3: "딸기잿빛곰팡이병",
    4: "딸기흰가루병",
    5: "참외노균병",
    6: "참외흰가루병",
    7: "토마토잎곰팡이병",
    8: "토마토황화잎말이바이러스병",
    9: "포도탄저병",
}

CROP_CLASS_INDICES = {
    "고추": [0, 1, 2],
    "딸기": [0, 3, 4],
    "참외": [0, 5, 6],
    "토마토": [0, 7, 8],
    "포도": [0, 9],
}

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


@lru_cache(maxsize=1)
def load_model():
    model_path = resolve_model_path()
    if not model_path.exists():
        return None

    try:
        import torch
        from torchvision import models
    except ImportError:
        return None

    try:
        state_dict = torch.load(model_path, map_location=torch.device("cpu"), weights_only=True)
    except TypeError:
        state_dict = torch.load(model_path, map_location=torch.device("cpu"))

    model = models.resnet50(weights=None)
    if any(key.startswith("fc.3.") for key in state_dict):
        model.fc = torch.nn.Sequential(
            torch.nn.Linear(model.fc.in_features, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(512, len(CLASS_LABELS)),
        )
    else:
        model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_LABELS))

    model.load_state_dict(state_dict)
    model.eval()
    return model


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


def demo_prediction(crop_name: str, filename: str, size_kb: float) -> dict:
    disease, confidence = DEMO_RESULTS.get(crop_name, ("추가 확인 필요", 60))
    return {
        "ok": True,
        "crop": crop_name,
        "filename": filename,
        "size_kb": size_kb,
        "disease": disease,
        "confidence": confidence,
        "next_action": "NCPMS 병해충 정보와 현장 증상을 함께 확인한 뒤 방제 여부를 결정하세요.",
        "model_mode": "demo",
    }


def model_prediction(crop_name: str, filename: str, size_kb: float, content: bytes) -> dict:
    import torch
    import torch.nn.functional as F
    from PIL import Image, UnidentifiedImageError
    from torchvision import transforms

    model = load_model()
    if model is None:
        return demo_prediction(crop_name, filename, size_kb)

    try:
        image = Image.open(io.BytesIO(content)).convert("RGB")
    except UnidentifiedImageError:
        return {"ok": False, "message": "이미지 파일을 읽을 수 없습니다. 다른 이미지를 선택해 주세요."}

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )

    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        probabilities = F.softmax(model(tensor), dim=1).squeeze()

    valid_indices = CROP_CLASS_INDICES.get(crop_name, list(CLASS_LABELS.keys()))
    predicted_index = max(valid_indices, key=lambda index: float(probabilities[index]))
    confidence = round(float(probabilities[predicted_index]) * 100, 1)
    disease = CLASS_LABELS.get(predicted_index, "추가 확인 필요")

    if predicted_index == 0:
        next_action = "정상 가능성이 높습니다. 재배 환경과 잎·열매 상태를 주기적으로 관찰하세요."
    elif confidence < 60:
        next_action = "신뢰도가 낮습니다. 다른 각도의 사진으로 다시 진단하고 NCPMS 정보를 함께 확인하세요."
    else:
        next_action = "NCPMS 병해충 정보와 현장 증상을 함께 확인한 뒤 방제 여부를 결정하세요."

    return {
        "ok": True,
        "crop": crop_name,
        "filename": filename,
        "size_kb": size_kb,
        "disease": disease,
        "confidence": confidence,
        "next_action": next_action,
        "model_mode": "pytorch",
    }


async def predict_disease(crop_name: str, file: UploadFile) -> dict:
    """Run crop disease prediction without persisting uploaded images."""

    content = await file.read()
    upload_error = validate_upload(file, content)
    if upload_error:
        return upload_error

    normalized_crop = normalize_crop_name(crop_name)
    filename = sanitize_filename(file.filename)
    size_kb = round(len(content) / 1024, 1)

    try:
        return model_prediction(normalized_crop, filename, size_kb, content)
    except Exception:
        return demo_prediction(normalized_crop, filename, size_kb)
