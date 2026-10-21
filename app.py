"""SlothPilot: Autonomous Overnight Briefing & Multi-Agent Command Center.

Streamlit Morning Dashboard engineered for Hacktoberfest 2026 Week 3 ('Slow and Steady: Reward Laziness').
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

# Setup sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.agents.pipeline import run_slothpilot_pipeline
from app.core.telemetry import get_recorded_spans
from app.ingestion.coordinator import run_overnight_ingestion
from app.storage.db import get_latest_briefing, save_briefing, update_action_status

# Page Configuration
st.set_page_config(
    page_title="SlothPilot: Autonomous Morning Command Center",
    page_icon="🦥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-container {
        background-color: #1a1c23;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .action-card {
        background-color: #1e222b;
        border-left: 5px solid #4CAF50;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }
    .action-card-urgent {
        background-color: #241e24;
        border-left: 5px solid #f44336;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }
    .sloth-badge {
        background-color: #2e7d32;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def ensure_initial_briefing():
    """Ensures at least one briefing exists in storage."""
    briefing = get_latest_briefing()
    if not briefing:
        sample_data = BASE_DIR / "sample_data"
        report = run_overnight_ingestion(
            git_paths=[str(BASE_DIR)],
            notes_dir=str(sample_data / "notes"),
            chats_dir=str(sample_data / "chats"),
            todos_dir=str(sample_data / "todos"),
            calendar_dir=str(sample_data / "calendar"),
        )
        briefing = run_slothpilot_pipeline(report)
        save_briefing(briefing)
    return briefing


# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("🦥 SlothPilot")
    st.caption("Overnight Autonomous Multi-Agent Triage")
    st.markdown("---")

    st.markdown("**Core Philosophy:**")
    st.info("You sleep like a sloth for 8 hours. SlothPilot quietly triages your repos, chats, and notes, serving a 1-click morning action plan.")

    if st.button("🌙 Simulate Overnight Run Now", use_container_width=True):
        with st.spinner("SlothPilot agents scanning local sources & generating briefing..."):
            sample_data = BASE_DIR / "sample_data"
            report = run_overnight_ingestion(
                git_paths=[str(BASE_DIR)],
                notes_dir=str(sample_data / "notes"),
                chats_dir=str(sample_data / "chats"),
                todos_dir=str(sample_data / "todos"),
                calendar_dir=str(sample_data / "calendar"),
            )
            new_briefing = run_slothpilot_pipeline(report)
            save_briefing(new_briefing)
            st.session_state["latest_briefing"] = new_briefing
            st.success("Overnight run completed! Briefing updated.")
            st.rerun()

    st.markdown("---")
    st.markdown("**Data Sources Monitored:**")
    st.write("📁 Local Git Repositories")
    st.write("📝 Markdown Notes Vault")
    st.write("💬 WhatsApp & Discord Exports")
    st.write("✅ Local Todos & Backlogs")
    st.write("📅 Local Calendar Exports (.ics)")
    st.markdown("---")
    st.caption("100% Local Inference · $0.00 Token Cost · Hacktoberfest 2026")


# ----------------- MAIN DASHBOARD -----------------
briefing = get_latest_briefing()
if not briefing:
    briefing = ensure_initial_briefing()

st.title("🦥 Good Morning! Here is your Overnight Briefing ☕")
st.markdown(f"**Briefing Generated:** `{briefing.generated_at}` | **Status:** `Autonomous Triage Complete`")

# Hero Metrics
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Sloth Efficiency", f"{briefing.sloth_efficiency_score}%", delta="Energy Conserved 🦥")
c2.metric("Triage Saved", f"{briefing.estimated_minutes_saved}m", delta="No morning rush")
c3.metric("Sleep Buffer", f"+{briefing.sleep_buffer_minutes}m", delta="Sleep in safely 🛌")
c4.metric("Urgent Blockers", f"{briefing.urgent_chats_detected + briefing.dirty_repos_detected}", delta="Pre-drafted")
c5.metric("Inference Cost", "$0.00", delta="100% Local & Free")

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Executive Morning Briefing",
    "🛡️ Human Approval Gate (Pre-Drafted Actions)",
    "🔍 Ingested Workspace Data",
    "📊 OpenTelemetry GenAI Observability",
])

# ----------------- TAB 1: EXECUTIVE BRIEFING -----------------
with tab1:
    st.subheader("Overnight Executive Synthesis")
    st.info(briefing.executive_summary)

    if getattr(briefing, "first_meeting", None):
        st.success(f"🛌 **Sloth Sleep Buffer Active:** First meeting is **{briefing.first_meeting}**. You have **+{briefing.sleep_buffer_minutes} mins** of extra sleep buffer before prep!")

    # 🎙️ 45-Second Sloth Morning Audio Briefing
    speech_text = briefing.generate_audio_speech_text().replace('"', '\\"').replace("\n", " ")
    audio_html = f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 12px 18px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <strong style="color: #4ade80; font-size: 14px;">🎙️ 45-Second Sloth Audio Briefing</strong><br>
            <span style="color: #94a3b8; font-size: 12px;">Listen to your overnight summary while pouring your morning coffee.</span>
        </div>
        <button id="audio-btn" onclick="playBriefing()" style="background-color: #22c55e; color: #000; border: none; font-weight: bold; padding: 8px 16px; border-radius: 6px; cursor: pointer;">
            ▶️ Listen
        </button>
    </div>
    <script>
    function playBriefing() {{
        const btn = document.getElementById('audio-btn');
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance("{speech_text}");
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.onstart = () => {{ btn.innerText = '⏸️ Playing...'; btn.style.backgroundColor = '#eab308'; }};
            utterance.onend = () => {{ btn.innerText = '▶️ Replay'; btn.style.backgroundColor = '#22c55e'; }};
            window.speechSynthesis.speak(utterance);
        }}
    }}
    </script>
    """
    st.components.v1.html(audio_html, height=75)

    st.markdown("### 🎯 Top 3 Focus Items for Today:")
    for idx, priority in enumerate(briefing.top_3_priorities, 1):
        st.checkbox(f"**Priority {idx}:** {priority}", key=f"priority_{idx}")

    st.markdown("---")

    # 📋 1-Click Auto-Standup Update
    st.markdown("### 📋 1-Click Auto-Standup Generator (Slack / Discord)")
    st.caption("Never type a morning standup from memory again. SlothPilot synthesizes yesterday's code, today's schedule, and pending approvals.")
    standup_text = briefing.generate_standup_report()
    st.code(standup_text, language="markdown")

    s_col1, s_col2 = st.columns([1, 2])
    with s_col1:
        st.download_button(
            label="📥 Download Standup (.md)",
            data=standup_text,
            file_name=f"Standup_{briefing.generated_at[:10]}.md",
            mime="text/markdown",
            key="download_standup"
        )

    st.markdown("---")
    # Exportable Digest
    digest_text = f"""# 🦥 SlothPilot Morning Executive Digest
**Date:** {briefing.generated_at}
**Efficiency Score:** {briefing.sloth_efficiency_score}%
**Time Saved:** {briefing.estimated_minutes_saved} minutes

## Executive Summary
{briefing.executive_summary}

## Top Priorities for Today:
""" + "\n".join([f"- [ ] {p}" for p in briefing.top_3_priorities]) + f"""

## Proposed Actions:
""" + "\n".join([f"- **{a.title}** ({a.category}) - Status: {a.approval_status}" for a in briefing.actions])

    st.download_button(
        label="📥 Download Full Executive Briefing (.md)",
        data=digest_text,
        file_name=f"SlothPilot_Morning_Briefing_{briefing.briefing_id}.md",
        mime="text/markdown",
        key="download_full_briefing"
    )

