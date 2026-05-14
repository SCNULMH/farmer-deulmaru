from __future__ import annotations

from fastapi import UploadFile


async def predict_disease(crop_name: str, file: UploadFile) -> dict:
    """Demo-safe diagnosis adapter.

    A real PyTorch model can replace this function without changing the route
    or UI contract. Uploaded images are read for prediction only and are not
    persisted to the local filesystem.
    """

    content = await file.read()
    size_kb = round(len(content) / 1024, 1)

    if not content:
        return {"ok": False, "message": "이미지 파일을 다시 선택해 주세요."}

    suggested = {
        "토마토": ("잎곰팡이병 의심", 84),
        "고추": ("탄저병 의심", 78),
        "상추": ("노균병 의심", 81),
        "딸기": ("잿빛곰팡이병 주의", 67),
    }
    disease, confidence = suggested.get(crop_name, ("추가 확인 필요", 60))

    return {
        "ok": True,
        "crop": crop_name,
        "filename": file.filename,
        "size_kb": size_kb,
        "disease": disease,
        "confidence": confidence,
        "next_action": "NCPMS 병해충 가이드와 현장 증상을 함께 확인한 뒤 방제 여부를 결정하세요.",
        "model_mode": "demo",
    }
