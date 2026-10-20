"""Local markdown and text notes scanner for SlothPilot."""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List

from app.ingestion.models import NoteItem


def scan_notes_directory(notes_dir: str, max_files: int = 15) -> List[NoteItem]:
    """Scans a local directory for markdown and text notes."""
    path = Path(notes_dir).resolve()
    if not path.exists() or not path.is_dir():
        return []

    items: List[NoteItem] = []
    supported_exts = {".md", ".markdown", ".txt"}

    for root, _, files in os.walk(str(path)):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in supported_exts:
                try:
                    stats = file_path.stat()
                    mtime_str = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")

                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    lines = content.splitlines()

                    # Extract title (first H1 or filename)
                    title = file_path.stem.replace("_", " ").title()
                    headings = []
                    action_items = []

                    for line in lines:
                        clean_line = line.strip()
                        if clean_line.startswith("#"):
                            h_text = clean_line.lstrip("#").strip()
                            headings.append(h_text)
                            if not title or title == file_path.stem.title():
                                if clean_line.startswith("# "):
                                    title = h_text
                        elif re.match(r"^\s*-\s*\[\s*\]\s+", line):
                            # Incomplete action checkbox
                            task = re.sub(r"^\s*-\s*\[\s*\]\s+", "", line).strip()
                            action_items.append(task)

                    snippet = " ".join(content.split()[:40]) + ("..." if len(content.split()) > 40 else "")

                    items.append(
                        NoteItem(
                            title=title,
                            filepath=str(file_path),
                            modified_at=mtime_str,
                            headings=headings[:5],
                            action_items=action_items[:5],
                            snippet=snippet,
                        )
                    )

                    if len(items) >= max_files:
                        return items
                except Exception:
                    continue

    return items