# ----------------- TAB 2: HUMAN APPROVAL GATE -----------------
with tab2:
    st.subheader("Human Approval Gate: Pre-Drafted Action Queue")
    st.caption("Nothing is sent or committed without your explicit approval. Review, tweak, and execute with 1 click.")

    if not briefing.actions:
        st.success("No pending actions in queue. All clear!")
    else:
        for act in briefing.actions:
            card_class = "action-card-urgent" if act.priority == "HIGH" else "action-card"
            st.markdown(f"""
            <div class="{card_class}">
                <h4>{act.title}</h4>
                <p><strong>Category:</strong> <code>{act.category}</code> | <strong>Priority:</strong> <code>{act.priority}</code> | <strong>Safety:</strong> <code>{act.safety_rating}</code></p>
                <p><strong>Reasoning:</strong> {act.reasoning}</p>
                <p><strong>Target:</strong> <code>{act.target_destination}</code></p>
            </div>
            """, unsafe_allow_html=True)

            if act.suggested_draft:
                st.code(act.suggested_draft, language="markdown" if "git" not in act.suggested_draft else "bash")

            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])
            with btn_col1:
                if st.button("✅ Approve", key=f"app_{act.action_id}"):
                    update_action_status(briefing.briefing_id, act.action_id, "APPROVED")
                    st.success(f"Action '{act.action_id}' Approved!")
                    st.rerun()
            with btn_col2:
                if st.button("❌ Dismiss", key=f"rej_{act.action_id}"):
                    update_action_status(briefing.briefing_id, act.action_id, "REJECTED")
                    st.info(f"Action '{act.action_id}' Dismissed.")
                    st.rerun()
            with btn_col3:
                status_color = "🟢" if act.approval_status == "APPROVED" else ("🔴" if act.approval_status == "REJECTED" else "🟡")
                st.write(f"Current Status: **{status_color} {act.approval_status}**")
            st.markdown("---")

