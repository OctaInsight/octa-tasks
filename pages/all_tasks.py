"""Octa Task Manager — All Tasks (Admin)."""
import streamlit as st
from datetime import date

from modules.auth import require_auth
from modules.sso import auto_login_from_url
from modules.ui_helpers import (inject_css, sidebar_nav, page_header,
                                 section_label, DARK, priority_badge, status_badge)
from modules.database import get_all_tasks, get_all_users, update_task_status, delete_task
from config import PRIORITIES, STATUSES, STATUS_LABELS, PRIORITY_COLORS, STATUS_COLORS, DARK as D
import plotly.graph_objects as go

st.set_page_config(page_title="All Tasks — Octa", page_icon="👥",
                   layout="wide", initial_sidebar_state="expanded")
inject_css(); auto_login_from_url(); require_auth(); sidebar_nav()

if st.session_state.get("role") != "admin":
    st.error("🔒 Admin access only.")
    st.stop()

page_header("All Tasks", "Full team task overview — filter, manage and monitor", "👥")

all_users = get_all_users()
user_map  = {u["id"]: u for u in all_users}
all_tasks = get_all_tasks()
today     = date.today().isoformat()
muted     = D["muted"]; acc = D["accent"]

def _name(uid):
    u = user_map.get(uid,{})
    fn = u.get("first_name",""); ln = u.get("last_name","")
    return f"{fn} {ln}".strip() or u.get("username","Unknown") if u else "Unknown"

# ── Summary mini-chart ────────────────────────────────────────────────────────
status_counts = {}
for t in all_tasks:
    s = t.get("status","pending")
    status_counts[s] = status_counts.get(s,0) + 1

if status_counts:
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    total = len(all_tasks)
    overdue_n = sum(1 for t in all_tasks if t.get("deadline","") < today and t.get("status") != "achieved")
    for col, label, val, color in [
        (sc1,"Total",       total,                           acc),
        (sc2,"Pending",     status_counts.get("pending",0),  D["muted"]),
        (sc3,"In Progress", status_counts.get("in_progress",0),D["warning"]),
        (sc4,"Achieved",    status_counts.get("achieved",0), D["success"]),
        (sc5,"Overdue",     overdue_n,                       D["danger"]),
    ]:
        bg2 = D["bg2"]
        col.markdown(
            f"<div style='background:{bg2};border-top:3px solid {color};"
            f"border:1px solid {color}44;border-radius:10px;"
            f"padding:0.65rem;text-align:center'>"
            f"<div style='font-size:1.4rem;font-weight:700;color:{color}'>{val}</div>"
            f"<div style='font-size:0.75rem;color:{muted}'>{label}</div></div>",
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)

# ── Filters ───────────────────────────────────────────────────────────────────
section_label("🔍 Filters")
ff1, ff2, ff3, ff4, ff5 = st.columns(5)
with ff1:
    user_opts = ["All users"] + [_name(u["id"]) for u in all_users]
    f_user    = st.selectbox("Person", user_opts, key="at_user")
with ff2:
    f_status  = st.selectbox("Status", ["All"] + [STATUS_LABELS[s] for s in STATUSES], key="at_status")
with ff3:
    f_pri     = st.selectbox("Priority", ["All","Urgent","High","Normal","Low"], key="at_pri")
with ff4:
    f_overdue = st.selectbox("Overdue", ["All","Overdue only","Not overdue"], key="at_ov")
with ff5:
    f_search  = st.text_input("Search task title", placeholder="Keyword…", key="at_search")

# Apply filters
filtered = all_tasks
if f_user != "All users":
    uid_sel  = next((u["id"] for u in all_users if (_name(u["id"])==f_user)), None)
    if uid_sel:
        filtered = [t for t in filtered if t.get("assigned_to")==uid_sel or t.get("assigned_by")==uid_sel]
if f_status != "All":
    status_rev = {v:k for k,v in STATUS_LABELS.items()}
    filtered   = [t for t in filtered if t.get("status")==status_rev.get(f_status)]
if f_pri != "All":
    filtered   = [t for t in filtered if t.get("priority","").lower()==f_pri.lower()]
if f_overdue == "Overdue only":
    filtered   = [t for t in filtered if t.get("deadline","") and t["deadline"]<today and t.get("status")!="achieved"]
elif f_overdue == "Not overdue":
    filtered   = [t for t in filtered if not (t.get("deadline","") and t["deadline"]<today)]
if f_search:
    q = f_search.lower()
    filtered = [t for t in filtered if q in (t.get("task","")).lower()]

