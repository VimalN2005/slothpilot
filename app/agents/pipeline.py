"""Autonomous overnight multi-agent pipeline coordinator for SlothPilot."""

from __future__ import annotations

import time
from app.agents.aggregator import aggregate_overnight_context
from app.agents.action_proposer import propose_overnight_actions
from app.agents.models import MorningBriefing
from app.agents.reviewer import review_and_synthesize
from app.core.telemetry import get_tracer
from app.ingestion.models import IngestionReport


def run_slothpilot_pipeline(report: IngestionReport) -> MorningBriefing:
    """Executes the complete overnight multi-agent pipeline and delivers the Morning Briefing."""
    tracer = get_tracer()
    with tracer.start_as_current_span("slothpilot.overnight_pipeline") as span:
        span.set_attribute("gen_ai.system", "slothpilot_multi_agent")
        start_time = time.perf_counter()

        # Step 1: Context Aggregator Agent
        context = aggregate_overnight_context(report)

        # Step 2: Action Proposer Agent
        actions = propose_overnight_actions(context)

        # Step 3: Safety & Reviewer Agent
        summary, priorities, efficiency_score, minutes_saved = review_and_synthesize(context, actions)

        duration_ms = (time.perf_counter() - start_time) * 1000
        span.set_attribute("pipeline.latency_ms", round(duration_ms, 2))
        span.set_attribute("pipeline.actions_generated", len(actions))
        span.set_attribute("pipeline.token_cost_usd", 0.0)

        return MorningBriefing(
            executive_summary=summary,
            sloth_efficiency_score=efficiency_score,
            estimated_minutes_saved=minutes_saved,
            dirty_repos_detected=len(context.get("dirty_repos", [])),
            urgent_chats_detected=len(context.get("urgent_chats", [])),
            high_priority_todos=len(context.get("high_priority_todos", [])),
            first_meeting=report.first_meeting_time,
            sleep_buffer_minutes=report.sleep_buffer_minutes,
            top_3_priorities=priorities,
            actions=actions,
        )
