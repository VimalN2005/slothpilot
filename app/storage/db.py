"""SQLite state store for SlothPilot morning briefings and approval lifecycle."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import List, Optional

from app.agents.models import MorningBriefing, ProposedAction


def get_db_path() -> Path:
    """Returns path to the local sqlite database."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    storage_dir = base_dir / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / "slothpilot.db"


def init_db() -> None:
    """Initializes the sqlite tables for briefings and actions."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS briefings (
            briefing_id TEXT PRIMARY KEY,
            generated_at TEXT,
            executive_summary TEXT,
            sloth_efficiency_score INTEGER,
            estimated_minutes_saved INTEGER,
            dirty_repos_detected INTEGER,
            urgent_chats_detected INTEGER,
            high_priority_todos INTEGER,
            top_3_priorities TEXT,
            raw_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            action_id TEXT,
            briefing_id TEXT,
            title TEXT,
            category TEXT,
            priority TEXT,
            reasoning TEXT,
            suggested_draft TEXT,
            target_destination TEXT,
            safety_rating TEXT,
            approval_status TEXT,
            PRIMARY KEY (action_id, briefing_id),
            FOREIGN KEY (briefing_id) REFERENCES briefings (briefing_id)
        )
    """)

    conn.commit()
    conn.close()


def save_briefing(briefing: MorningBriefing) -> None:
    """Saves or updates a complete morning briefing and its proposed actions."""
    init_db()
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO briefings (
            briefing_id, generated_at, executive_summary, sloth_efficiency_score,
            estimated_minutes_saved, dirty_repos_detected, urgent_chats_detected,
            high_priority_todos, top_3_priorities, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        briefing.briefing_id,
        briefing.generated_at,
        briefing.executive_summary,
        briefing.sloth_efficiency_score,
        briefing.estimated_minutes_saved,
        briefing.dirty_repos_detected,
        briefing.urgent_chats_detected,
        briefing.high_priority_todos,
        json.dumps(briefing.top_3_priorities),
        briefing.model_dump_json(),
    ))

    for act in briefing.actions:
        cursor.execute("""
            INSERT OR REPLACE INTO actions (
                action_id, briefing_id, title, category, priority, reasoning,
                suggested_draft, target_destination, safety_rating, approval_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            act.action_id,
            briefing.briefing_id,
            act.title,
            act.category,
            act.priority,
            act.reasoning,
            act.suggested_draft,
            act.target_destination,
            act.safety_rating,
            act.approval_status,
        ))

    conn.commit()
    conn.close()


def update_action_status(briefing_id: str, action_id: str, status: str) -> bool:
    """Updates the human approval status of a proposed action."""
    init_db()
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE actions SET approval_status = ? WHERE action_id = ? AND briefing_id = ?
    """, (status, action_id, briefing_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_latest_briefing() -> Optional[MorningBriefing]:
    """Retrieves the most recent morning briefing from storage."""
    init_db()
    conn = sqlite3.connect(str(get_db_path()))
    cursor = conn.cursor()
    cursor.execute("SELECT raw_json FROM briefings ORDER BY generated_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        try:
            return MorningBriefing.model_validate_json(row[0])
        except Exception:
            return None
    return None
