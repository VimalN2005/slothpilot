"""Unit tests for Calendar (.ics) parser and Sleep Buffer calculation."""

from pathlib import Path
from app.ingestion.calendar_parser import (
    calculate_sleep_buffer,
    parse_ics_file,
    scan_calendar_directory,
)
from app.ingestion.models import CalendarEvent


def test_parse_sample_ics():
    calendar_file = Path("sample_data/calendar/schedule.ics")
    events = parse_ics_file(calendar_file)
    assert len(events) == 2
    assert "Sprint Architecture" in events[0].summary
    assert events[0].start_time == "10:30 AM"
    assert events[0].is_urgent is True
    assert "Client Dave" in events[1].summary


def test_calculate_sleep_buffer_with_events():
    events = [
        CalendarEvent(summary="Morning Sync", start_time="10:30 AM", end_time="11:00 AM")
    ]
    first_meeting, buffer_mins = calculate_sleep_buffer(events, default_wakeup_hour=8)
    assert "Morning Sync" in first_meeting
    # 10:30 - 30m prep = 10:00. 10:00 - 8:00 = 120 minutes buffer.
    assert buffer_mins == 120


def test_calculate_sleep_buffer_no_events():
    first_meeting, buffer_mins = calculate_sleep_buffer([])
    assert first_meeting is None
    assert buffer_mins == 180  # Full sloth sleep mode


def test_scan_calendar_directory():
    calendar_dir = Path("sample_data/calendar")
    events, first_meeting, sleep_buffer = scan_calendar_directory(calendar_dir)
    assert len(events) >= 2
    assert first_meeting is not None
    assert sleep_buffer > 0
