"""Local Git repository scanner for SlothPilot using git CLI & subprocess."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import List, Optional

from app.ingestion.models import GitRepoStatus


def _run_git_cmd(repo_path: Path, args: List[str]) -> Optional[str]:
    """Runs a git command inside the repo directory safely."""
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None


def scan_git_repository(repo_path: str) -> Optional[GitRepoStatus]:
    """Inspects a local git repository and extracts branch, dirty state, and recent commits."""
    path = Path(repo_path).resolve()
    if not path.exists():
        return None

    # Check if directory contains .git or is inside a worktree
    rev_parse = _run_git_cmd(path, ["rev-parse", "--is-inside-work-tree"])
    if rev_parse != "true":
        return None

    repo_name = path.name

    # Current branch
    branch = _run_git_cmd(path, ["branch", "--show-current"])
    if not branch:
        # Check detached HEAD
        head_commit = _run_git_cmd(path, ["rev-parse", "--short", "HEAD"])
        branch = f"detached@{head_commit}" if head_commit else "main"

    # Status porcelain: modified, untracked, staged
    status_out = _run_git_cmd(path, ["status", "--porcelain"])
    modified_files = []
    untracked_count = 0
    is_dirty = False

    if status_out:
        lines = [line.strip() for line in status_out.splitlines() if line.strip()]
        if lines:
            is_dirty = True
            for line in lines:
                status_code = line[:2]
                file_name = line[3:].strip()
                if status_code.startswith("??"):
                    untracked_count += 1
                else:
                    modified_files.append(file_name)

    # Recent 3 commits
    log_out = _run_git_cmd(path, ["log", "-n", "3", "--oneline"])
    recent_commits = []
    if log_out:
        recent_commits = [c.strip() for c in log_out.splitlines() if c.strip()]
    else:
        recent_commits = ["Initial repository (no commits yet)"]

    return GitRepoStatus(
        repo_name=repo_name,
        path=str(path),
        branch=branch,
        is_dirty=is_dirty,
        untracked_files_count=untracked_count,
        modified_files_count=len(modified_files),
        modified_files=modified_files[:10],
        recent_commits=recent_commits,
    )


def scan_git_directories(root_paths: List[str]) -> List[GitRepoStatus]:
    """Scans multiple root directories for git repositories."""
    results: List[GitRepoStatus] = []
    for p in root_paths:
        status = scan_git_repository(p)
        if status:
            results.append(status)
    return results
