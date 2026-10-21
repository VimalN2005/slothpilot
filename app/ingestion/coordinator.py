"""Master coordinator running all ingestion parsers across local data sources."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from app.ingestion.calendar_parser import scan_calendar_directory
from app.ingestion.chats_parser import scan_chats_directory
from app.ingestion.git_parser import scan_git_directories
from app.ingestion.models import IngestionReport
from app.ingestion.notes_parser import scan_notes_directory
from app.ingestion.todos_parser import scan_todos_directory


def run_overnight_ingestion(
    git_paths: Optional[List[str]] = None,
    notes_dir: Optional[str] = None,
    chats_dir: Optional[str] = None,
    todos_dir: Optional[str] = None,
    calendar_dir: Optional[str] = None,
) -> IngestionReport:
    """Runs overnight collection across all configured local data sources."""
    git_statuses = []
    if git_paths:
        git_statuses = scan_git_directories(git_paths)

    notes = []
    if notes_dir and Path(notes_dir).exists():
        notes = scan_notes_directory(notes_dir)

    chats = []
    if chats_dir and Path(chats_dir).exists():
        chats = scan_chats_directory(chats_dir)

    todos = []
    if todos_dir and Path(todos_dir).exists():
        todos = scan_todos_directory(todos_dir)

    calendar_events = []
    first_meeting = None
    sleep_buffer = 120
    if calendar_dir and Path(calendar_dir).exists():
        calendar_events, first_meeting, sleep_buffer = scan_calendar_directory(calendar_dir)

    return IngestionReport(
        git_repos=git_statuses,
        notes=notes,
        chats=chats,
        todos=todos,
        calendar_events=calendar_events,
        sleep_buffer_minutes=sleep_buffer,
        first_meeting_time=first_meeting,
    )
