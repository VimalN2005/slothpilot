"""Unit tests for SlothPilot ingestion layer."""

from pathlib import Path
import pytest

from app.ingestion.chats_parser import parse_chat_file, scan_chats_directory
from app.ingestion.coordinator import run_overnight_ingestion
from app.ingestion.git_parser import scan_git_repository
from app.ingestion.notes_parser import scan_notes_directory
from app.ingestion.todos_parser import parse_todos_from_file, scan_todos_directory


BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DATA = BASE_DIR / "sample_data"


def test_git_repo_scanner():
    status = scan_git_repository(str(BASE_DIR))
    assert status is not None
    assert status.repo_name == "slothpilot"
    assert status.branch == "main"
    assert isinstance(status.is_dirty, bool)
    assert isinstance(status.recent_commits, list)


def test_notes_scanner():
    notes_dir = str(SAMPLE_DATA / "notes")
    notes = scan_notes_directory(notes_dir)
    assert len(notes) > 0
    note = notes[0]
    assert "Distributed Systems" in note.title or "Systems Notes" in note.title
    assert len(note.headings) > 0
    assert len(note.action_items) > 0


def test_chats_scanner():
    chats_dir = str(SAMPLE_DATA / "chats")
    digests = scan_chats_directory(chats_dir)
    assert len(digests) > 0
    digest = digests[0]
    assert digest.total_messages >= 4
    assert digest.urgent_messages_count > 0
    assert "Aman Verma" in digest.senders or "Priya Sharma" in digest.senders


def test_todos_scanner():
    todos_dir = str(SAMPLE_DATA / "todos")
    todos = scan_todos_directory(todos_dir)
    assert len(todos) >= 4
    high_priority = [t for t in todos if t.priority == "High"]
    completed = [t for t in todos if t.completed]
    assert len(high_priority) > 0
    assert len(completed) > 0


def test_coordinator_aggregation():
    report = run_overnight_ingestion(
        git_paths=[str(BASE_DIR)],
        notes_dir=str(SAMPLE_DATA / "notes"),
        chats_dir=str(SAMPLE_DATA / "chats"),
        todos_dir=str(SAMPLE_DATA / "todos"),
    )
    assert report is not None
    assert len(report.git_repos) == 1
    assert len(report.notes) >= 1
    assert len(report.chats) >= 1
    assert len(report.todos) >= 1
    assert report.scanned_at is not None
