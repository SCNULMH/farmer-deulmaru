from __future__ import annotations

from datetime import date

from app.core.settings import settings
from app.services.public_data import fetch_crop_schedule, fetch_pest_guides, fetch_support_grants

DEMO_USER = {
    "name": "예비 청년농 김하루",
    "region": "전남 나주",
    "crop": "토마토",
    "stage": "정식 후 생육 관리",
}

FALLBACK_GRANTS = [
    {
        "id": "grant-001",
        "title": "청년농업인 영농정착 지원사업",
        "source": "농림축산식품 공공데이터",
        "deadline": "2026-06-14",
        "fit": 96,
        "reason": "나이, 지역, 신규 영농 준비 조건이 모두 맞습니다.",
    },
    {
        "id": "grant-002",
        "title": "스마트팜 현장실습 교육 지원",
        "source": "농사로/농업교육 데이터",
        "deadline": "2026-06-30",
        "fit": 88,
        "reason": "토마토 시설 재배 계획과 교육 과정이 연결됩니다.",
    },
    {
        "id": "grant-003",
        "title": "귀농 창업 및 주택구입 지원",
        "source": "지자체 지원사업 데이터",
        "deadline": "2026-07-05",
        "fit": 81,
        "reason": "나주 지역 정착 준비 단계에서 검토할 만합니다.",
    },
]

FALLBACK_SCHEDULES = {
    "토마토": {
        "crop": "토마토",
        "source": "농사로 작물 재배 일정 API",
        "tasks": [
            {"period": "5월 중순", "task": "시설 온습도 점검과 환기 관리"},
            {"period": "5월 하순", "task": "잿빛곰팡이병 예찰과 병든 잎 제거"},
            {"period": "6월 초", "task": "착과 상태 확인과 양액 농도 조정"},
        ],
    },
    "고추": {
        "crop": "고추",
        "source": "농사로 작물 재배 일정 API",
        "tasks": [
            {"period": "5월 중순", "task": "정식 후 활착 상태 점검"},
            {"period": "5월 하순", "task": "총채벌레와 바이러스 매개충 예찰"},
            {"period": "6월 초", "task": "지주 설치와 웃거름 관리"},
        ],
    },
}

FALLBACK_PEST_GUIDES = [
    {
        "crop": "토마토",
        "name": "토마토 잎곰팡이병",
        "source": "NCPMS 병해충 데이터",
        "symptom": "잎 뒷면에 연한 갈색 곰팡이가 생기고 잎이 마릅니다.",
        "action": "환기를 늘리고 병든 잎을 제거한 뒤 등록 약제를 확인합니다.",
    },
    {
        "crop": "고추",
        "name": "고추 탄저병",
        "source": "NCPMS 병해충 데이터",
        "symptom": "열매에 둥근 병반이 생기고 습할 때 빠르게 번집니다.",
        "action": "강우 전후 예찰을 강화하고 감염 과실을 즉시 제거합니다.",
    },
    {
        "crop": "참외",
        "name": "참외 흰가루병",
        "source": "NCPMS 병해충 데이터",
        "symptom": "잎 표면에 흰 가루 형태의 균사가 퍼집니다.",
        "action": "밀식을 줄이고 초기 방제를 우선합니다.",
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
        "grants": get_grants(),
        "schedule": get_crop_schedule(crop),
        "pests": get_pest_guides(crop),
        "diagnosis_history": diagnosis_history or [],
        "data_sources": [
            "농림축산식품 공공데이터 포털",
            "농사로 작물 재배 일정",
            "NCPMS 병해충 정보",
            "지자체 청년농 지원사업 데이터",
        ],
    }


def get_grants() -> list[dict]:
    if not settings.use_demo_data:
        grants = fetch_support_grants()
        if grants:
            return grants
    return FALLBACK_GRANTS


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
            "tasks": [{"period": "이번 주", "task": "해당 작물의 공공데이터 연동을 준비 중입니다."}],
        },
    )


def get_pest_guides(crop_name: str = "토마토") -> list[dict]:
    if not settings.use_demo_data:
        guides = fetch_pest_guides(crop_name)
        if guides:
            return guides
    return FALLBACK_PEST_GUIDES
