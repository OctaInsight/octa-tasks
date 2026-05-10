"""Octa Task Manager — UI helpers and dark-mode CSS."""
import streamlit as st
from config import DARK, APP_NAME, APP_VERSION, PRIORITY_COLORS, PRIORITY_ICONS, STATUS_COLORS, STATUS_ICONS, STATUS_LABELS

GLOBAL_CSS = f"""
<style>
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="block-container"] {{
    background-color: {DARK['bg']} !important;
    color: {DARK['text']} !important;
}}
[data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"],
[data-testid="column"],.element-container,.stMarkdown {{
    background: transparent !important;
}}
h1,h2,h3,h4 {{ color: {DARK['text']} !important; }}
p, li {{ color: {DARK['text']}; }}
label, .stTextInput label, .stSelectbox label, .stMultiselect label,
.stTextArea label, .stNumberInput label, .stDateInput label {{
    color: {DARK['muted']} !important; font-size: 0.85rem !important;
}}
[data-testid="stSidebar"] {{
    background: {DARK['sidebar']} !important;
    border-right: 3px solid {DARK['accent']} !important;
    box-shadow: 4px 0 20px rgba(0,188,212,0.1) !important;
}}
[data-testid="stSidebar"] * {{ color: {DARK['text']} !important; }}
[data-testid="stSidebarNav"] {{ display: none !important; }}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; width: 100% !important;
    color: {DARK['text']} !important; font-size: 0.87rem !important;
    text-align: left !important; margin-bottom: 2px !important;
    transition: all 0.18s !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: {DARK['accent']}22 !important;
    border-color: {DARK['accent']}66 !important;
    color: {DARK['accent']} !important;
}}
input, textarea {{
    background: {DARK['bg3']} !important;
    border: 1px solid {DARK['border']} !important;
    border-radius: 8px !important; color: {DARK['text']} !important;
}}
input::placeholder, textarea::placeholder {{ color: {DARK['muted']} !important; }}
div[data-baseweb="select"] > div {{
    background: {DARK['bg3']} !important;
    border-color: {DARK['border']} !important; color: {DARK['text']} !important;
}}
div[data-baseweb="select"] * {{ color: {DARK['text']} !important; }}
div[data-baseweb="popover"] {{
    background: {DARK['bg2']} !important;
    border: 1px solid {DARK['border']} !important;
}}
div[data-baseweb="popover"] li:hover {{ background: {DARK['bg3']} !important; }}
[data-testid="stTabs"] [role="tablist"] {{
    background: {DARK['bg2']}; border-radius: 10px;
    padding: 4px; border: 1px solid {DARK['border']};
}}
[data-testid="stTabs"] [role="tab"] {{
    color: {DARK['muted']} !important; border-radius: 8px;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    background: {DARK['accent']} !important; color: white !important;
}}
[data-testid="stButton"] > button {{
    background: {DARK['bg3']} !important;
    border: 1px solid {DARK['border']} !important;
    color: {DARK['text']} !important; border-radius: 8px !important;
}}
[data-testid="stButton"] > button:hover {{
    border-color: {DARK['accent']} !important; color: {DARK['accent']} !important;
}}
[data-testid="stButton"] > button[kind="primary"] {{
    background: linear-gradient(135deg,{DARK['accent']},#0097A7) !important;
    border: none !important; color: white !important; font-weight: 600 !important;
}}
[data-testid="stExpander"] {{
    background: {DARK['bg2']} !important;
    border: 1px solid {DARK['border']} !important; border-radius: 10px !important;
}}
[data-testid="stExpander"] summary {{ color: {DARK['text']} !important; }}
[data-testid="stProgress"] > div > div {{
    background: {DARK['accent']} !important;
}}
hr {{ border-color: {DARK['border']} !important; }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {DARK['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {DARK['bg3']}; border-radius: 3px; }}
.section-label {{
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: {DARK['accent']};
    margin: 1rem 0 0.4rem; padding-bottom: 0.3rem;
    border-bottom: 1px solid {DARK['border']};
}}
.page-header {{
    background: linear-gradient(135deg,{DARK['sidebar']} 0%,#2d4a7a 100%);
    padding: 1.2rem 1.8rem; border-radius: 12px;
    border-left: 4px solid {DARK['accent']};
    margin-bottom: 1.4rem;
}}
.page-header h1 {{ margin: 0; font-size: 1.6rem; font-weight: 700; color: white !important; }}
.page-header p  {{ margin: 0.2rem 0 0; color: rgba(255,255,255,0.65) !important; font-size: 0.88rem; }}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(f"""
<div class="page-header">
  <h1>{icon + ' ' if icon else ''}{title}</h1>
  {'<p>' + subtitle + '</p>' if subtitle else ''}
