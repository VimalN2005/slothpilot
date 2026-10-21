"""One-command overnight autonomous runner for SlothPilot."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.agents.pipeline import run_slothpilot_pipeline
from app.ingestion.coordinator import run_overnight_ingestion
from app.storage.db import save_briefing


def safe_print(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


def main() -> None:
    safe_print("=" * 60)
    safe_print("[SLOTH PILOT] STARTING AUTONOMOUS OVERNIGHT RUN...")
    safe_print("   Go to sleep. SlothPilot is triaging your workspace.")
    safe_print("=" * 60)

    sample_data = BASE_DIR / "sample_data"

    safe_print("\n[1/3] Ingesting local data sources (Git, Notes, Chats, Todos, Calendar)...")
    report = run_overnight_ingestion(
        git_paths=[str(BASE_DIR)],
        notes_dir=str(sample_data / "notes"),
        chats_dir=str(sample_data / "chats"),
        todos_dir=str(sample_data / "todos"),
        calendar_dir=str(sample_data / "calendar"),
    )
    safe_print(f"      [OK] Scanned {len(report.git_repos)} Git repository")
    safe_print(f"      [OK] Scanned {len(report.notes)} Markdown notes")
    safe_print(f"      [OK] Scanned {len(report.chats)} Chat exports")
    safe_print(f"      [OK] Scanned {len(report.todos)} Backlog todos")
    safe_print(f"      [OK] Scanned {len(report.calendar_events)} Calendar events")
    if report.first_meeting_time:
        safe_print(f"      [OK] First Meeting: {report.first_meeting_time}")
        safe_print(f"      [OK] Sloth Sleep Buffer: +{report.sleep_buffer_minutes} mins extra sleep!")

    safe_print("\n[2/3] Running Multi-Agent Pipeline (Aggregator -> Proposer -> Reviewer)...")
    briefing = run_slothpilot_pipeline(report)
    safe_print(f"      [OK] Sloth Efficiency Score: {briefing.sloth_efficiency_score}%")
    safe_print(f"      [OK] Estimated Minutes Saved: {briefing.estimated_minutes_saved} mins")
    safe_print(f"      [OK] Proposed Actions Queued: {len(briefing.actions)} actions")

    safe_print("\n[3/3] Saving Morning Briefing to SQLite State Store...")
    save_briefing(briefing)
    safe_print(f"      [OK] Saved briefing: {briefing.briefing_id}")

    safe_print("\n" + "=" * 60)
    safe_print("[SUCCESS] OVERNIGHT RUN COMPLETE! WAKE UP & RUN YOUR MORNING DASHBOARD:")
    safe_print("   streamlit run app.py")
    safe_print("=" * 60)


if __name__ == "__main__":
    main()
