from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from app.services.db import (
    add_interest,
    list_diagnosis_history,
    list_interests,
    remove_interest,
    save_diagnosis,
)
from app.services.demo_data import get_crop_schedule, get_grants, get_pest_guides
from app.services.diagnosis import predict_disease

router = APIRouter()


def current_user_id(request: Request) -> str:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user["id"]


@router.get("/grants")
def grants() -> list[dict]:
    return get_grants()


@router.get("/crop-schedule/{crop_name}")
def crop_schedule(crop_name: str) -> dict:
    return get_crop_schedule(crop_name)


@router.get("/pests")
def pests() -> list[dict]:
    return get_pest_guides()


@router.get("/interests")
def interests(request: Request) -> list[dict]:
    return list_interests(current_user_id(request))


@router.post("/interests/{grant_id}")
def add_grant_interest(grant_id: str, request: Request) -> dict:
    grant = next((item for item in get_grants() if item["id"] == grant_id), None)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    add_interest(current_user_id(request), grant)
    return {"ok": True}


@router.delete("/interests/{grant_id}")
def delete_grant_interest(grant_id: str, request: Request) -> dict:
    remove_interest(current_user_id(request), grant_id)
    return {"ok": True}


@router.get("/diagnosis/history")
def diagnosis_history(request: Request) -> list[dict]:
    return list_diagnosis_history(current_user_id(request))


@router.post("/diagnosis")
async def diagnosis(
    request: Request,
    crop_name: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    user_id = current_user_id(request)
    result = await predict_disease(crop_name=crop_name, file=file)
    if result.get("ok"):
        save_diagnosis(user_id, result)
    return result
