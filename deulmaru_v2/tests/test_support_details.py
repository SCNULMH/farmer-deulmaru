from datetime import date, timedelta
from unittest import TestCase

from app.services.public_data import normalize_support_detail, support_status


class SupportDetailTest(TestCase):
    def test_normalize_support_detail_keeps_original_detail_fields(self):
        detail = normalize_support_detail(
            {
                "seq": "123",
                "title": "청년농 지원 공고",
                "applStDt": "2026-06-01",
                "applEdDt": "2026-06-30",
                "chargeAgency": "농업기관",
                "chargeDept": "청년농지원팀",
                "area2Nm": "전라남도 나주시",
                "eduTarget": "청년농업인",
                "contents": "지원 내용",
                "infoUrl": "https://example.com/notice",
            }
        )

        self.assertEqual(detail["id"], "123")
        self.assertEqual(detail["region"], "전라남도 나주시")
        self.assertEqual(detail["department"], "청년농지원팀")
        self.assertEqual(detail["url"], "https://example.com/notice")
        self.assertEqual(detail["period"], "2026-06-01 ~ 2026-06-30")

    def test_support_status_distinguishes_open_and_closed_notices(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        self.assertEqual(support_status(tomorrow), "접수중")
        self.assertEqual(support_status(yesterday), "마감")
        self.assertEqual(support_status("상시/공고 확인"), "공고 확인")
