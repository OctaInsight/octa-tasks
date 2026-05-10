"""Octa Task Manager — My Tasks."""
import streamlit as st
from datetime import date

from modules.auth import require_auth
from modules.sso import auto_login_from_url
from modules.ui_helpers import (inject_css, sidebar_nav, page_header,
                                 section_label, DARK, priority_badge,
                                 status_badge, task_card)
from modules.database import (get_my_tasks, update_task_status,
                               get_task_comments, add_comment,
                               get_user_by_id)
from config import PRIORITIES, STATUSES, STATUS_LABELS, PRIORITY_COLORS, STATUS_COLORS, DARK as D

st.set_page_config(page_title="My Tasks — Octa", page_icon="✅",
                   layout="wide", initial_sidebar_state="expanded")
inject_css(); auto_login_from_url(); require_auth(); sidebar_nav()

page_header("My Tasks", "Tasks assigned to you — update status and add notes", "✅")

user_id = st.session_state.get("user_id")
muted   = D["muted"]; acc = D["accent"]

# ── Filters ───────────────────────────────────────────────────────────────────
fc1, fc2, fc3 = st.columns(3)
with fc1:
    f_status = st.selectbox("Filter by Status",
        ["All"] + [STATUS_LABELS[s] for s in STATUSES], key="mt_status")
with fc2:
    f_pri = st.selectbox("Filter by Priority",
        ["All", "Urgent", "High", "Normal", "Low"], key="mt_pri")
with fc3:
    f_search = st.text_input("Search", placeholder="Task title or description…",
                              key="mt_search")

all_my = get_my_tasks(user_id)
today  = date.today().isoformat()

# Apply filters
filtered = all_my
if f_status != "All":
    status_rev = {v: k for k,v in STATUS_LABELS.items()}
    filtered = [t for t in filtered if t.get("status") == status_rev.get(f_status)]
if f_pri != "All":
    filtered = [t for t in filtered if t.get("priority","").lower() == f_pri.lower()]
if f_search:
    q = f_search.lower()
    filtered = [t for t in filtered
                if q in (t.get("task","")).lower()
                or q in (t.get("description","")).lower()]

# Sort: overdue first, then by deadline, then by priority weight
pri_w = {"urgent":0,"high":1,"normal":2,"low":3}
def _sort_key(t):
    dl      = t.get("deadline","9999-99-99")
    overdue = 0 if (dl < today and t.get("status") != "achieved") else 1
    return (overdue, dl, pri_w.get(t.get("priority","normal"),2))

filtered = sorted(filtered, key=_sort_key)

# Counts
st.markdown(
    f"<p style='color:{muted};font-size:0.84rem'>"
    f"<strong style='color:{D["text"]}'>{len(filtered)}</strong> of "
    f"{len(all_my)} tasks</p>",
    unsafe_allow_html=True
)

if not filtered:
    st.info("No tasks match your filters.")
    st.stop()

