"""Data models for SlothPilot ingestion layer."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class GitRepoStatus(BaseModel):
    """Snapshot of a local git repository."""
    repo_name: str
    path: str
    branch: str = "main"
    is_dirty: bool = False
    untracked_files_count: int = 0
    modified_files_count: int = 0
    modified_files: List[str] = Field(default_factory=list)
    recent_commits: List[str] = Field(default_factory=list)


class NoteItem(BaseModel):
    """Snapshot of a local markdown or text note."""
    title: str
    filepath: str
    modified_at: str
    headings: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    snippet: str = ""


class ChatMessage(BaseModel):
    """Individual parsed message from chat export."""
    sender: str
    text: str
    timestamp: Optional[str] = None
    is_urgent: bool = False


class ChatDigest(BaseModel):
    """Digest of a WhatsApp/Discord/Telegram chat export."""
    platform: str = "WhatsApp"
    source_file: str
    total_messages: int = 0
    urgent_messages_count: int = 0
    senders: List[str] = Field(default_factory=list)
    highlights: List[ChatMessage] = Field(default_factory=list)


class TodoItem(BaseModel):
    """Individual todo item parsed from local notes or todo files."""
    task: str
    completed: bool = False
    priority: str = "Normal"  # High, Normal, Low
    source_file: str = ""


class IngestionReport(BaseModel):
    """Aggregated local system snapshot created overnight."""
    scanned_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    git_repos: List[GitRepoStatus] = Field(default_factory=list)
    notes: List[NoteItem] = Field(default_factory=list)
    chats: List[ChatDigest] = Field(default_factory=list)
    todos: List[TodoItem] = Field(default_factory=list)
