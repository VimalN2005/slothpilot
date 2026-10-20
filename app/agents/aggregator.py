"""Context Aggregator Agent: Synthesizes multi-source raw ingestion data overnight."""

from __future__ import annotations

from typing import Any, Dict
from app.core.telemetry import get_tracer
from app.ingestion.models import IngestionReport


def aggregate_overnight_context(report: IngestionReport) -> Dict[str, Any]:
    """Analyzes raw report and identifies dirty repositories, urgent chats, and high-priority tasks."""
    tracer = get_tracer()
    with tracer.start_as_current_span("agent.context_aggregator") as span:
        span.set_attribute("agent.name", "ContextAggregator")
        span.set_attribute("sloth.input_git_count", len(report.git_repos))
        span.set_attribute("sloth.input_notes_count", len(report.notes))
        span.set_attribute("sloth.input_chats_count", len(report.chats))

        dirty_repos = [r for r in report.git_repos if r.is_dirty]
        urgent_chats = []
        for chat in report.chats:
            for msg in chat.highlights:
                if msg.is_urgent:
                    urgent_chats.append({"sender": msg.sender, "text": msg.text, "source": chat.source_file})

        high_priority_todos = [t for t in report.todos if t.priority == "High" and not t.completed]

        span.set_attribute("sloth.dirty_repos_detected", len(dirty_repos))
        span.set_attribute("sloth.urgent_chats_detected", len(urgent_chats))

        return {
            "dirty_repos": dirty_repos,
            "urgent_chats": urgent_chats,
            "high_priority_todos": high_priority_todos,
            "total_notes": len(report.notes),
            "total_todos": len(report.todos),
        }
