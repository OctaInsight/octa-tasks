"""Octa Task Manager — Configuration."""

APP_NAME    = "Task Manager"
APP_ICON    = "✅"
APP_VERSION = "1.0.0"

DARK = {
    "bg":      "#0f1421",
    "bg2":     "#1a2235",
    "bg3":     "#232f45",
    "border":  "rgba(255,255,255,0.09)",
    "text":    "#e2e8f0",
    "muted":   "#8899b0",
    "accent":  "#00BCD4",
    "accent2": "#FF6B35",
    "sidebar": "#1B2A4A",
    "success": "#6fcf97",
    "warning": "#f6cc52",
    "danger":  "#fc8181",
}

PRIORITY_COLORS = {
    "urgent": "#fc8181",
    "high":   "#f6cc52",
    "normal": "#00BCD4",
    "low":    "#8899b0",
}

PRIORITY_ICONS = {
    "urgent": "🔴",
    "high":   "🟠",
    "normal": "🔵",
    "low":    "⚪",
}

STATUS_COLORS = {
    "pending":     "#8899b0",
    "seen":        "#00BCD4",
    "in_progress": "#f6cc52",
    "achieved":    "#6fcf97",
}

STATUS_ICONS = {
    "pending":     "⏳",
    "seen":        "👁",
    "in_progress": "🔄",
    "achieved":    "✅",
}

STATUS_LABELS = {
    "pending":     "Pending",
    "seen":        "Seen",
    "in_progress": "In Progress",
    "achieved":    "Achieved",
}

PRIORITIES = ["urgent", "high", "normal", "low"]
STATUSES   = ["pending", "seen", "in_progress", "achieved"]
