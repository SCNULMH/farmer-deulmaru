from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel

from app.services.db import (
    add_interest,
    delete_diagnosis,
    list_diagnosis_history,
    list_interests,
    remove_interest,
    save_diagnosis,
)
from app.services.demo_data import get_crop_schedule, get_grants, get_pest_guides
from app.services.diagnosis import predict_disease
from app.services.public_data import CROP_NAMES, fetch_support_detail, search_consults, search_pests

router = APIRouter()


class OkResponse(BaseModel):
    ok: bool


def current_user_id(request: Request) -> str:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user["id"]


@router.get("/grants")
async def grants() -> list[dict]:
    return get_grants()


@router.get("/grants/{grant_id}")
async def grant_detail(grant_id: str) -> dict:
    detail = fetch_support_detail(grant_id)
    if detail:
        return detail
    grant = next((item for item in get_grants() if item["id"] == grant_id), None)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return {
        "id": grant["id"],
        "title": grant["title"],
        "target": grant["reason"],
        "period": grant["deadline"],
        "agency": grant["source"],
        "content": grant["reason"],
        "url": "",
    }


@router.get("/crop-schedule/{crop_name}")
async def crop_schedule(crop_name: str) -> dict:
    return get_crop_schedule(crop_name)


@router.get("/crop-schedule")
async def legacy_crop_schedule(cropName: str = "토마토") -> dict:
    return get_crop_schedule(cropName)


@router.get("/crop-names")
async def crop_names() -> list[str]:
    return CROP_NAMES


@router.get("/pests")
async def pests(crop: str = "토마토") -> list[dict]:
    return get_pest_guides(crop)


@router.get("/ncpms/search")
async def ncpms_search(query: str = "토마토", search_type: str = "crop") -> list[dict]:
    results = search_pests(query, search_type)
    if results:
        return results
    return [
        {
            "sick_key": f"fallback-{idx}",
            "crop": item["crop"],
            "name": item["name"],
            "english_name": "",
            "thumb": "",
        }
        for idx, item in enumerate(get_pest_guides(query), start=1)
    ]


@router.get("/ncpms/consult")
async def ncpms_consult(query: str = "토마토", page: int = 1) -> list[dict]:
    results = search_consults(query, page)
    if results:
        return results
    return [
        {
            "id": "demo-consult",
            "title": f"{query} 재배 상담 예시",
            "crop": query,
            "date": "",
            "summary": "API 응답이 없을 때 표시하는 데모 상담 사례입니다. 현장 증상과 병해충 가이드를 함께 확인하세요.",
        }
    ]


@router.get("/interests")
async def interests(request: Request) -> list[dict]:
    return list_interests(current_user_id(request))


@router.get("/interest/list")
async def legacy_interest_list(request: Request) -> list[dict]:
    return list_interests(current_user_id(request))


@router.get("/interest/check")
async def legacy_interest_check(grantId: str, request: Request) -> dict:
    exists = any(item.get("grant_id") == grantId or item.get("grantId") == grantId for item in list_interests(current_user_id(request)))
    return {"exists": exists}


@router.post("/interest/add")
async def legacy_interest_add(
    request: Request,
    grantId: str = Form(...),
    applEdDt: str = Form("상시/공고 확인"),
    title: str = Form("지원사업"),
) -> dict:
    add_interest(
        current_user_id(request),
        {
            "id": grantId,
            "title": title,
            "deadline": applEdDt,
        },
    )
    return {"ok": True, "message": "관심 지원사업으로 저장했습니다."}


@router.delete("/interest/cancel")
async def legacy_interest_cancel(grantId: str, request: Request) -> dict:
    remove_interest(current_user_id(request), grantId)
    return {"ok": True, "message": "관심 지원사업을 취소했습니다."}


@router.post("/interests/{grant_id}", response_model=OkResponse)
async def add_grant_interest(grant_id: str, request: Request) -> OkResponse:
    grant = next((item for item in get_grants() if item["id"] == grant_id), None)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    add_interest(current_user_id(request), grant)
    return OkResponse(ok=True)


@router.delete("/interests/{grant_id}", response_model=OkResponse)
async def delete_grant_interest(grant_id: str, request: Request) -> OkResponse:
    remove_interest(current_user_id(request), grant_id)
    return OkResponse(ok=True)


@router.get("/diagnosis/history")
async def diagnosis_history(request: Request) -> list[dict]:
    return list_diagnosis_history(current_user_id(request))


@router.get("/ident/history")
async def legacy_ident_history(request: Request) -> list[dict]:
    return [
        {
            "id": item.get("id"),
            "cropName": item.get("crop"),
            "diseaseName": item.get("disease"),
            "confidence": item.get("confidence"),
            "createdAt": item.get("created_at"),
            **item,
        }
        for item in list_diagnosis_history(current_user_id(request))
    ]


@router.delete("/diagnosis/history/{diagnosis_id}", response_model=OkResponse)
async def delete_diagnosis_history(diagnosis_id: str, request: Request) -> OkResponse:
    delete_diagnosis(current_user_id(request), diagnosis_id)
    return OkResponse(ok=True)


@router.delete("/ident/delete/{diagnosis_id}", response_model=OkResponse)
async def legacy_ident_delete(diagnosis_id: str, request: Request) -> OkResponse:
    delete_diagnosis(current_user_id(request), diagnosis_id)
    return OkResponse(ok=True)


@router.post("/ident/save")
async def legacy_ident_save(
    request: Request,
    diseaseName: str = Form(...),
    cropName: str = Form(...),
) -> dict:
    save_diagnosis(
        current_user_id(request),
        {
            "crop": cropName,
            "disease": diseaseName,
            "confidence": 70,
            "filename": None,
        },
    )
    return {"ok": True, "message": "진단 이력을 저장했습니다."}


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


@router.get("/recommendation/overall")
async def recommendation_overall() -> list[dict]:
    return [
        {"grantId": item["id"], "interestCount": max(1, 30 - index * 7), **item}
        for index, item in enumerate(get_grants()[:3])
    ]


@router.get("/recommendation/personal")
async def recommendation_personal(request: Request) -> dict:
    current_user_id(request)
    grants = get_grants()
    return {
        "overall": {"grantId": grants[0]["id"], "interestCount": 24, **grants[0]} if grants else None,
        "ageGender": {"grantId": grants[1]["id"], "interestCount": 17, **grants[1]} if len(grants) > 1 else None,
        "region": {"grantId": grants[2]["id"], "interestCount": 11, **grants[2]} if len(grants) > 2 else None,
    }
