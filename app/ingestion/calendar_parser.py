"""Zero-dependency local calendar parser (.ics / json) and Sleep Buffer calculator."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from app.ingestion.models import CalendarEvent


def parse_ics_datetime(dt_str: str) -> str:
    """Parses raw ICS date string like 20261021T103000Z or 20261021T103000 into readable format."""
    clean = re.sub(r"[^0-9T]", "", dt_str)
    try:
        if "T" in clean:
            dt = datetime.strptime(clean[:15], "%Y%m%dT%H%M%S")
            return dt.strftime("%I:%M %p")
        dt = datetime.strptime(clean[:8], "%Y%m%d")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return dt_str.strip()


def parse_ics_file(filepath: Path | str) -> List[CalendarEvent]:
    """Parses an iCalendar (.ics) file into structured CalendarEvent models."""
    path = Path(filepath)
    if not path.is_file():
        return []

    events: List[CalendarEvent] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    vevents = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", content, re.DOTALL)
    for block in vevents:
        summary_m = re.search(r"SUMMARY:(.*)", block)
        dtstart_m = re.search(r"DTSTART(?:;[^:]+)?:(.*)", block)
        dtend_m = re.search(r"DTEND(?:;[^:]+)?:(.*)", block)
        desc_m = re.search(r"DESCRIPTION:(.*)", block)

        summary = summary_m.group(1).strip() if summary_m else "Meeting"
        start_time = parse_ics_datetime(dtstart_m.group(1)) if dtstart_m else "09:00 AM"
        end_time = parse_ics_datetime(dtend_m.group(1)) if dtend_m else "10:00 AM"
        desc = desc_m.group(1).strip() if desc_m else ""

        is_urgent = any(k in summary.upper() for k in ["DEMO", "CLIENT", "URGENT", "REVIEW", "INTERVIEW", "STANDUP"])

        events.append(CalendarEvent(
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            is_urgent=is_urgent,
            description=desc,
        ))

    return events


def calculate_sleep_buffer(events: List[CalendarEvent], default_wakeup_hour: int = 8) -> Tuple[Optional[str], int]:
    """Calculates first meeting time and how many minutes of extra sleep buffer the developer gets.
    
    A sloth developer baseline waking time is 8:00 AM.
    If the first meeting is at 10:30 AM (prep time 30 mins -> wake up 10:00 AM),
    the developer gets +120 minutes of extra sleep buffer!
    """
    if not events:
        # No morning meetings: unlimited sloth sleep!
        return None, 180

    first = events[0]
    time_str = first.start_time

    try:
        # Parse time string like "10:30 AM" or "02:00 PM"
        parsed_time = datetime.strptime(time_str.strip(), "%I:%M %p").time()
        meeting_minutes = parsed_time.hour * 60 + parsed_time.minute
        baseline_minutes = default_wakeup_hour * 60  # e.g., 08:00 -> 480 mins

        # Require 30 mins prep before meeting
        safe_wake_minutes = max(baseline_minutes, meeting_minutes - 30)
        buffer_minutes = max(0, safe_wake_minutes - baseline_minutes)

        return f"{first.summary} ({first.start_time})", buffer_minutes
    except Exception:
        return f"{first.summary} ({first.start_time})", 60


def scan_calendar_directory(calendar_dir: Path | str) -> Tuple[List[CalendarEvent], Optional[str], int]:
    """Scans directory for .ics files and computes schedule & sleep buffer."""
    c_dir = Path(calendar_dir)
    if not c_dir.is_dir():
        return [], None, 120

    all_events: List[CalendarEvent] = []
    for f in c_dir.glob("*.ics"):
        all_events.extend(parse_ics_file(f))

    first_meeting, sleep_buffer = calculate_sleep_buffer(all_events)
    return all_events, first_meeting, sleep_buffer
