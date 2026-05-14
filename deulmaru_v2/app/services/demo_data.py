from __future__ import annotations

import re
from datetime import date

from app.core.settings import settings
from app.services.public_data import fetch_crop_schedule, fetch_pest_guides, fetch_support_grants

REGION_CODES = {
    "전국": "00",
    "서울": "11",
    "부산": "21",
    "대구": "22",
    "인천": "23",
    "광주": "24",
    "대전": "25",
    "울산": "26",
    "세종": "29",
    "경기": "31",
    "강원": "32",
    "충북": "33",
    "충남": "34",
    "전북": "35",
    "전남": "36",
    "경북": "37",
    "경남": "38",
    "제주": "39",
    "나주": "36",
    "전라남도": "36",
}

REGION_OPTIONS = [
    "전국",
    "서울",
    "부산",
    "대구",
    "인천",
    "광주",
    "대전",
    "울산",
    "세종",
    "경기",
    "강원",
    "충북",
    "충남",
    "전북",
    "전남",
    "경북",
    "경남",
    "제주",
]

DEMO_USER = {
    "name": "데모 청년농",
    "region": "전남 나주",
    "crop": "토마토",
    "stage": "정식 초기",
}

FALLBACK_GRANTS = [
    {
        "id": "grant-001",
        "title": "청년농 영농정착 지원사업",
        "source": "농림축산식품부",
        "deadline": "2026-06-14",
        "fit": 96,
        "reason": "초기 영농 정착 단계와 지역 조건이 잘 맞는 지원사업입니다.",
    },
    {
        "id": "grant-002",
        "title": "스마트팜 시설 개선 지원",
        "source": "농촌진흥청",
        "deadline": "2026-06-30",
        "fit": 88,
        "reason": "작물 관리 자동화와 생육 데이터 수집 계획에 활용할 수 있습니다.",
    },
    {
        "id": "grant-003",
        "title": "지역 농산물 판로 확대 바우처",
        "source": "지자체 농업기술센터",
        "deadline": "2026-07-05",
        "fit": 81,
        "reason": "지역 기반 직거래와 온라인 판매 준비에 도움이 됩니다.",
    },
]

FALLBACK_SCHEDULES = {
    "토마토": {
        "crop": "토마토",
        "source": "농사로 작물 재배 일정 API",
        "tasks": [
            {"period": "5월 중순", "task": "정식 후 뿌리 활착 상태와 관수 간격을 점검합니다."},
            {"period": "5월 하순", "task": "유인끈을 정리하고 하엽 제거로 통풍을 확보합니다."},
            {"period": "6월 초", "task": "착과 상태를 확인하고 칼슘 결핍 증상을 관찰합니다."},
        ],
    },
    "고추": {
        "crop": "고추",
        "source": "농사로 작물 재배 일정 API",
        "tasks": [
            {"period": "5월 중순", "task": "정식 후 활착과 초기 병해충 발생 여부를 확인합니다."},
            {"period": "5월 하순", "task": "지주대를 세우고 강풍 피해를 예방합니다."},
            {"period": "6월 초", "task": "탄저병 예방을 위해 배수와 통풍 상태를 점검합니다."},
        ],
    },
}

FALLBACK_PEST_GUIDES = [
    {
        "crop": "토마토",
        "name": "잎곰팡이병",
        "source": "NCPMS 병해충 정보",
        "symptom": "잎 뒷면에 회갈색 곰팡이가 생기고 잎이 마르기 시작합니다.",
        "action": "환기를 늘리고 감염 잎을 제거한 뒤 등록 약제를 기준에 맞게 사용합니다.",
    },
    {
        "crop": "고추",
        "name": "탄저병",
        "source": "NCPMS 병해충 정보",
        "symptom": "과실에 둥근 병반이 생기고 습할 때 빠르게 번질 수 있습니다.",
        "action": "배수를 개선하고 비가림 관리와 예방 방제를 병행합니다.",
    },
    {
        "crop": "상추",
        "name": "노균병",
        "source": "NCPMS 병해충 정보",
        "symptom": "잎에 노란 반점이 생기고 뒷면에 곰팡이가 보일 수 있습니다.",
        "action": "밀식을 피하고 야간 습도를 낮춰 병 확산을 줄입니다.",
    },
]


def get_dashboard_context(user: dict | None = None, diagnosis_history: list[dict] | None = None) -> dict:
    current_user = user or DEMO_USER
    crop = current_user.get("crop") or DEMO_USER["crop"]
    return {
        "today": date.today().isoformat(),
        "user": {
            "name": current_user.get("name", DEMO_USER["name"]),
            "region": current_user.get("region", DEMO_USER["region"]),
            "crop": crop,
            "stage": current_user.get("stage", DEMO_USER["stage"]),
        },
        "grants": get_grants(current_user),
        "schedule": get_crop_schedule(crop),
        "pests": get_pest_guides(crop),
        "diagnosis_history": diagnosis_history or [],
        "data_sources": [
            "농림축산식품부 청년농 지원사업 공공데이터",
            "농사로 작물 재배 일정",
            "NCPMS 병해충 정보",
            "지자체 농업기술센터 지원사업 공고",
        ],
    }


