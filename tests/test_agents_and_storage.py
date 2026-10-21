"""Unit tests for SlothPilot multi-agent pipeline, OpenTelemetry tracing, and SQLite storage."""

from pathlib import Path
import pytest

from app.agents.models import MorningBriefing, ProposedAction
from app.agents.pipeline import run_slothpilot_pipeline
from app.core.telemetry import get_recorded_spans, init_telemetry
from app.ingestion.coordinator import run_overnight_ingestion
from app.storage.db import get_latest_briefing, init_db, save_briefing, update_action_status


BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DATA = BASE_DIR / "sample_data"


@pytest.fixture(autouse=True)
def setup_env():
    init_telemetry()
    init_db()


def test_multi_agent_pipeline():
    report = run_overnight_ingestion(
        git_paths=[str(BASE_DIR)],
        notes_dir=str(SAMPLE_DATA / "notes"),
        chats_dir=str(SAMPLE_DATA / "chats"),
        todos_dir=str(SAMPLE_DATA / "todos"),
    )

    briefing = run_slothpilot_pipeline(report)
    assert briefing is not None
    assert isinstance(briefing.executive_summary, str)
    assert len(briefing.executive_summary) > 20
    assert briefing.sloth_efficiency_score >= 80
    assert briefing.estimated_minutes_saved > 0
    assert len(briefing.top_3_priorities) > 0
    assert len(briefing.actions) > 0

    # Verify action structure and human approval gate
    for action in briefing.actions:
        assert action.action_id.startswith("act_")
        assert action.approval_status == "PENDING"
        if action.category in ["CHAT_REPLY", "GIT_COMMIT"]:
            assert action.safety_rating == "REQUIRES_HUMAN_APPROVAL"


def test_agent_opentelemetry_spans():
    initial_count = len(get_recorded_spans())
    report = run_overnight_ingestion(
        git_paths=[str(BASE_DIR)],
        notes_dir=str(SAMPLE_DATA / "notes"),
        chats_dir=str(SAMPLE_DATA / "chats"),
        todos_dir=str(SAMPLE_DATA / "todos"),
    )
    run_slothpilot_pipeline(report)
    spans = get_recorded_spans()
    assert len(spans) > initial_count

    span_names = [s["name"] for s in spans]
    assert "slothpilot.overnight_pipeline" in span_names
    assert "agent.context_aggregator" in span_names
    assert "agent.action_proposer" in span_names
    assert "agent.safety_reviewer" in span_names


def test_sqlite_storage_and_approval_gate():
    briefing = MorningBriefing(
        briefing_id="test_briefing_001",
        executive_summary="Test morning summary for unit test.",
        sloth_efficiency_score=95,
        estimated_minutes_saved=60,
        actions=[
            ProposedAction(
                action_id="act_test_01",
                title="Test Proposed Reply",
                category="CHAT_REPLY",
                reasoning="Testing approval gate",
                suggested_draft="Hello World",
                safety_rating="REQUIRES_HUMAN_APPROVAL",
                approval_status="PENDING",
            )
        ],
    )

    save_briefing(briefing)
    retrieved = get_latest_briefing()
    assert retrieved is not None
    assert retrieved.briefing_id == "test_briefing_001"

    # Test Human Approval Gate status transition
    updated = update_action_status(
        briefing_id="test_briefing_001", action_id="act_test_01", status="APPROVED"
    )
    assert updated is True


def test_standup_and_speech_generation():
    briefing = MorningBriefing(
        executive_summary="Everything triaged smoothly.",
        top_3_priorities=["Fix auth blocker", "Deploy to production"],
        first_meeting="Sprint Demo (10:30 AM)",
        sleep_buffer_minutes=120,
        urgent_chats_detected=1,
        dirty_repos_detected=0,
    )

    standup = briefing.generate_standup_report()
    assert "Morning Standup Update" in standup
    assert "Fix auth blocker" in standup
    assert "Sprint Demo (10:30 AM)" in standup
    assert "Needs approval: 1" in standup

    speech = briefing.generate_audio_speech_text()
    assert "Good morning!" in speech
    assert "Sprint Demo (10:30 AM)" in speech
    assert "120 minutes of extra sleep buffer" in speech

