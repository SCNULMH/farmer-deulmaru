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
from app.services.demo_data import get_crop_schedule, get_grants, get_pest_guides, normalize_region
from app.services.diagnosis import predict_disease
from app.services.public_data import CROP_NAMES, fetch_consult_detail, fetch_support_detail, search_consults, search_pests

router = APIRouter()


class OkResponse(BaseModel):
    ok: bool


def current_user_id(request: Request) -> str:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user["id"]


@router.get("/grants")
async def grants(
    request: Request,
    keyword: str = "",
    region: str = "",
    age: int | None = None,
    status: str = "",
    start_date: str = "",
    end_date: str = "",
) -> list[dict]:
    user = request.session.get("user")
    selected_region = normalize_region(region or (user or {}).get("region", "전국"))
    return get_grants(
        user,
        keyword=keyword,
        region=selected_region,
        age=age,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/grants/{grant_id}")
async def grant_detail(grant_id: str, request: Request) -> dict:
    detail = fetch_support_detail(grant_id)
    if detail:
        return detail
    grant = next((item for item in get_grants(request.session.get("user")) if item["id"] == grant_id), None)
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
            "image": "",
        }
        for idx, item in enumerate(get_pest_guides(query), start=1)
    ]


@router.get("/ncpms/pest-detail/{sick_key}")
async def ncpms_pest_detail(sick_key: str) -> dict:
    from app.services.public_data import fetch_pest_detail

    detail = fetch_pest_detail(sick_key)
    if detail:
        return detail
    return {
        "symptom": "상세 증상 정보를 불러오지 못했습니다. 병해충 사전 검색 결과와 현장 증상을 함께 확인하세요.",
        "action": "정확한 방제 여부는 농업기술센터 또는 NCPMS 원문 정보를 함께 확인한 뒤 결정하세요.",
        "images": [],
    }


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


@router.get("/ncpms/consult-detail/{consult_id}")
async def ncpms_consult_detail(consult_id: str) -> dict:
    detail = fetch_consult_detail(consult_id)
    if detail:
        return detail
    return {
        "id": consult_id,
        "title": "상담 상세 예시",
        "request": "작물 잎에 반점이 생기고 생육이 약해지는 증상을 문의한 사례입니다.",
        "opinion": "정확한 병명은 현장 증상과 사진 확인이 필요하며, 병해충 사전의 증상 정보와 비교한 뒤 방제 여부를 결정하세요.",
        "images": [],
    }


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
    grant = next((item for item in get_grants(request.session.get("user")) if item["id"] == grant_id), None)
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
        disease_query = (
            result.get("disease", "")
            .replace("의심", "")
            .replace("주의", "")
            .replace("추가 확인 필요", "")
            .strip()
        )
        related = []
        if disease_query:
            related = search_pests(disease_query, "sick", limit=3)
        if not related:
            related = search_pests(crop_name, "crop", limit=3)
        if not related:
            related = [
                {
                    "sick_key": f"fallback-{idx}",
                    "crop": item.get("crop", crop_name),
                    "name": item.get("name", "병해충 정보"),
                    "english_name": "",
                    "thumb": "",
                    "image": "",
                    "symptom": item.get("symptom", ""),
                    "action": item.get("action", ""),
                }
                for idx, item in enumerate(get_pest_guides(crop_name), start=1)
            ]
        result["related_pests"] = related
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
    grants = get_grants(request.session.get("user"))
    return {
        "overall": {"grantId": grants[0]["id"], "interestCount": 24, **grants[0]} if grants else None,
        "ageGender": {"grantId": grants[1]["id"], "interestCount": 17, **grants[1]} if len(grants) > 1 else None,
        "region": {"grantId": grants[2]["id"], "interestCount": 11, **grants[2]} if len(grants) > 2 else None,
    }
