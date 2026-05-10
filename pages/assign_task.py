"""Octa Task Manager — Assign Task."""
import streamlit as st
from datetime import date, timedelta

from modules.auth import require_auth
from modules.sso import auto_login_from_url
from modules.ui_helpers import inject_css, sidebar_nav, page_header, section_label, DARK, status_badge, priority_badge
from modules.database import (get_all_users, get_tasks_assigned_by_me,
                               create_task, update_task, delete_task,
                               get_all_proposals_brief, get_user_by_id)
from config import PRIORITIES, STATUS_LABELS, PRIORITY_COLORS, STATUS_COLORS, DARK as D

st.set_page_config(page_title="Assign Task — Octa", page_icon="📌",
                   layout="wide", initial_sidebar_state="expanded")
inject_css(); auto_login_from_url(); require_auth(); sidebar_nav()

page_header("Assign Task", "Create tasks and assign them to your team", "📌")

user_id   = st.session_state.get("user_id")
is_admin  = st.session_state.get("role") == "admin"
muted     = D["muted"]; acc = D["accent"]

users     = get_all_users()
proposals = get_all_proposals_brief()

user_opts = {
    f"{u.get('first_name','')} {u.get('last_name','')}".strip() or u.get("username",""): u["id"]
    for u in users
}
prop_opts = {"— No proposal link —": None} | {
    f"{p.get('acronym','')} — {p.get('proposal_title','')[:40]}": p["proposal_id"]
    for p in proposals
}

# ═══════════════════════════════════════════════════════════════════════════════
# NEW TASK FORM
# ═══════════════════════════════════════════════════════════════════════════════
section_label("➕ New Task")
with st.form("new_task_form", clear_on_submit=True):
    ft1, ft2 = st.columns([3, 1])
    with ft1:
        task_title = st.text_input("Task *", placeholder="Short, clear task description")
    with ft2:
        priority = st.selectbox("Priority", PRIORITIES,
                                 format_func=lambda p: p.title(), index=2)

    task_desc = st.text_area("Description / Details", height=80,
                              placeholder="Additional context, links, or instructions…")

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        assignee_label = st.selectbox("Assign To *", list(user_opts.keys()),
                                       key="at_assignee")
        assignee_id    = user_opts[assignee_label]
    with fc2:
        deadline = st.date_input("Deadline",
                                  value=date.today() + timedelta(days=7),
                                  min_value=date.today())
    with fc3:
        prop_sel = st.selectbox("Link to Proposal (optional)",
                                 list(prop_opts.keys()), key="at_prop")
        prop_id  = prop_opts[prop_sel]

    assigner_note = st.text_input("Note to assignee (optional)",
                                   placeholder="Anything the person should know…")

    if st.form_submit_button("📌 Assign Task", type="primary", use_container_width=True):
        if not task_title.strip():
            st.error("❌ Task title is required.")
        elif not assignee_id:
            st.error("❌ Please select who to assign to.")
        else:
            ok, tid = create_task({
                "task":          task_title.strip(),
                "description":   task_desc.strip(),
                "priority":      priority,
                "assigned_by":   user_id,
                "assigned_to":   assignee_id,
                "deadline":      deadline.isoformat(),
                "proposal_id":   prop_id,
                "assigner_note": assigner_note.strip(),
                "app_origin":    "octa_tasks",
                "status":        "pending",
                "progress_pct":  0,
            })
            if ok:
                st.success(f"✅ Task assigned to **{assignee_label}**!")
                st.rerun()
            else:
                st.error(f"❌ Failed: {tid}")

# ═══════════════════════════════════════════════════════════════════════════════
# TASKS I ASSIGNED
# ═══════════════════════════════════════════════════════════════════════════════
section_label("📋 Tasks I Assigned")
my_assigned = get_tasks_assigned_by_me(user_id)

if not my_assigned:
    st.info("You haven't assigned any tasks yet.")
    st.stop()

# Filter tabs
tab_active, tab_done = st.tabs([
    f"🔄 Active ({sum(1 for t in my_assigned if t.get('status') != 'achieved')})",
    f"✅ Achieved ({sum(1 for t in my_assigned if t.get('status') == 'achieved')})",
])