def get_grants(
    user: dict | None = None,
    *,
    keyword: str = "",
    region: str = "",
    age: int | None = None,
    status: str = "",
    start_date: str = "",
    end_date: str = "",
    page: int = 1,
    limit: int = 24,
) -> list[dict]:
    area_code = region_code(region)
    if not settings.use_demo_data:
        grants = fetch_support_grants(
            limit=limit,
            keyword=keyword,
            area_code=area_code if area_code != "00" else "",
            status=status,
            start_date=start_date,
            end_date=end_date,
            page=page,
        )
        if grants:
            return filter_grants(personalize_grants(grants, user), keyword=keyword, region=region, age=age)
    return filter_grants(personalize_grants(FALLBACK_GRANTS, user), keyword=keyword, region=region, age=age)


def personalize_grants(grants: list[dict], user: dict | None = None) -> list[dict]:
    if not user:
        return grants

    region = str(user.get("region") or "").strip()
    crop = str(user.get("crop") or "").strip()
    region_tokens = [token for token in region.replace("특별시", "").replace("광역시", "").replace("도", "").split() if token]
    crop_tokens = [crop] if crop else []

    personalized = []
    for index, grant in enumerate(grants):
        text = " ".join(str(grant.get(key, "")) for key in ("title", "source", "reason", "target", "content"))
        score = int(grant.get("fit", max(72, 96 - index * 5)))
        reasons = []

        if region and (region in text or any(token in text for token in region_tokens)):
            score += 10
            reasons.append(f"{region} 지역 조건 반영")
        if crop and any(token and token in text for token in crop_tokens):
            score += 6
            reasons.append(f"{crop} 작물 정보 반영")
        if not reasons:
            if region or crop:
                score += 2
                context = " · ".join(value for value in (region, crop) if value)
                reasons.append(f"{context} 조건으로 후보 비교")
            else:
                reasons.append("청년농 공통 지원 조건 우선")

        item = dict(grant)
        item["fit"] = min(score, 99)
        item["match_reason"] = " · ".join(reasons)
        item["reason"] = f"{item.get('reason', '지원 조건을 확인할 만한 사업입니다.')} ({item['match_reason']})"
        personalized.append(item)

    return sorted(personalized, key=lambda item: item.get("fit", 0), reverse=True)


def region_code(region: str = "") -> str:
    text = str(region or "").strip()
    if not text:
        return ""
    for name, code in REGION_CODES.items():
        if name and name in text:
            return code
    return ""


def normalize_region(region: str = "") -> str:
    text = str(region or "").strip()
    for name in REGION_OPTIONS:
        if name != "전국" and name in text:
            return name
    return text or "전국"


def filter_grants(grants: list[dict], *, keyword: str = "", region: str = "", age: int | None = None) -> list[dict]:
    keyword = str(keyword or "").strip()
    region = normalize_region(region)
    filtered = []
    for grant in grants:
        text = grant_search_text(grant)
        if keyword and keyword not in text:
            continue
        if region and region != "전국" and has_region_text(text) and region not in text and region_code(region) != region_code(text):
            continue
        if age is not None and not age_matches(text, age):
            continue
        filtered.append(grant)
    return filtered


def grant_search_text(grant: dict) -> str:
    return " ".join(str(grant.get(key, "")) for key in ("title", "source", "reason", "target", "content", "agency"))


def has_region_text(text: str) -> bool:
    return any(name != "전국" and name in text for name in REGION_CODES)


def age_matches(text: str, age: int) -> bool:
    if age <= 0:
        return True

    numbers = [int(value) for value in re.findall(r"(\d{2})\s*세", text)]
    if not numbers:
        return 19 <= age <= 49 if "청년" in text else True

    range_match = re.search(r"(\d{2})\s*세\s*(?:~|-|부터)\s*(\d{2})\s*세", text)
    if range_match:
        start, end = map(int, range_match.groups())
        return start <= age <= end

    min_values = [int(value) for value in re.findall(r"(\d{2})\s*세\s*이상", text)]
    max_values = [int(value) for value in re.findall(r"(\d{2})\s*세\s*(?:이하|미만)", text)]
    min_age = max(min_values) if min_values else 0
    max_age = min(max_values) if max_values else 150
    if "미만" in text and max_values:
        return min_age <= age < max_age
    return min_age <= age <= max_age


def get_crop_schedule(crop_name: str) -> dict:
    if not settings.use_demo_data:
        schedule = fetch_crop_schedule(crop_name)
        if schedule:
            return schedule
    return FALLBACK_SCHEDULES.get(
        crop_name,
        {
            "crop": crop_name,
            "source": "농사로 작물 재배 일정 API",
            "tasks": [{"period": "이번 주", "task": "선택한 작물의 생육 상태와 관수, 병해충 여부를 점검하세요."}],
        },
    )


def get_pest_guides(crop_name: str = "토마토") -> list[dict]:
    if not settings.use_demo_data:
        guides = fetch_pest_guides(crop_name)
        if guides:
            return guides
    return FALLBACK_PEST_GUIDES
