"""Local todos and task lists scanner for SlothPilot."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List

from app.ingestion.models import TodoItem


def parse_todos_from_file(file_path: str) -> List[TodoItem]:
    """Parses markdown checkboxes into structured TodoItem instances."""
    path = Path(file_path).resolve()
    if not path.exists() or not path.is_file():
        return []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    todos: List[TodoItem] = []
    lines = content.splitlines()

    for line in lines:
        clean = line.strip()
        # Incomplete checkbox: "- [ ] task" or "* [ ] task"
        match_incomplete = re.match(r"^[-*]\s*\[\s*\]\s+(.+)$", clean)
        # Completed checkbox: "- [x] task" or "* [X] task"
        match_completed = re.match(r"^[-*]\s*\[[xX]\]\s+(.+)$", clean)

        if match_incomplete:
            task_text = match_incomplete.group(1).strip()
            completed = False
        elif match_completed:
            task_text = match_completed.group(1).strip()
            completed = True
        else:
            continue

        # Priority detection
        priority = "Normal"
        lower_task = task_text.lower()
        if any(p in lower_task for p in ["!high", "p1", "urgent", "critical", "asap"]):
            priority = "High"
        elif any(p in lower_task for p in ["!low", "p3", "someday", "optional"]):
            priority = "Low"

        # Clean tags from text
        clean_text = re.sub(r"(!high|!low|p1|p2|p3|urgent)\b", "", task_text, flags=re.IGNORECASE).strip()

        todos.append(
            TodoItem(
                task=clean_text or task_text,
                completed=completed,
                priority=priority,
                source_file=path.name,
            )
        )

    return todos


def scan_todos_directory(todos_dir: str) -> List[TodoItem]:
    """Scans a directory for todo files or markdown files with checkboxes."""
    path = Path(todos_dir).resolve()
    if not path.exists() or not path.is_dir():
        return []

    all_todos: List[TodoItem] = []
    for ext in ["*.md", "*.txt"]:
        for file in path.glob(ext):
            all_todos.extend(parse_todos_from_file(str(file)))
    return all_todos