all_users_map = {u["id"]: u for u in users}
today = date.today().isoformat()

def _render_assigned(tasks):
    for t in tasks:
        tid      = t["id"]
        pri      = t.get("priority","normal")
        status   = t.get("status","pending")
        assignee = all_users_map.get(t.get("assigned_to"),{})
        fn  = assignee.get("first_name",""); ln = assignee.get("last_name","")
        aname = f"{fn} {ln}".strip() or assignee.get("username","Unknown")
        dl   = t.get("deadline","")
        is_ov= dl and dl < today and status != "achieved"
        p_color= PRIORITY_COLORS.get(pri, D["muted"])
        s_color= STATUS_COLORS.get(status, D["muted"])
        prog   = int(t.get("progress_pct",0) or 0)
        bg2    = D["bg2"]; border = D["border"]; txt = D["text"]

        with st.expander(
            f"{t.get('task','')}  →  {aname}  ·  {STATUS_LABELS.get(status,status)}"
            + ("  ⚠️ OVERDUE" if is_ov else ""),
            expanded=False
        ):
            ic1, ic2 = st.columns([3,1])
            with ic1:
                st.markdown(
                    f"<strong style='color:{txt}'>{t.get('task','')}</strong>",
                    unsafe_allow_html=True
                )
                if t.get("description"):
                    st.markdown(
                        f"<p style='color:{D["muted"]};font-size:0.84rem'>"
                        f"{t.get('description','')}</p>",
                        unsafe_allow_html=True
                    )
                meta = []
                if dl: meta.append(f"📅 {dl}" + (" ⚠️" if is_ov else ""))
                if t.get("proposal_id"): meta.append(f"📋 {t['proposal_id']}")
                if t.get("assignee_note"):
                    meta.append(f"💬 Note from assignee: {t['assignee_note']}")
                for m in meta:
                    dl_c = D["danger"] if "⚠️" in m else D["muted"]
                    st.markdown(
                        f"<span style='color:{dl_c};font-size:0.8rem'>{m}</span>",
                        unsafe_allow_html=True
                    )

                # Progress bar
                if prog > 0:
                    st.progress(prog / 100, text=f"Progress: {prog}%")

                # Current status badge
                st.markdown(
                    f"{priority_badge(pri)} {status_badge(status)}",
                    unsafe_allow_html=True
                )

            with ic2:
                with st.form(f"edit_assigned_{tid}"):
                    new_dl = st.date_input("Update deadline",
                                           value=date.fromisoformat(dl) if dl else date.today(),
                                           key=f"edl_{tid}")
                    new_note = st.text_area("Update my note", height=60,
                                             value=t.get("assigner_note","") or "",
                                             key=f"enote_{tid}")
                    new_pri  = st.selectbox("Priority", PRIORITIES,
                                            index=PRIORITIES.index(pri) if pri in PRIORITIES else 2,
                                            format_func=lambda p: p.title(),
                                            key=f"epri_{tid}")
                    ea1, ea2 = st.columns(2)
                    with ea1:
                        if st.form_submit_button("💾 Save", type="primary",
                                                  use_container_width=True):
                            ok = update_task(tid, {
                                "deadline":      new_dl.isoformat(),
                                "assigner_note": new_note.strip(),
                                "priority":      new_pri,
                            })
                            if ok: st.success("Saved!"); st.rerun()
                    with ea2:
                        if st.form_submit_button("🗑 Delete", use_container_width=True):
                            if delete_task(tid): st.rerun()

with tab_active:
    active = [t for t in my_assigned if t.get("status") != "achieved"]
    active.sort(key=lambda t: (t.get("deadline","9999") < today and t.get("status")!="achieved", t.get("deadline","9999")))
    if active:
        _render_assigned(active)
    else:
        st.success("No active tasks assigned by you. 🎉")

with tab_done:
    done = [t for t in my_assigned if t.get("status") == "achieved"]
    if done:
        _render_assigned(done)
    else:
        st.info("No achieved tasks yet.")
