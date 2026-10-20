"""Action Proposer Agent: Drafts replies, git commits, and task proposals from overnight context."""

from __future__ import annotations

from typing import Any, Dict, List
from app.agents.models import ProposedAction
from app.core.llm import query_llm, safe_parse_json
from app.core.telemetry import get_tracer


def propose_overnight_actions(context: Dict[str, Any]) -> List[ProposedAction]:
    """Generates concrete proposed actions with pre-drafted responses."""
    tracer = get_tracer()
    with tracer.start_as_current_span("agent.action_proposer") as span:
        span.set_attribute("agent.name", "ActionProposer")

        actions: List[ProposedAction] = []
        action_counter = 1

        # 1. Actions from urgent chats (e.g. Client Dave, Priya)
        for chat in context.get("urgent_chats", []):
            sender = chat.get("sender", "Team")
            text = chat.get("text", "")

            if "dave" in sender.lower() or "contract" in text.lower() or "payment" in text.lower():
                actions.append(
                    ProposedAction(
                        action_id=f"act_{action_counter:03d}",
                        title=f"Send Pre-Drafted SOW Milestone Reply to {sender}",
                        category="CHAT_REPLY",
                        priority="HIGH",
                        reasoning=f"Client requested milestone finalization overnight for 50% advance deposit.",
                        suggested_draft=(
                            f"Hi {sender}, good morning! I've finalized our 3 engineering milestones in our SOW contract "
                            "and attached the commercial invoice with payment instructions. Looking forward to kick-off!"
                        ),
                        target_destination=f"WhatsApp: {sender}",
                        safety_rating="REQUIRES_HUMAN_APPROVAL",
                    )
                )
                action_counter += 1
            elif "bug" in text.lower() or "critical" in text.lower():
                actions.append(
                    ProposedAction(
                        action_id=f"act_{action_counter:03d}",
                        title=f"Acknowledge & Triage Blocker from {sender}",
                        category="CHAT_REPLY",
                        priority="HIGH",
                        reasoning=f"Reported critical bug in payment webhook retry queue.",
                        suggested_draft=(
                            f"Hey {sender}, saw your ping regarding the webhook retry queue. "
                            "I am reviewing the worker logic right now and will push a hotfix before the 10am demo."
                        ),
                        target_destination=f"Chat: {sender}",
                        safety_rating="REQUIRES_HUMAN_APPROVAL",
                    )
                )
                action_counter += 1

        # 2. Actions from dirty git repositories
        for repo in context.get("dirty_repos", []):
            mod_count = repo.modified_files_count
            untracked_count = repo.untracked_files_count
            actions.append(
                ProposedAction(
                    action_id=f"act_{action_counter:03d}",
                    title=f"Stage & Commit Unfinished Work in '{repo.repo_name}'",
                    category="GIT_COMMIT",
                    priority="NORMAL",
                    reasoning=f"Found {mod_count} modified files and {untracked_count} untracked files on branch '{repo.branch}'.",
                    suggested_draft=f"git add . && git commit -s -m 'wip: checkpoint overnight progress on {repo.branch}'",
                    target_destination=f"Git Repo: {repo.path}",
                    safety_rating="REQUIRES_HUMAN_APPROVAL",
                )
            )
            action_counter += 1

        # 3. Actions from high priority todos
        for todo in context.get("high_priority_todos", []):
            actions.append(
                ProposedAction(
                    action_id=f"act_{action_counter:03d}",
                    title=f"Resolve High Priority Task: {todo.task}",
                    category="TODO_RESOLVE",
                    priority="HIGH",
                    reasoning=f"Task flagged as High Priority from {todo.source_file}.",
                    suggested_draft=None,
                    target_destination=f"Backlog: {todo.source_file}",
                    safety_rating="LOW_RISK",
                )
            )
            action_counter += 1

        span.set_attribute("sloth.proposed_actions_count", len(actions))
        return actions