</div>""", unsafe_allow_html=True)


def section_label(text: str):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def _hr():
    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.12);margin:0.5rem 0'>",
        unsafe_allow_html=True
    )


def _nav_section(text: str):
    muted = DARK["muted"]
    st.markdown(
        f"<div style='font-size:0.68rem;font-weight:600;letter-spacing:0.1em;"
        f"text-transform:uppercase;color:{muted};margin-bottom:0.3rem'>{text}</div>",
        unsafe_allow_html=True
    )


def priority_badge(priority: str) -> str:
    color = PRIORITY_COLORS.get(priority, DARK["muted"])
    icon  = PRIORITY_ICONS.get(priority, "")
    label = priority.title()
    return (f"<span style='background:{color}22;color:{color};"
            f"border:1px solid {color}44;padding:2px 8px;"
            f"border-radius:10px;font-size:0.72rem;font-weight:600'>"
            f"{icon} {label}</span>")


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, DARK["muted"])
    icon  = STATUS_ICONS.get(status, "")
    label = STATUS_LABELS.get(status, status.replace("_"," ").title())
    return (f"<span style='background:{color}22;color:{color};"
            f"border:1px solid {color}44;padding:2px 8px;"
            f"border-radius:10px;font-size:0.72rem;font-weight:600'>"
            f"{icon} {label}</span>")


def task_card(task: dict, show_assignee: bool = False,
              show_assigner: bool = False,
              users_map: dict = None) -> str:
    """Return HTML for a task summary card (not interactive)."""
    D       = DARK
    bg2     = D["bg2"]; border = D["border"]
    txt     = D["text"]; muted  = D["muted"]
    pri     = task.get("priority","normal")
    status  = task.get("status","pending")
    p_color = PRIORITY_COLORS.get(pri, muted)
    title   = task.get("task","")
    desc    = task.get("description","")
    dl      = task.get("deadline","")
    prog    = int(task.get("progress_pct",0) or 0)

    extra = ""
    if show_assignee and users_map:
        u = users_map.get(task.get("assigned_to"))
        if u:
            fn = u.get("first_name",""); ln = u.get("last_name","")
            name = f"{fn} {ln}".strip() or u.get("username","")
            extra += f"<span style='color:{muted};font-size:0.78rem'>→ {name}</span>  "
    if show_assigner and users_map:
        u = users_map.get(task.get("assigned_by"))
        if u:
            fn = u.get("first_name",""); ln = u.get("last_name","")
            name = f"{fn} {ln}".strip() or u.get("username","")
            extra += f"<span style='color:{muted};font-size:0.78rem'>from {name}</span>  "

    deadline_html = ""
    if dl:
        from datetime import date
        is_overdue = dl < date.today().isoformat() and status != "achieved"
        dl_color   = D["danger"] if is_overdue else muted
        deadline_html = (f"<span style='color:{dl_color};font-size:0.78rem'>"
                         f"📅 {dl}{'  ⚠️ OVERDUE' if is_overdue else ''}</span>")

    prog_bar = ""
    if prog > 0:
        prog_bar = (f"<div style='background:{D["bg3"]};border-radius:4px;"
                    f"height:4px;margin-top:6px'>"
                    f"<div style='background:{p_color};width:{prog}%;"
                    f"height:4px;border-radius:4px'></div></div>")

    return (
        f"<div style='background:{bg2};border:1px solid {border};"
        f"border-left:4px solid {p_color};border-radius:10px;"
        f"padding:0.8rem 1rem;margin-bottom:0.5rem'>"
        f"<div style='display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:0.3rem'>"
        f"{priority_badge(pri)} {status_badge(status)} {extra}"
        f"</div>"
        f"<strong style='color:{txt};font-size:0.95rem'>{title}</strong>"
        + (f"<br><span style='color:{muted};font-size:0.82rem'>{desc[:120]}{'…' if len(desc)>120 else ''}</span>" if desc else "")
        + (f"<br>{deadline_html}" if deadline_html else "")
        + prog_bar
        + "</div>"
    )


def sidebar_nav():
    is_auth       = st.session_state.get("authenticated", False)
    is_admin_user = st.session_state.get("role") == "admin"
    uname         = st.session_state.get("first_name") or st.session_state.get("username","")

    with st.sidebar:
        txt = DARK["text"]; muted = DARK["muted"]
        st.markdown(f"""
