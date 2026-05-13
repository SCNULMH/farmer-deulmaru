from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.settings import settings

DB_PATH = Path("data/deulmaru.sqlite3")


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def use_firebase() -> bool:
    return settings.database_backend.lower() == "firebase"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_firestore_client():
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError as exc:
        raise RuntimeError(
            "firebase-admin is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    if not firebase_admin._apps:
        if settings.firebase_credentials_json:
            info = json.loads(settings.firebase_credentials_json)
            cred = credentials.Certificate(info)
            firebase_admin.initialize_app(cred)
        elif settings.google_application_credentials:
            cred = credentials.Certificate(settings.google_application_credentials)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()

    return firestore.client()


def demo_user() -> dict[str, str]:
    return {
        "id": "demo",
        "password_hash": hash_password("demo1234"),
        "name": "예비 청년농 김하루",
        "region": "전남 나주",
        "crop": "토마토",
        "created_at": now(),
    }


def init_db() -> None:
    if use_firebase():
        init_firebase()
    else:
        init_sqlite()


def init_sqlite() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                region TEXT NOT NULL,
                crop TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS interests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                grant_id TEXT NOT NULL,
                title TEXT NOT NULL,
                deadline TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, grant_id)
            );

            CREATE TABLE IF NOT EXISTS diagnosis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                crop TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence INTEGER NOT NULL,
                filename TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        user = demo_user()
        conn.execute(
            """
            INSERT OR IGNORE INTO users
                (id, password_hash, name, region, crop, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                user["password_hash"],
                user["name"],
                user["region"],
                user["crop"],
                user["created_at"],
            ),
        )


def init_firebase() -> None:
    client = get_firestore_client()
    user = demo_user()
    ref = client.collection("users").document(user["id"])
    ref.set(user, merge=True)


def authenticate_user(user_id: str, password: str) -> dict | None:
    return authenticate_user_firebase(user_id, password) if use_firebase() else authenticate_user_sqlite(user_id, password)


def authenticate_user_sqlite(user_id: str, password: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row or row["password_hash"] != hash_password(password):
        return None
    return row_to_user(row)


def authenticate_user_firebase(user_id: str, password: str) -> dict | None:
    doc = get_firestore_client().collection("users").document(user_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    if data.get("password_hash") != hash_password(password):
        return None
    return row_to_user(data)


def row_to_user(row: Any) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "region": row["region"],
        "crop": row["crop"],
    }


def list_interests(user_id: str) -> list[dict]:
    return list_interests_firebase(user_id) if use_firebase() else list_interests_sqlite(user_id)


def list_interests_sqlite(user_id: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM interests WHERE user_id = ? ORDER BY deadline ASC",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_interests_firebase(user_id: str) -> list[dict]:
    docs = (
        get_firestore_client()
        .collection("users")
        .document(user_id)
        .collection("interests")
        .stream()
    )
    return sorted([doc.to_dict() for doc in docs], key=lambda item: item.get("deadline", ""))


def add_interest(user_id: str, grant: dict) -> None:
    if use_firebase():
        add_interest_firebase(user_id, grant)
    else:
        add_interest_sqlite(user_id, grant)


def add_interest_sqlite(user_id: str, grant: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO interests
                (user_id, grant_id, title, deadline, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, grant["id"], grant["title"], grant["deadline"], now()),
        )


def add_interest_firebase(user_id: str, grant: dict) -> None:
    get_firestore_client().collection("users").document(user_id).collection("interests").document(
        grant["id"]
    ).set(
        {
            "user_id": user_id,
            "grant_id": grant["id"],
            "title": grant["title"],
            "deadline": grant["deadline"],
            "created_at": now(),
        }
    )


def remove_interest(user_id: str, grant_id: str) -> None:
    if use_firebase():
        get_firestore_client().collection("users").document(user_id).collection("interests").document(
            grant_id
        ).delete()
    else:
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM interests WHERE user_id = ? AND grant_id = ?",
                (user_id, grant_id),
            )


def list_diagnosis_history(user_id: str) -> list[dict]:
    return list_diagnosis_history_firebase(user_id) if use_firebase() else list_diagnosis_history_sqlite(user_id)


def list_diagnosis_history_sqlite(user_id: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT crop, disease, confidence, filename, created_at
            FROM diagnosis_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 10
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_diagnosis_history_firebase(user_id: str) -> list[dict]:
    docs = (
        get_firestore_client()
        .collection("users")
        .document(user_id)
        .collection("diagnosis_history")
        .order_by("created_at", direction="DESCENDING")
        .limit(10)
        .stream()
    )
    return [doc.to_dict() for doc in docs]


def save_diagnosis(user_id: str, result: dict) -> None:
    if use_firebase():
        save_diagnosis_firebase(user_id, result)
    else:
        save_diagnosis_sqlite(user_id, result)


def diagnosis_payload(user_id: str, result: dict) -> dict:
    return {
        "user_id": user_id,
        "crop": result["crop"],
        "disease": result["disease"],
        "confidence": int(result["confidence"]),
        "filename": result.get("filename"),
        "created_at": now(),
    }


def save_diagnosis_sqlite(user_id: str, result: dict) -> None:
    payload = diagnosis_payload(user_id, result)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO diagnosis_history
                (user_id, crop, disease, confidence, filename, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload["user_id"],
                payload["crop"],
                payload["disease"],
                payload["confidence"],
                payload["filename"],
                payload["created_at"],
            ),
        )


def save_diagnosis_firebase(user_id: str, result: dict) -> None:
    get_firestore_client().collection("users").document(user_id).collection(
        "diagnosis_history"
    ).add(diagnosis_payload(user_id, result))
