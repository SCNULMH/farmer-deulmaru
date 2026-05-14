from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from html import unescape

import httpx

from app.core.settings import settings

REQUEST_TIMEOUT = 8.0

CROP_CONTENTS = {
    "토마토": "30646",
    "고추": "30600",
    "상추": "30640",
    "딸기": "30669",
    "감자": "30624",
    "배추": "30618",
    "오이": "30636",
}


def fetch_support_grants(limit: int = 6) -> list[dict]:
    if not settings.support_api_service_key:
        return []

    url = f"{settings.support_api_base_url}/policyListV2"
    params = {
        "typeDv": "json",
        "serviceKey": settings.support_api_service_key,
    }
    try:
        response = httpx.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return []

    rows = find_list(payload)
    grants = []
    for idx, row in enumerate(rows[:limit]):
        title = pick(row, "title", "policyNm", "bizNm", "plcyNm", "servNm", "name", default=f"지원사업 {idx + 1}")
        seq = str(pick(row, "seq", "id", "policyId", "plcyNo", default=f"support-{idx + 1}"))
        deadline = pick(row, "applEdDt", "aplyEndDt", "endDt", "reqstEndDe", default="상시/공고 확인")
        grants.append(
            {
                "id": seq,
                "title": clean(title),
                "source": "청년농 지원사업 API",
                "deadline": clean(deadline),
                "fit": max(72, 96 - idx * 5),
                "reason": "사용자 지역과 작물 정보를 기준으로 확인할 만한 지원사업입니다.",
            }
        )
    return grants


def fetch_crop_schedule(crop_name: str) -> dict | None:
    api_key = settings.nongsaro_api_key
    contents_no = CROP_CONTENTS.get(crop_name)
    if not api_key or not contents_no:
        return None

    url = "http://api.nongsaro.go.kr/service/farmWorkingPlanNew/workScheduleEraInfoLst"
    try:
        response = httpx.get(
            url,
            params={"apiKey": api_key, "cntntsNo": contents_no},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
    except Exception:
        return None

    html_node = root.find(".//htmlCn")
    html_text = html_node.text if html_node is not None else ""
    tasks = split_tasks(clean_html(html_text))
    if not tasks:
        return None
    return {
        "crop": crop_name,
        "source": "농사로 작물 재배 일정 API",
        "tasks": tasks[:5],
    }


def fetch_pest_guides(query: str = "토마토", limit: int = 3) -> list[dict]:
    if not settings.ncpms_api_key:
        return []

    try:
        search_response = httpx.get(
            settings.ncpms_api_base_url,
            params={
                "apiKey": settings.ncpms_api_key,
                "serviceCode": "SVC01",
                "serviceType": "AA001",
                "displayCount": str(limit),
                "startPoint": "1",
                "cropName": query,
            },
            timeout=REQUEST_TIMEOUT,
        )
        search_response.raise_for_status()
        root = ET.fromstring(search_response.text)
    except Exception:
        return []

    guides = []
    for item in root.findall(".//item")[:limit]:
        crop = node_text(item, "cropName") or query
        name = node_text(item, "sickNameKor") or node_text(item, "sickNameEng") or "병해충 정보"
        sick_key = node_text(item, "sickKey")
        detail = fetch_pest_detail(sick_key) if sick_key else {}
        guides.append(
            {
                "crop": clean(crop),
                "name": clean(name),
                "source": "NCPMS 병해충 API",
                "symptom": detail.get("symptom") or "NCPMS 상세 증상 정보를 확인해 현장 증상과 비교하세요.",
                "action": detail.get("action") or "등록 약제와 방제 기준을 확인한 뒤 조치하세요.",
            }
        )
    return guides


def fetch_pest_detail(sick_key: str) -> dict:
    try:
        response = httpx.get(
            settings.ncpms_api_base_url,
            params={
                "apiKey": settings.ncpms_api_key,
                "serviceCode": "SVC05",
                "serviceType": "AA001",
                "sickKey": sick_key,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)
    except Exception:
        return {}

    symptom = first_text(root, "symptoms", "symptom", "sickSymptom")
    prevention = first_text(root, "preventionMethod", "preventMethod", "controlMethod")
    return {
        "symptom": clean_html(symptom) if symptom else "",
        "action": clean_html(prevention) if prevention else "",
    }


def find_list(value) -> list:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ("data", "items", "item", "list", "result", "body"):
            found = find_list(value.get(key))
            if found:
                return found
        for child in value.values():
            found = find_list(child)
            if found:
                return found
    return []


def pick(row: dict, *keys: str, default: str = ""):
    lower = {str(key).lower(): value for key, value in row.items()}
    for key in keys:
        if key in row and row[key]:
            return row[key]
        value = lower.get(key.lower())
        if value:
            return value
    return default


def node_text(item: ET.Element, tag: str) -> str:
    node = item.find(tag)
    return node.text.strip() if node is not None and node.text else ""


def first_text(root: ET.Element, *tags: str) -> str:
    for tag in tags:
        node = root.find(f".//{tag}")
        if node is not None and node.text:
            return node.text
    return ""


def clean(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def clean_html(value: str | None) -> str:
    text = unescape(value or "")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return clean(text)


def split_tasks(text: str) -> list[dict]:
    chunks = [chunk.strip(" -\t") for chunk in re.split(r"[\n\r]+|(?<=다\.)", text) if chunk.strip()]
    tasks = []
    for idx, chunk in enumerate(chunks[:8]):
        if len(chunk) < 8:
            continue
        tasks.append({"period": f"{idx + 1}번째 작업", "task": chunk[:120]})
    return tasks
