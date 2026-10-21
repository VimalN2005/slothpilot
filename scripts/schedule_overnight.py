"""Automated overnight scheduler daemon for SlothPilot.

Allows developers to set and forget: SlothPilot runs autonomously while you sleep.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.run_overnight import main as run_overnight_triage, safe_print


def run_daemon(target_hour: int = 3, target_minute: int = 0, interval_seconds: int = 60) -> None:
    """Runs a lightweight daemon that triggers overnight triage every day at target_hour:target_minute."""
    safe_print("=" * 60)
    safe_print(f"[SLOTH PILOT DAEMON] ACTIVE — Scheduled for {target_hour:02d}:{target_minute:02d} AM nightly.")
    safe_print("   Go to sleep like a sloth. SlothPilot will wake up at night to work.")
    safe_print("=" * 60)

    last_run_date = None

    while True:
        now = datetime.now()
        current_date = now.date()

        if now.hour == target_hour and now.minute == target_minute and last_run_date != current_date:
            safe_print(f"\n[DAEMON TRIGGER] Time reached {now.strftime('%H:%M:%S')}. Executing overnight triage...")
            try:
                run_overnight_triage()
                last_run_date = current_date
            except Exception as e:
                safe_print(f"[ERROR] Overnight triage error: {e}")

        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="SlothPilot Automated Overnight Scheduler Daemon")
    parser.add_argument("--hour", type=int, default=3, help="Hour to run overnight triage (0-23, default 3 AM)")
    parser.add_argument("--minute", type=int, default=0, help="Minute to run overnight triage (0-59, default 0)")
    parser.add_argument("--dry-run", action="store_true", help="Execute one triage immediately and exit")

    args = parser.parse_args()

    if args.dry_run:
        safe_print("[DAEMON] Performing dry-run execution...")
        run_overnight_triage()
        sys.exit(0)

    run_daemon(target_hour=args.hour, target_minute=args.minute)


if __name__ == "__main__":
    main()
