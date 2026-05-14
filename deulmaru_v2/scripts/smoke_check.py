from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.settings import settings
from app.services.db import (
    add_interest,
    authenticate_user,
    create_user,
    init_db,
    list_interests,
)
from app.services.demo_data import get_crop_schedule, get_grants, get_pest_guides


def main() -> None:
    print({"backend": settings.database_backend, "demo": settings.use_demo_data})
    init_db()

    user_id = "codex_check_0514"
    user = {
        "id": user_id,
        "password": "password123",
        "name": "검증농",
        "region": "전남 나주",
        "crop": "토마토",
    }
    try:
        created = create_user(user)
        print("created", created["id"])
    except ValueError:
        print("created", "exists")

    login = authenticate_user(user_id, "password123")
    print("login", bool(login))

    grants = get_grants()
    print("grants", len(grants), grants[0]["source"] if grants else "none")
    add_interest(user_id, grants[0])
    print("interests", len(list_interests(user_id)))

    schedule = get_crop_schedule("토마토")
    print("schedule", schedule["source"], len(schedule["tasks"]))

    pests = get_pest_guides("토마토")
    print("pests", len(pests), pests[0]["source"] if pests else "none")


if __name__ == "__main__":
    main()
