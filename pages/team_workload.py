"""Octa Task Manager — Team Workload (Admin)."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date

from modules.auth import require_auth
from modules.sso import auto_login_from_url
from modules.ui_helpers import (inject_css, sidebar_nav, page_header,
                                 section_label, DARK, status_badge, priority_badge)
from modules.database import get_workload_by_user, get_all_tasks, get_all_users
from config import STATUS_COLORS, PRIORITY_COLORS, STATUS_LABELS, DARK as D

st.set_page_config(page_title="Team Workload — Octa", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")
inject_css(); auto_login_from_url(); require_auth(); sidebar_nav()

if st.session_state.get("role") != "admin":
    st.error("🔒 Admin access only.")
    st.stop()

page_header("Team Workload", "Visual task distribution and load per team member", "📈")

workload  = get_workload_by_user()
all_tasks = get_all_tasks()
all_users = get_all_users()
user_map  = {u["id"]: u for u in all_users}
today     = date.today().isoformat()
muted     = D["muted"]; acc = D["accent"]

if not workload:
    st.info("No tasks assigned to anyone yet.")
    st.stop()

# ── Summary KPIs ──────────────────────────────────────────────────────────────
total_people = len(workload)
total_active = sum(w["total"] - w["achieved"] for w in workload)
heaviest     = max(workload, key=lambda w: w["total"] - w["achieved"])
most_overdue = max(workload, key=lambda w: w["overdue"]) if any(w["overdue"] for w in workload) else None

kc1,kc2,kc3,kc4 = st.columns(4)
for col, label, val, color in [
    (kc1, "Team Members with Tasks", total_people,       acc),
    (kc2, "Active Tasks (total)",    total_active,        D["warning"]),
    (kc3, "Heaviest Load",  f"{heaviest['name']} ({heaviest['total'] - heaviest['achieved']} active)", D["accent2"]),
    (kc4, "Most Overdue",  f"{most_overdue['name']} ({most_overdue['overdue']})" if most_overdue and most_overdue['overdue']>0 else "None", D["danger"] if most_overdue and most_overdue['overdue']>0 else D["success"]),
]:
    bg2 = D["bg2"]
    col.markdown(
        f"<div style='background:{bg2};border-top:3px solid {color};"
        f"border:1px solid {color}44;border-radius:10px;"
        f"padding:0.7rem;text-align:center'>"
        f"<div style='font-size:1rem;font-weight:700;color:{color};line-height:1.3'>{val}</div>"
        f"<div style='font-size:0.72rem;color:{muted}'>{label}</div></div>",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Stacked horizontal bar chart ──────────────────────────────────────────────
section_label("📊 Task Load by Team Member")
st.caption("Stacked by status. Click a bar segment in the legend to hide/show that status.")

names    = [w["name"] for w in workload]
pending  = [w.get("pending",0) + w.get("seen",0) for w in workload]
progress = [w.get("in_progress",0) for w in workload]
achieved = [w.get("achieved",0) for w in workload]
overdue  = [w.get("overdue",0) for w in workload]

fig = go.Figure()

fig.add_trace(go.Bar(
    name="In Progress", y=names, x=progress, orientation="h",
    marker_color=STATUS_COLORS["in_progress"], marker_line_width=0,
))
fig.add_trace(go.Bar(
    name="Pending / Seen", y=names, x=pending, orientation="h",
    marker_color=STATUS_COLORS["pending"], marker_line_width=0,
))
fig.add_trace(go.Bar(
    name="Achieved", y=names, x=achieved, orientation="h",
    marker_color=STATUS_COLORS["achieved"], marker_line_width=0, opacity=0.5,
))
fig.add_trace(go.Bar(
    name="⚠️ Overdue", y=names, x=overdue, orientation="h",
    marker_color=D["danger"], marker_line_width=0,
))

fig.update_layout(
    barmode="stack",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    height=max(300, len(names)*50+100),
    margin=dict(l=0,r=20,t=20,b=40),
    font_color=D["text"], font_size=12,
    xaxis=dict(title="Number of Tasks", gridcolor="rgba(255,255,255,0.06)",
               color=D["text"]),
    yaxis=dict(showgrid=False, color=D["text"], autorange="reversed"),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                bgcolor="rgba(0,0,0,0)", font=dict(color=D["text"])),
)
st.plotly_chart(fig, use_container_width=True)

# ── Overdue heatmap ───────────────────────────────────────────────────────────
section_label("⚠️ Overdue by Team Member")

overdue_tasks = [
    t for t in all_tasks
    if t.get("deadline","") and t["deadline"] < today
    and t.get("status") != "achieved"
]

if not overdue_tasks:
    st.success("🎉 No overdue tasks across the team!")
else:
    overdue_by_user = {}
    for t in overdue_tasks:
        uid  = t.get("assigned_to")
        if not uid: continue
        user = user_map.get(uid,{})
        fn   = user.get("first_name",""); ln = user.get("last_name","")
        name = f"{fn} {ln}".strip() or user.get("username","Unknown")
        if name not in overdue_by_user:
            overdue_by_user[name] = []
        overdue_by_user[name].append(t)

    for person, tasks in sorted(overdue_by_user.items(), key=lambda x: -len(x[1])):
        danger = D["danger"]; bg2 = D["bg2"]; border = D["border"]
        with st.expander(f"⚠️ {person}  —  {len(tasks)} overdue", expanded=True):
            for t in sorted(tasks, key=lambda x: x.get("deadline","")):
                dl      = t.get("deadline","")
                days_ov = (date.today() - date.fromisoformat(dl)).days if dl else 0
                pri     = t.get("priority","normal")
                p_color = PRIORITY_COLORS.get(pri, D["muted"])
                txt     = D["text"]
                st.markdown(
                    f"<div style='background:{bg2};border:1px solid {border};"
                    f"border-left:3px solid {danger};border-radius:8px;"
                    f"padding:0.5rem 0.8rem;margin-bottom:0.3rem;display:flex;"
                    f"align-items:center;gap:0.8rem'>"
                    f"<span style='background:{danger}22;color:{danger};"
                    f"padding:1px 7px;border-radius:8px;font-size:0.75rem;font-weight:600'>"
                    f"+{days_ov}d</span>"
                    f"<span style='color:{txt};font-size:0.88rem'>{t.get('task','')}</span>"
                    f"<span style='color:{D["muted"]};font-size:0.78rem'>📅 {dl}</span>"
                    f"{priority_badge(pri)}"
                    f"</div>",
                    unsafe_allow_html=True
                )

# ── Per-person breakdown cards ────────────────────────────────────────────────
section_label("👤 Per-Person Breakdown")

n_cols = 3
cols   = st.columns(n_cols)

for i, w in enumerate(workload):
    with cols[i % n_cols]:
        name    = w["name"]
        total   = w["total"]
        pending_n = w.get("pending",0) + w.get("seen",0)
        prog_n  = w.get("in_progress",0)
        done_n  = w.get("achieved",0)
        ov_n    = w.get("overdue",0)
        active  = total - done_n
        org     = w.get("org","")

        # Colour by workload
        if ov_n > 0:
            border_c = D["danger"]
        elif active > 5:
            border_c = D["warning"]
        else:
            border_c = D["success"]

        bg2 = D["bg2"]; border = D["border"]; txt = D["text"]
        st.markdown(
            f"<div style='background:{bg2};border:1px solid {border};"
            f"border-top:3px solid {border_c};border-radius:12px;"
            f"padding:1rem;margin-bottom:0.8rem'>"
            f"<div style='font-size:1rem;font-weight:700;color:{txt}'>{name}</div>"
            + (f"<div style='font-size:0.75rem;color:{muted}'>{org}</div>" if org else "")
            + f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:0.3rem;margin-top:0.6rem'>"
            f"<div style='text-align:center;background:{D["bg3"]};border-radius:8px;padding:0.4rem'>"
            f"<div style='font-size:1.3rem;font-weight:700;color:{acc}'>{active}</div>"
            f"<div style='font-size:0.7rem;color:{muted}'>Active</div></div>"
            f"<div style='text-align:center;background:{D["bg3"]};border-radius:8px;padding:0.4rem'>"
            f"<div style='font-size:1.3rem;font-weight:700;color:{D["success"]}'>{done_n}</div>"
            f"<div style='font-size:0.7rem;color:{muted}'>Achieved</div></div>"
            f"<div style='text-align:center;background:{D["bg3"]};border-radius:8px;padding:0.4rem'>"
            f"<div style='font-size:1.3rem;font-weight:700;color:{D["warning"]}'>{prog_n}</div>"
            f"<div style='font-size:0.7rem;color:{muted}'>In Progress</div></div>"
            f"<div style='text-align:center;background:{D["bg3"]};border-radius:8px;padding:0.4rem'>"
            f"<div style='font-size:1.3rem;font-weight:700;color:{D["danger"]}'>{ov_n}</div>"
            f"<div style='font-size:0.7rem;color:{muted}'>Overdue</div></div>"
            f"</div></div>",
            unsafe_allow_html=True
        )
