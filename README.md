# 🦥 SlothPilot: The Autonomous Overnight Briefing & Multi-Agent Command Center

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Open-Source AI](https://img.shields.io/badge/AI-Open--Weight%20Models-purple)](https://ai.google.dev/gemma)

> **Channel your inner sloth. You sleep, SlothPilot works.**

Built for **[Hacktoberfest 2026 Week 3 DEV Challenge (Theme: "Slow and Steady: Build something with open-source AI that rewards laziness")](https://dev.to/challenges/hacktoberfest-week3-2026-10-19)**.

---

## 🎯 The Core Problem

Developers and engineers spend their first 60–90 minutes every morning performing tedious, stressful digital archaeology:
- Checking which Git branches were left dirty the night before.
- Digging through chaotic WhatsApp, Discord, or Slack exports to see what decisions teammates made overnight.
- Sifting through unorganized Markdown notes and fragmented todo lists.

**SlothPilot** runs entirely locally overnight while you sleep. It scans your local git repos, note vaults, and chat exports, feeds them through an autonomous multi-agent pipeline, and serves an executive **Morning Command Center** with prioritized action items, auto-drafted replies, and a 1-click **Human Approval Gate**.

---

## 🏗️ Architecture

```
Local Data Sources (Git Repos, Notes, Chats, Todos)
        │
        ▼
   Ingestion Layer (app/ingestion)
        │
        ▼
   Multi-Agent Pipeline (app/agents)
   ├── Context Aggregator Agent
   ├── Action Proposer Agent
   └── Safety & Approval Reviewer
        │
        ▼
   Morning Command Center (app/ui)
```