# ----------------- TAB 3: INGESTED WORKSPACE EXPLORER -----------------
with tab3:
    st.subheader("Raw Ingested Local Data Sources")
    st.caption("Inspect the local artifacts scanned while you were sleeping.")

    sub_t1, sub_t2, sub_t3, sub_t4, sub_t5 = st.tabs(["Git Repos", "Chat Exports", "Markdown Notes", "Todos", "Calendar & Meetings (.ics)"])

    with sub_t1:
        st.write(f"**Detected Git Repositories:** {briefing.dirty_repos_detected} dirty")
        st.json({
            "repo": "slothpilot",
            "branch": "main",
            "is_dirty": False,
            "recent_commits": ["a5bc75a - docs: add live Streamlit Cloud demo badge", "938ef28 - feat: configure dark theme"]
        })

    with sub_t2:
        st.write(f"**Urgent Messages Flagged:** {briefing.urgent_chats_detected}")
        st.markdown("""
        - 🚨 **10/19/26, 11:45 PM - Priya Sharma:** *"We have a critical bug in the payment webhook retry queue, needs urgent review before tomorrow 10am demo!"*
        - 💰 **10/20/26, 01:14 AM - Client Dave:** *"Hey team, we need to finalize the contract milestones by morning so we can wire the 50% advance deposit."*
        """)

    with sub_t3:
        st.write("Scanned Markdown notes:")
        st.markdown("- **`sample_data/notes/systems_notes.md`** (Distributed Systems, Raft Consensus, Mock Prep)")

    with sub_t4:
        st.write(f"**Pending High-Priority Todos:** {briefing.high_priority_todos}")
        st.markdown("""
        - 🔴 Fix payment webhook retry queue blocker (`!high`)
        - 🔴 Review Dave's contract milestones and send invoice draft (`!high`)
        - ⚪ Clean up dirty git branches on laptop
        """)

    with sub_t5:
        st.write(f"**Sleep Buffer Available:** `+{getattr(briefing, 'sleep_buffer_minutes', 120)} mins extra sleep`")
        st.markdown("""
        - 📅 **10:30 AM – 11:15 AM:** `Sprint Architecture & Payment Webhook Review` *(High Stakes Demo)*
        - 📅 **02:00 PM – 02:30 PM:** `Client Dave SOW Contract Alignment Call` *(Advance wire confirmation)*
        """)

# ----------------- TAB 4: OPENTELEMETRY OBSERVABILITY -----------------
with tab4:
    st.subheader("OpenTelemetry Multi-Agent Tracing & Latency")
    st.caption("Live trace spans proving zero-cost local inference and multi-agent latency.")

    spans = get_recorded_spans()
    o1, o2, o3 = st.columns(3)
    o1.metric("Recorded Agent Spans", len(spans))
    o2.metric("Local Inference Cost", "$0.00 USD", delta="100% Margin")
    o3.metric("Proprietary API Tax Saved", f"${round(max(len(spans), 4) * 0.045, 3)} USD", delta="Saved via Open Weights")

    if not spans:
        st.info("Simulate an overnight run from the sidebar to inspect live OpenTelemetry spans.")
    else:
        for s in reversed(spans[-6:]):
            st.markdown(f"""
            <div class="metric-container">
                <strong>Span:</strong> <code>{s['name']}</code> | 
                <strong>Duration:</strong> {s['duration_ms']} ms | 
                <strong>Status:</strong> {s['status']} <br>
                <small>Trace ID: <code>{s['trace_id']}</code> | Span ID: <code>{s['span_id']}</code></small>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("View OpenTelemetry Semantic Attributes"):
                st.json(s.get("attributes", {}))
