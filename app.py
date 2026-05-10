"""Octa Task Manager — Dashboard."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date, timedelta

from modules.auth import require_auth
from modules.sso import auto_login_from_url, set_token_in_url, get_token_from_url
from modules.ui_helpers import inject_css, sidebar_nav, page_header, section_label, DARK, status_badge, priority_badge
from modules.database import (get_my_tasks, get_tasks_assigned_by_me,
                               get_my_stats, get_team_stats,
                               get_all_tasks, get_all_users)
from config import PRIORITY_COLORS, STATUS_COLORS, DARK as D

st.set_page_config(page_title="Task Manager — Octa",
                   page_icon="✅", layout="wide",
                   initial_sidebar_state="expanded")
inject_css()
auto_login_from_url()
require_auth()

token = st.session_state.get("sso_token","") or get_token_from_url()
if token: set_token_in_url(token)

sidebar_nav()
page_header("Task Manager", "Your personal task hub and team overview", "✅")

user_id  = st.session_state.get("user_id")
is_admin = st.session_state.get("role") == "admin"
uname    = st.session_state.get("first_name") or st.session_state.get("username","")
D        = DARK
muted    = D["muted"]; acc = D["accent"]

my_stats = get_my_stats(user_id)

# ── KPI row — My stats ────────────────────────────────────────────────────────
section_label(f"📋 My Tasks — {uname}")
k1,k2,k3,k4,k5,k6 = st.columns(6)
kpi_data = [
    (k1, "Total",       my_stats["total"],       D["accent"]),
    (k2, "Pending",     my_stats["pending"],      D["muted"]),
    (k3, "In Progress", my_stats["in_progress"],  D["warning"]),
    (k4, "Achieved",    my_stats["achieved"],      D["success"]),
    (k5, "Overdue",     my_stats["overdue"],       D["danger"]),
    (k6, "Urgent",      my_stats["urgent"],        "#fc8181"),
]
for col, label, val, color in kpi_data:
    bg2 = D["bg2"]
    col.markdown(
        f"<div style='background:{bg2};border-top:3px solid {color};"
        f"border:1px solid {color}44;border-radius:10px;"
        f"padding:0.7rem;text-align:center'>"
        f"<div style='font-size:1.6rem;font-weight:700;color:{color}'>{val}</div>"
        f"<div style='font-size:0.75rem;color:{muted}'>{label}</div></div>",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts row ────────────────────────────────────────────────────────────────
ch1, ch2 = st.columns(2)

with ch1:
    my_tasks = get_my_tasks(user_id)
    status_counts = {}
    for t in my_tasks:
        s = t.get("status","pending")
        status_counts[s] = status_counts.get(s,0) + 1

    if status_counts:
        labels = list(status_counts.keys())
        values = list(status_counts.values())
        colors = [STATUS_COLORS.get(l, D["muted"]) for l in labels]
        labels_nice = [l.replace("_"," ").title() for l in labels]

        fig = go.Figure(go.Pie(
            labels=labels_nice, values=values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color=D["bg"], width=2)),
            textfont=dict(color=D["text"]),
        ))
        fig.update_layout(
            title=dict(text="My Tasks by Status", font=dict(color=D["text"],size=13)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=260, margin=dict(l=0,r=0,t=40,b=0),
            showlegend=True,
            legend=dict(font=dict(color=D["text"],size=11), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tasks yet.")

with ch2:
    pri_counts = {}
    for t in my_tasks:
        p = t.get("priority","normal")
        pri_counts[p] = pri_counts.get(p,0) + 1

    if pri_counts:
        order  = ["urgent","high","normal","low"]
        labels = [p for p in order if p in pri_counts]
        values = [pri_counts[p] for p in labels]
        colors = [PRIORITY_COLORS.get(p, D["muted"]) for p in labels]
        labels_nice = [l.title() for l in labels]

        fig2 = go.Figure(go.Bar(
            x=labels_nice, y=values,
            marker=dict(color=colors, line=dict(width=0)),
            text=values, textposition="outside",
            textfont=dict(color=D["text"]),
        ))
        fig2.update_layout(
            title=dict(text="My Tasks by Priority", font=dict(color=D["text"],size=13)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=260, margin=dict(l=0,r=0,t=40,b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", color=D["text"]),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", color=D["text"]),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── Team stats (admin) ────────────────────────────────────────────────────────
if is_admin:
    team = get_team_stats()
    section_label("👥 Team Overview")
    tk1,tk2,tk3,tk4,tk5 = st.columns(5)
    for col, label, val, color in [
        (tk1,"Total Tasks",   team["total"],       acc),
        (tk2,"Pending",       team["pending"],      D["muted"]),
        (tk3,"In Progress",   team["in_progress"],  D["warning"]),
        (tk4,"Achieved",      team["achieved"],      D["success"]),
        (tk5,"Overdue",       team["overdue"],       D["danger"]),
    ]:
        bg2 = D["bg2"]
        col.markdown(
            f"<div style='background:{bg2};border-top:3px solid {color};"
            f"border:1px solid {color}44;border-radius:10px;"
            f"padding:0.7rem;text-align:center'>"
            f"<div style='font-size:1.4rem;font-weight:700;color:{color}'>{val}</div>"
            f"<div style='font-size:0.75rem;color:{muted}'>{label}</div></div>",
            unsafe_allow_html=True
        )

# ── Upcoming deadlines ────────────────────────────────────────────────────────
section_label("📅 My Upcoming Deadlines (next 14 days)")
today   = date.today()
horizon = (today + timedelta(days=14)).isoformat()
today_s = today.isoformat()

upcoming = [
    t for t in my_tasks
    if t.get("deadline") and t["deadline"] >= today_s
    and t["deadline"] <= horizon
    and t.get("status") != "achieved"
]
upcoming.sort(key=lambda x: x.get("deadline",""))

if not upcoming:
    st.info("No deadlines in the next 14 days. 🎉")
else:
    for t in upcoming:
        dl        = t.get("deadline","")
        dl_date   = date.fromisoformat(dl)
        days_left = (dl_date - today).days
        pri       = t.get("priority","normal")
        pri_color = PRIORITY_COLORS.get(pri, D["muted"])
        urgency   = D["danger"] if days_left <= 3 else (D["warning"] if days_left <= 7 else D["success"])
        bg2       = D["bg2"]; border = D["border"]; txt = D["text"]

        st.markdown(
            f"<div style='background:{bg2};border:1px solid {border};"
            f"border-left:4px solid {pri_color};border-radius:10px;"
            f"padding:0.7rem 1rem;margin-bottom:0.4rem;"
            f"display:flex;flex-wrap:wrap;align-items:center;gap:0.8rem'>"
            f"<span style='background:{urgency}22;color:{urgency};"
            f"padding:2px 10px;border-radius:8px;font-size:0.8rem;font-weight:600'>"
            f"{days_left}d left</span>"
            f"<strong style='color:{txt}'>{t.get('task','')}</strong>"
            f"<span style='color:{D["muted"]};font-size:0.8rem'>📅 {dl}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

# ── Overdue tasks ─────────────────────────────────────────────────────────────
overdue = [
    t for t in my_tasks
    if t.get("deadline") and t["deadline"] < today_s
    and t.get("status") != "achieved"
]
if overdue:
    section_label(f"⚠️ Overdue Tasks ({len(overdue)})")
    for t in overdue:
        danger = D["danger"]; bg2 = D["bg2"]; border = D["border"]; txt = D["text"]
        st.markdown(
            f"<div style='background:{bg2};border:1px solid {danger}44;"
            f"border-left:4px solid {danger};border-radius:10px;"
            f"padding:0.7rem 1rem;margin-bottom:0.4rem'>"
            f"<strong style='color:{danger}'>⚠️ {t.get('task','')}</strong>"
            f"<span style='color:{D["muted"]};font-size:0.8rem'> · Due {t.get('deadline','')}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    if st.button("→ View & resolve overdue tasks", type="primary"):
        st.switch_page("pages/my_tasks.py")

# ── Recent tasks assigned by me ───────────────────────────────────────────────
assigned_by_me = get_tasks_assigned_by_me(user_id)
pending_from_me = [t for t in assigned_by_me if t.get("status") != "achieved"]

if pending_from_me:
    section_label(f"📌 Tasks I Assigned (pending: {len(pending_from_me)})")
    all_users = {u["id"]: u for u in get_all_users()}
    for t in pending_from_me[:5]:
        assignee = all_users.get(t.get("assigned_to"),{})
        fn = assignee.get("first_name",""); ln = assignee.get("last_name","")
        name = f"{fn} {ln}".strip() or assignee.get("username","Unknown")
        status = t.get("status","pending")
        s_color= STATUS_COLORS.get(status, D["muted"])
        bg2    = D["bg2"]; border = D["border"]; txt = D["text"]
        st.markdown(
            f"<div style='background:{bg2};border:1px solid {border};"
            f"border-left:4px solid {s_color};border-radius:10px;"
            f"padding:0.6rem 1rem;margin-bottom:0.3rem'>"
            f"<strong style='color:{txt}'>{t.get('task','')}</strong>"
            f" <span style='color:{D["muted"]};font-size:0.8rem'>→ {name}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