<div style="text-align:center;padding:0.9rem 0 0.6rem">
  <div style="font-size:2rem">✅</div>
  <div style="font-weight:700;font-size:0.95rem;color:{txt}">{APP_NAME}</div>
  <div style="color:{muted};font-size:0.65rem">v{APP_VERSION}</div>
</div>""", unsafe_allow_html=True)

        if is_auth and uname:
            st.markdown(
                f"<div style='background:rgba(255,255,255,0.07);"
                f"border:1px solid rgba(255,255,255,0.12);border-radius:8px;"
                f"padding:0.35rem 0.7rem;font-size:0.8rem;margin-bottom:0.3rem'>"
                f"👤 <strong style='color:{txt}'>{uname}</strong></div>",
                unsafe_allow_html=True
            )

        _hr()

        # ── My Work ───────────────────────────────────────────────────────────
        _nav_section("My Work")
        if st.button("📊  Dashboard",    key="nav_dash",   use_container_width=True):
            st.switch_page("app.py")
        if st.button("✅  My Tasks",     key="nav_mine",   use_container_width=True):
            st.switch_page("pages/my_tasks.py")
        if st.button("📌  Assign Task",  key="nav_assign", use_container_width=True):
            st.switch_page("pages/assign_task.py")

        _hr()

        # ── Team (admin only) ─────────────────────────────────────────────────
        if is_admin_user:
            _nav_section("Team")
            if st.button("👥  All Tasks",       key="nav_all",      use_container_width=True):
                st.switch_page("pages/all_tasks.py")
            if st.button("📈  Team Workload",   key="nav_workload", use_container_width=True):
                st.switch_page("pages/team_workload.py")
            _hr()

        # ── Administration ────────────────────────────────────────────────────
        if is_admin_user:
            _nav_section("Administration")
            if st.button("🛡️  Admin Panel", key="nav_admin", use_container_width=True):
                st.switch_page("pages/admin.py")
            _hr()

        # ── Account ───────────────────────────────────────────────────────────
        _nav_section("Account")
        if is_auth:
            if st.button("🚪  Sign Out", use_container_width=True, key="nav_signout"):
                try:
                    from modules.sso import logout
                    logout()
                except Exception:
                    pass
                st.switch_page("pages/login.py")
        else:
            if st.button("🔑  Login", use_container_width=True, key="nav_login"):
                st.switch_page("pages/login.py")

        st.markdown(
            f"<div style='color:{muted};font-size:0.62rem;text-align:center;"
            f"margin-top:1rem'>Octa Platform · "
            f"{__import__('datetime').date.today().year}</div>",
            unsafe_allow_html=True
        )
