"""Local chat export scanner (WhatsApp, Discord, Telegram) for SlothPilot."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from app.ingestion.models import ChatDigest, ChatMessage

URGENT_KEYWORDS = {
    "urgent", "asap", "deadline", "bug", "issue", "critical",
    "payment", "deploy", "review", "blocker", "help", "broken"
}

# Matches standard WhatsApp export formats:
# "10/19/26, 11:45 PM - Aman: Hey did you push the commit?"
# "[19/10/26, 23:45:10] Aman Verma: Can you review PR #4?"
WHATSAPP_PATTERN = re.compile(
    r"^(?:\[?(\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}[,\s]+\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\]?\s*[-:]?\s*)([^:]+?):\s*(.+)$"
)


def parse_chat_file(file_path: str) -> Optional[ChatDigest]:
    """Parses a WhatsApp, Discord, or text chat export."""
    path = Path(file_path).resolve()
    if not path.exists() or not path.is_file():
        return None

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    lines = content.splitlines()
    messages: List[ChatMessage] = []
    senders_set = set()

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        match = WHATSAPP_PATTERN.match(line_clean)
        if match:
            timestamp, sender, text = match.groups()
            sender = sender.strip()
            text = text.strip()
            senders_set.add(sender)

            is_urgent = any(kw in text.lower() for kw in URGENT_KEYWORDS)
            messages.append(
                ChatMessage(
                    sender=sender,
                    text=text,
                    timestamp=timestamp.strip(),
                    is_urgent=is_urgent,
                )
            )
        else:
            # Fallback for simple "Name: Message" or Discord format
            if ":" in line_clean and not line_clean.startswith("http"):
                parts = line_clean.split(":", 1)
                sender = parts[0].strip()
                text = parts[1].strip()
                if len(sender) < 30 and text:
                    senders_set.add(sender)
                    is_urgent = any(kw in text.lower() for kw in URGENT_KEYWORDS)
                    messages.append(
                        ChatMessage(
                            sender=sender,
                            text=text,
                            is_urgent=is_urgent,
                        )
                    )

    if not messages:
        return None

    urgent_messages = [m for m in messages if m.is_urgent]

    return ChatDigest(
        platform="WhatsApp / Chat Export",
        source_file=path.name,
        total_messages=len(messages),
        urgent_messages_count=len(urgent_messages),
        senders=list(senders_set)[:10],
        highlights=(urgent_messages + messages[-5:])[:8],
    )


def scan_chats_directory(chats_dir: str) -> List[ChatDigest]:
    """Scans a directory for chat export text files."""
    path = Path(chats_dir).resolve()
    if not path.exists() or not path.is_dir():
        return []

    digests: List[ChatDigest] = []
    for file in path.glob("*.txt"):
        digest = parse_chat_file(str(file))
        if digest:
            digests.append(digest)
    return digests
