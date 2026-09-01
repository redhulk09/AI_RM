"""Small SQLite persistence layer."""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.getenv("RISK_MANAGER_DB", "risk_manager.db")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True) if Path(DB_PATH).parent != Path(".") else None
    with connect() as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                owner TEXT NOT NULL,
                likelihood INTEGER NOT NULL,
                impact INTEGER NOT NULL,
                control_effectiveness INTEGER NOT NULL,
                base_score INTEGER NOT NULL,
                adjusted_score INTEGER NOT NULL,
                severity TEXT NOT NULL,
                priority TEXT NOT NULL,
                recommendation TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )"""
        )


def create_risk(data: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    fields = dict(data)
    fields.update(created_at=now, updated_at=now)
    columns = ", ".join(fields)
    placeholders = ", ".join("?" for _ in fields)
    with connect() as db:
        cursor = db.execute(
            f"INSERT INTO risks ({columns}) VALUES ({placeholders})",
            tuple(fields.values()),
        )
        row = db.execute("SELECT * FROM risks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


def list_risks() -> list[dict]:
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM risks ORDER BY adjusted_score DESC, id DESC")]


def get_risk(risk_id: int) -> dict | None:
    with connect() as db:
        row = db.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()
    return dict(row) if row else None


def delete_risk(risk_id: int) -> bool:
    with connect() as db:
        result = db.execute("DELETE FROM risks WHERE id = ?", (risk_id,))
    return result.rowcount > 0


def update_recommendation(risk_id: int, recommendation: str) -> dict | None:
    now = datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute("UPDATE risks SET recommendation = ?, updated_at = ? WHERE id = ?", (recommendation, now, risk_id))
        row = db.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()
    return dict(row) if row else None
