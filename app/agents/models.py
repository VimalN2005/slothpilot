"""Data models for SlothPilot multi-agent pipeline and morning briefing."""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


ActionCategory = Literal["CHAT_REPLY", "GIT_COMMIT", "TODO_RESOLVE", "SYSTEM_CLEANUP"]
ApprovalStatus = Literal["PENDING", "APPROVED", "REJECTED", "EXECUTED"]
SafetyRating = Literal["LOW_RISK", "REQUIRES_HUMAN_APPROVAL", "HIGH_RISK_EXTERNAL"]


class ProposedAction(BaseModel):
    """An actionable decision or draft proposed by the overnight agent pipeline."""
    action_id: str
    title: str
    category: ActionCategory
    priority: Literal["HIGH", "NORMAL", "LOW"] = "NORMAL"
    reasoning: str
    suggested_draft: Optional[str] = None
    target_destination: str = ""  # e.g., "WhatsApp: Client Dave", "Git: feat/auth"
    safety_rating: SafetyRating = "REQUIRES_HUMAN_APPROVAL"
    approval_status: ApprovalStatus = "PENDING"


class MorningBriefing(BaseModel):
    """Executive morning digest delivered to the user upon waking up."""
    briefing_id: str = Field(default_factory=lambda: datetime.now().strftime("briefing_%Y%m%d_%H%M%S"))
    generated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    greeting: str = "Good Morning! While you were sleeping peacefully, SlothPilot triaged your local workspace."
    executive_summary: str
    sloth_efficiency_score: int = 94  # 0 to 100%
    estimated_minutes_saved: int = 85
    dirty_repos_detected: int = 0
    urgent_chats_detected: int = 0
    high_priority_todos: int = 0
    top_3_priorities: List[str] = Field(default_factory=list)
    actions: List[ProposedAction] = Field(default_factory=list)
