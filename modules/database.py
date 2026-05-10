"""Octa Task Manager — Supabase database layer."""
import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone, date


@st.cache_resource
def _client() -> Client:
    return create_client(st.secrets["supabase"]["url"],
                         st.secrets["supabase"]["key"])

def db() -> Client:
    return _client()

def _now():
    return datetime.now(timezone.utc).isoformat()


# ── Users ─────────────────────────────────────────────────────────────────────

def get_all_users() -> list:
    try:
        return db().table("octa_users").select(
            "id,username,first_name,last_name,email,role,organisation"
        ).eq("status","approved").order("first_name").execute().data or []
    except Exception:
        return []

def get_user_by_id(uid: int) -> dict | None:
    try:
        r = db().table("octa_users").select(
            "id,username,first_name,last_name,email,role,organisation"
        ).eq("id", uid).execute()
        return r.data[0] if r.data else None
    except Exception:
        return None

def _display_name(user: dict) -> str:
    if not user:
        return "Unknown"
    fn = user.get("first_name","")
    ln = user.get("last_name","")
    if fn or ln:
        return f"{fn} {ln}".strip()
    return user.get("username","Unknown")


# ── Tasks ─────────────────────────────────────────────────────────────────────

def get_my_tasks(user_id: int) -> list:
    """Tasks assigned TO the current user."""
    try:
        return db().table("tasks").select("*") \
                   .eq("assigned_to", user_id) \
                   .order("created_at", desc=True).execute().data or []
    except Exception:
        return []

def get_tasks_assigned_by_me(user_id: int) -> list:
    """Tasks assigned BY the current user."""
    try:
        return db().table("tasks").select("*") \
                   .eq("assigned_by", user_id) \
                   .order("created_at", desc=True).execute().data or []
    except Exception:
        return []

def get_all_tasks() -> list:
    """All tasks — for admin view."""
    try:
        return db().table("tasks").select("*") \
                   .order("created_at", desc=True).execute().data or []
    except Exception:
        return []

def create_task(data: dict) -> tuple:
    try:
        data["created_at"] = _now()
        data["updated_at"] = _now()
        data.setdefault("status", "pending")
        r = db().table("tasks").insert(data).execute()
        return True, r.data[0]["id"] if r.data else None
    except Exception as e:
        return False, str(e)

def update_task(task_id: int, data: dict) -> bool:
    try:
        data["updated_at"] = _now()
        db().table("tasks").update(data).eq("id", task_id).execute()
        return True
    except Exception:
        return False

def update_task_status(task_id: int, status: str,
                        note: str = "", progress_pct: int = None) -> bool:
    """Update status + timestamps + optional note and progress."""
    now = _now()
    patch = {"status": status, "updated_at": now}

    if status == "seen"        and not patch.get("seen_at"):
        patch["seen_at"] = now
    if status == "in_progress" :
        patch["started_at"] = now
    if status == "achieved"    :
        patch["achieved_at"] = now
        patch["progress_pct"] = 100

    if note:
        patch["assignee_note"] = note
    if progress_pct is not None:
        patch["progress_pct"] = progress_pct

    return update_task(task_id, patch)

def delete_task(task_id: int) -> bool:
    try:
        db().table("tasks").delete().eq("id", task_id).execute()
        return True
    except Exception:
        return False

def get_task_by_id(task_id: int) -> dict | None:
    try:
        r = db().table("tasks").select("*").eq("id", task_id).execute()
        return r.data[0] if r.data else None
    except Exception:
        return None


# ── Task comments ─────────────────────────────────────────────────────────────

def get_task_comments(task_id: int) -> list:
    try:
        return db().table("task_comments").select("*") \
                   .eq("task_id", task_id) \
                   .order("created_at").execute().data or []
    except Exception:
        return []

def add_comment(task_id: int, user_id: int, comment: str) -> bool:
    try:
        db().table("task_comments").insert({
            "task_id":    task_id,
            "user_id":    user_id,
            "comment":    comment.strip(),
            "created_at": _now(),
        }).execute()
        return True
    except Exception:
        return False


# ── Dashboard stats ───────────────────────────────────────────────────────────

def get_my_stats(user_id: int) -> dict:
    tasks = get_my_tasks(user_id)
    today = date.today().isoformat()
    return {
        "total":       len(tasks),
        "pending":     sum(1 for t in tasks if t.get("status") == "pending"),
        "in_progress": sum(1 for t in tasks if t.get("status") == "in_progress"),
        "achieved":    sum(1 for t in tasks if t.get("status") == "achieved"),
        "overdue":     sum(1 for t in tasks
                          if t.get("deadline") and t["deadline"] < today
                          and t.get("status") not in ("achieved",)),
        "urgent":      sum(1 for t in tasks
                          if t.get("priority") == "urgent"
                          and t.get("status") != "achieved"),
    }

def get_team_stats() -> dict:
    """Aggregate stats for admin dashboard."""
    tasks = get_all_tasks()
    today = date.today().isoformat()
    return {
        "total":       len(tasks),
        "pending":     sum(1 for t in tasks if t.get("status") == "pending"),
        "in_progress": sum(1 for t in tasks if t.get("status") == "in_progress"),
        "achieved":    sum(1 for t in tasks if t.get("status") == "achieved"),
        "overdue":     sum(1 for t in tasks
                          if t.get("deadline") and t["deadline"] < today
                          and t.get("status") != "achieved"),
    }

def get_workload_by_user() -> list:
    """
    Returns [{user_id, pending, in_progress, achieved, overdue, total}, ...]
    for the team workload chart.
    """
    tasks = get_all_tasks()
    users = get_all_users()
    today = date.today().isoformat()

    user_map = {u["id"]: u for u in users}
    workload = {}

    for t in tasks:
        uid = t.get("assigned_to")
        if not uid:
            continue
        if uid not in workload:
            workload[uid] = {"pending":0,"seen":0,"in_progress":0,
                             "achieved":0,"overdue":0,"total":0}
        workload[uid]["total"] += 1
        status = t.get("status","pending")
        workload[uid][status] = workload[uid].get(status, 0) + 1
        if (t.get("deadline","") or "") < today and status != "achieved":
            workload[uid]["overdue"] += 1

    result = []
    for uid, stats in workload.items():
        user = user_map.get(uid, {})
        result.append({
            "user_id":   uid,
            "name":      _display_name(user),
            "org":       user.get("organisation",""),
            **stats,
        })
    return sorted(result, key=lambda x: -x["total"])


# ── Proposals (read-only for context labels) ──────────────────────────────────

def get_all_proposals_brief() -> list:
    try:
        return db().table("proposals").select(
            "proposal_id,acronym,proposal_title"
        ).order("proposal_id", desc=True).execute().data or []
    except Exception:
        return []