st.markdown(
    f"<p style='color:{muted};font-size:0.84rem'>"
    f"<strong style='color:{D["text"]}'>{len(filtered)}</strong> task(s)</p>",
    unsafe_allow_html=True
)

if not filtered:
    st.info("No tasks match the filters.")
    st.stop()

# ── Task table ────────────────────────────────────────────────────────────────
section_label("📋 Task List")

pri_w = {"urgent":0,"high":1,"normal":2,"low":3}
filtered.sort(key=lambda t: (
    0 if (t.get("deadline","") < today and t.get("status")!="achieved") else 1,
    t.get("deadline","9999"),
    pri_w.get(t.get("priority","normal"),2)
))

for t in filtered:
    tid     = t["id"]
    pri     = t.get("priority","normal")
    status  = t.get("status","pending")
    dl      = t.get("deadline","")
    is_ov   = dl and dl < today and status != "achieved"
    p_color = PRIORITY_COLORS.get(pri, D["muted"])
    assignee_name = _name(t.get("assigned_to"))
    assigner_name = _name(t.get("assigned_by"))
    prog    = int(t.get("progress_pct",0) or 0)

    with st.expander(
        f"{t.get('task','')}  →  {assignee_name}  ·  {STATUS_LABELS.get(status,status)}"
        + ("  ⚠️ OVERDUE" if is_ov else ""),
        expanded=is_ov
    ):
        ec1, ec2 = st.columns([3,1])
        with ec1:
            txt = D["text"]
            st.markdown(
                f"<strong style='color:{txt};font-size:0.95rem'>{t.get('task','')}</strong>",
                unsafe_allow_html=True
            )
            if t.get("description"):
                st.markdown(
                    f"<p style='color:{D["muted"]};font-size:0.83rem'>"
                    f"{t.get('description','')}</p>",
                    unsafe_allow_html=True
                )
            meta = []
            dl_c = D["danger"] if is_ov else D["muted"]
            if dl:   meta.append(f"<span style='color:{dl_c}'>📅 {dl}</span>")
            meta.append(f"<span style='color:{muted}'>→ {assignee_name}</span>")
            meta.append(f"<span style='color:{muted}'>from {assigner_name}</span>")
            if t.get("proposal_id"):
                meta.append(f"<span style='color:{muted}'>📋 {t['proposal_id']}</span>")
            if t.get("app_origin"):
                meta.append(f"<span style='color:{muted}'>🔗 {t['app_origin']}</span>")
            st.markdown(
                "<div style='display:flex;flex-wrap:wrap;gap:0.8rem;font-size:0.8rem;"
                f"margin:0.4rem 0'>" + "  ".join(meta) + "</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"{priority_badge(pri)} {status_badge(status)}",
                unsafe_allow_html=True
            )
            if prog:
                st.progress(prog/100, text=f"{prog}%")
            # Notes
            if t.get("assigner_note"):
                warn = D["warning"]
                st.markdown(
                    f"<div style='background:{warn}11;border-left:3px solid {warn};"
                    f"border-radius:6px;padding:0.3rem 0.6rem;font-size:0.8rem;color:{warn}'>"
                    f"📌 Assigner: {t['assigner_note']}</div>",
                    unsafe_allow_html=True
                )
            if t.get("assignee_note"):
                suc = D["success"]
                st.markdown(
                    f"<div style='background:{suc}11;border-left:3px solid {suc};"
                    f"border-radius:6px;padding:0.3rem 0.6rem;font-size:0.8rem;color:{suc}'>"
                    f"💬 Assignee: {t['assignee_note']}</div>",
                    unsafe_allow_html=True
                )

        with ec2:
            # Admin can update status and delete
            with st.form(f"admin_update_{tid}"):
                new_status = st.selectbox("Status", STATUSES,
                    index=STATUSES.index(status) if status in STATUSES else 0,
                    format_func=lambda s: STATUS_LABELS.get(s,s),
                    key=f"ast_{tid}")
                new_prog = st.slider("Progress %", 0, 100, prog, 5, key=f"aprog_{tid}")
                ac1, ac2 = st.columns(2)
                with ac1:
                    if st.form_submit_button("💾 Save", type="primary",
                                              use_container_width=True):
                        if update_task_status(tid, new_status, progress_pct=new_prog):
                            st.success("Saved!"); st.rerun()
                with ac2:
                    if st.form_submit_button("🗑 Delete", use_container_width=True):
                        if delete_task(tid): st.rerun()
