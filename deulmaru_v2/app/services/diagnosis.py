from __future__ import annotations

from fastapi import UploadFile


async def predict_disease(crop_name: str, file: UploadFile) -> dict:
    """Demo-safe diagnosis adapter.

    A real PyTorch model can replace the rule below without changing the route
    or UI. This keeps contest demos stable while model work continues.
    """

    content = await file.read()
    size_kb = round(len(content) / 1024, 1)

    if not content:
        return {"ok": False, "message": "이미지 파일이 비어 있습니다."}

    suggested = {
        "토마토": ("잎곰팡이병 의심", 84),
        "고추": ("탄저병 의심", 78),
        "참외": ("흰가루병 의심", 81),
        "포도": ("정상 또는 초기 증상", 67),
    }
    disease, confidence = suggested.get(crop_name, ("분석 대기", 60))

    return {
        "ok": True,
        "crop": crop_name,
        "filename": file.filename,
        "size_kb": size_kb,
        "disease": disease,
        "confidence": confidence,
        "next_action": "NCPMS 병해충 사전과 연결해 증상, 예찰, 방제 정보를 확인하세요.",
        "model_mode": "demo",
    }