# ── Task list ─────────────────────────────────────────────────────────────────
for t in filtered:
    tid    = t["id"]
    pri    = t.get("priority","normal")
    status = t.get("status","pending")
    p_color= PRIORITY_COLORS.get(pri, D["muted"])
    dl     = t.get("deadline","")
    is_ov  = dl and dl < today and status != "achieved"
    prog   = int(t.get("progress_pct",0) or 0)

    # Card border: danger if overdue, else priority color
    border_color = D["danger"] if is_ov else p_color

    with st.expander(
        f"{t.get('task','')}  ·  {pri.title()}  ·  {STATUS_LABELS.get(status, status)}"
        + ("  ⚠️ OVERDUE" if is_ov else ""),
        expanded=is_ov
    ):
        tc1, tc2 = st.columns([3, 2])

        with tc1:
            txt = D["text"]
            st.markdown(
                f"<strong style='color:{txt};font-size:1rem'>{t.get('task','')}</strong>",
                unsafe_allow_html=True
            )
            if t.get("description"):
                st.markdown(
                    f"<p style='color:{muted};font-size:0.85rem;margin:0.3rem 0'>"
                    f"{t.get('description','')}</p>",
                    unsafe_allow_html=True
                )

            # Meta row
            meta = []
            if dl:
                dl_color = D["danger"] if is_ov else muted
                meta.append(f"<span style='color:{dl_color}'>📅 {dl}</span>")
            if t.get("proposal_id"):
                meta.append(f"<span style='color:{muted}'>📋 {t['proposal_id']}</span>")
            if t.get("app_origin"):
                meta.append(f"<span style='color:{muted}'>🔗 {t['app_origin']}</span>")
            if meta:
                st.markdown(
                    f"<div style='display:flex;gap:1rem;flex-wrap:wrap;"
                    f"margin:0.4rem 0;font-size:0.8rem'>" + "  ·  ".join(meta) + "</div>",
                    unsafe_allow_html=True
                )

            # Assigner note
            if t.get("assigner_note"):
                warn = D["warning"]
                st.markdown(
                    f"<div style='background:{warn}11;border-left:3px solid {warn};"
                    f"border-radius:6px;padding:0.4rem 0.7rem;margin-top:0.4rem;"
                    f"font-size:0.82rem;color:{warn}'>"
                    f"💬 Assigner note: {t['assigner_note']}</div>",
                    unsafe_allow_html=True
                )

        with tc2:
            with st.form(f"task_update_{tid}"):
                new_status = st.selectbox(
                    "Update Status",
                    options=STATUSES,
                    index=STATUSES.index(status) if status in STATUSES else 0,
                    format_func=lambda s: STATUS_LABELS.get(s, s),
                    key=f"sel_status_{tid}"
                )
                new_prog = st.slider("Progress %", 0, 100, prog, 5,
                                      key=f"prog_{tid}")
                note = st.text_area("Add note", height=60,
                                     placeholder="Update note…",
                                     key=f"note_{tid}",
                                     value=t.get("assignee_note","") or "")

                if st.form_submit_button("💾 Save Update", type="primary",
                                          use_container_width=True):
                    ok = update_task_status(tid, new_status, note, new_prog)
                    if ok:
                        st.success("✅ Updated!")
                        st.rerun()
                    else:
                        st.error("Update failed.")

        # ── Comment thread ────────────────────────────────────────────────────
        comments = get_task_comments(tid)
        if comments or True:
            st.markdown(
                f"<div style='margin-top:0.8rem;font-size:0.78rem;color:{muted};"
                f"font-weight:600;text-transform:uppercase;letter-spacing:0.06em'>"
                f"💬 Activity ({len(comments)})</div>",
                unsafe_allow_html=True
            )
            for c in comments:
                user = get_user_by_id(c.get("user_id"))
                name = f"{user.get('first_name','')} {user.get('last_name','')}".strip() if user else "Unknown"
                ts   = str(c.get("created_at",""))[:16].replace("T"," ")
                bg2  = D["bg2"]; border = D["border"]; txt = D["text"]
                st.markdown(
                    f"<div style='background:{bg2};border:1px solid {border};"
                    f"border-radius:8px;padding:0.4rem 0.7rem;margin-bottom:0.2rem'>"
                    f"<span style='color:{acc};font-size:0.78rem;font-weight:600'>{name}</span>"
                    f" <span style='color:{muted};font-size:0.72rem'>{ts}</span><br>"
                    f"<span style='color:{txt};font-size:0.84rem'>{c.get('comment','')}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with st.form(f"comment_{tid}"):
                new_comment = st.text_input("Add comment", placeholder="Type a comment…",
                                             key=f"cmt_{tid}",
                                             label_visibility="collapsed")
                if st.form_submit_button("💬 Send", use_container_width=True):
                    if new_comment.strip():
                        add_comment(tid, user_id, new_comment)
                        st.rerun()
