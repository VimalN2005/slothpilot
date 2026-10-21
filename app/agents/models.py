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
    first_meeting: Optional[str] = None
    sleep_buffer_minutes: int = 0
    top_3_priorities: List[str] = Field(default_factory=list)
    actions: List[ProposedAction] = Field(default_factory=list)

    def generate_standup_report(self) -> str:
        """Generates a ready-to-paste Slack/Discord morning standup digest."""
        yesterday_items = [
            "- Triaged uncommitted git changes and overnight chat backlogs",
            "- Automated test suite verification across workspace",
        ]
        today_items = [f"- {p}" for p in self.top_3_priorities]
        if self.first_meeting:
            today_items.append(f"- Attend: {self.first_meeting}")

        blocker_items = []
        if self.urgent_chats_detected > 0:
            blocker_items.append(f"- Needs approval: {self.urgent_chats_detected} pre-drafted client/team communications")
        if self.dirty_repos_detected > 0:
            blocker_items.append(f"- Pending git checkpoint review on local working tree")
        if not blocker_items:
            blocker_items.append("- None (all overnight blockers auto-triaged by SlothPilot)")

        return (
            "🦥 **Morning Standup Update (via SlothPilot):**\n\n"
            "**🚀 Yesterday / Overnight:**\n"
            + "\n".join(yesterday_items)
            + "\n\n**🎯 Today's Focus:**\n"
            + "\n".join(today_items)
            + "\n\n**🛡️ Blockers:**\n"
            + "\n".join(blocker_items)
        )

    def generate_audio_speech_text(self) -> str:
        """Returns clean text suited for browser Web Speech synthesis."""
        meeting_text = (
            f"Your first meeting is {self.first_meeting}. You have {self.sleep_buffer_minutes} minutes of extra sleep buffer."
            if self.first_meeting
            else "You have no morning meetings today."
        )
        return (
            f"Good morning! Your Sloth Efficiency Score is {self.sloth_efficiency_score} percent. "
            f"Overnight, SlothPilot saved you approximately {self.estimated_minutes_saved} minutes. "
            f"{meeting_text} "
            f"All {len(self.actions)} proposed actions have been staged in your approval gate. Drink your coffee and take it easy."
        )
