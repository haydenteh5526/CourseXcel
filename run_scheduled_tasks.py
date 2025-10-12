import pathlib
from datetime import datetime, timedelta, timezone

from flask import current_app, url_for
from flask_mail import Message

from app import app
from app.models import Admin
from app.po_routes import check_overdue_requisitions
from app.lecturer_routes import check_overdue_claims

# Reuse your Drive service constructor so you don't duplicate auth logic
from app.admin_routes import get_drive_service

# ============================================================
#  File-Based Rate Limiting Setup (for alert emails)
# ============================================================
CACHE_DIR = pathlib.Path("/home/TomazHayden/.cache/coursexcel")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LAST_ALERT_FILE = CACHE_DIR / "last_quota_alert.txt"

# ============================================================
#  Small utilities (pure functions, no Flask request/session)
# ============================================================
def bytes_human(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} EB"

def _should_send_quota_alert(every_hours=6) -> bool:
    """Send at most once every `every_hours`."""
    try:
        if LAST_ALERT_FILE.exists():
            ts = LAST_ALERT_FILE.read_text().strip()
            last = datetime.fromisoformat(ts)
            return datetime.now(timezone.utc) - last >= timedelta(hours=every_hours)
        return True
    except Exception:
        # fail-open: if cache is broken, allow sending
        return True

def _mark_quota_alert_sent():
    try:
        LAST_ALERT_FILE.write_text(datetime.now(timezone.utc).isoformat())
    except Exception:
        pass

# ============================================================
#  Drive quota helpers
# ============================================================
def drive_get_quota():
    """
    Return (usage, limit, usage_in_drive, usage_in_trash) as ints.
    Limit may be 0/None for unlimited (Google sometimes reports 0).
    """
    svc = get_drive_service()
    about = svc.about().get(fields="storageQuota").execute()
    q = (about or {}).get("storageQuota", {})
    usage = int(q.get("usage") or 0)
    limit = int(q.get("limit") or 0)  # 0 or missing -> unlimited/org policies
    usage_in_drive = int(q.get("usageInDrive") or 0)
    usage_in_trash = int(q.get("usageInDriveTrash") or 0)
    return usage, limit, usage_in_drive, usage_in_trash

def drive_quota_status_bg(threshold: float | None = None):
    """
    Background-safe version of drive_quota_status:
    - No Flask 'session'
    - Reads thresholds from app.config if available
    Returns dict:
      {
        "limited": bool,
        "percent": float|None,
        "usage": int,
        "limit": int,
        "message": str,
        "over_threshold": bool (when limited)
      }
    """
    # Pull config safely (works under app_context)
    thr = threshold
    if thr is None:
        try:
            thr = float(current_app.config.get("DRIVE_QUOTA_THRESHOLD", 0.85))
        except Exception:
            thr = 0.85

    usage, limit, usage_in_drive, usage_in_trash = drive_get_quota()

    if not limit:
        # Unlimited or unknown
        return {
            "limited": False,
            "percent": None,
            "usage": usage,
            "limit": limit,
            "message": "Drive storage appears unlimited (no limit reported).",
            "over_threshold": False,
        }

    pct = usage / limit if limit else 0.0
    return {
        "limited": True,
        "percent": pct,
        "usage": usage,
        "limit": limit,
        "message": f"Using {bytes_human(usage)} of {bytes_human(limit)} ({pct*100:.1f}%).",
        "over_threshold": pct >= thr,
    }

# ============================================================
#  Email helper (NO request/session; handles SERVER_NAME fallback)
# ============================================================
def _build_url(endpoint: str, fallback_path: str) -> str:
    """
    Tries to build an absolute URL with url_for(_external=True).
    If SERVER_NAME is not configured, falls back to a relative path.
    """
    try:
        # Needs SERVER_NAME in app.config to succeed outside a request
        return url_for(endpoint, _external=True)
    except Exception:
        # Fallback: relative path so email still contains a usable link
        return fallback_path

def email_admin_low_storage_bg(admin_email: str, quota: dict):
    if not admin_email:
        return

    mail = current_app.extensions.get("mail")
    if not mail:
        return

    # Provide sensible default fallbacks if url_for cannot externalize
    report_url = _build_url("adminReportPage", "/admin/report")
    home_url = _build_url("adminHomepage", "/admin")

    subject = "CourseXcel: Google Drive storage nearing capacity"
    body = (
        "Dear Admin,\n\n"
        f"Our Google Drive storage is nearing capacity. {quota.get('message','')}\n\n"
        "Please take the following actions:\n"
        f"• Generate reports: {report_url}\n"
        f"• Export and clear completed approvals: {home_url}\n\n"
        "Thank you,\n"
        "The CourseXcel Team"
    )

    msg = Message(subject=subject, recipients=[admin_email], body=body)
    mail.send(msg)

# ============================================================
#  Job: Google Drive Quota Check & Admin Alerts
# ============================================================
def job_drive_quota_alert():
    """Checks Google Drive quota and emails all admins if over threshold."""
    quota = drive_quota_status_bg()  # dict with 'limited' and 'over_threshold'
    limited = quota.get("limited", False)
    over = quota.get("over_threshold", False)

    if limited and over and _should_send_quota_alert(every_hours=6):
        admins = Admin.query.all()
        for a in admins:
            if getattr(a, "email", None):
                email_admin_low_storage_bg(a.email, quota)
        _mark_quota_alert_sent()

# ============================================================
#  Scheduled Jobs Entry Point
# ============================================================
if __name__ == "__main__":
    # Ensure we have an app context for DB/Mail/url_for config access
    with app.app_context():
        # NOTE: If your app sends absolute URLs in the emails
        # set this in app config (recommended):
        #   app.config["SERVER_NAME"] = "yourdomain.pythonanywhere.com"
        #   app.config["PREFERRED_URL_SCHEME"] = "https"

        # 1) Requisition reminders (>48h)
        check_overdue_requisitions()

        # 2) Claim reminders (>48h)
        check_overdue_claims()

        # 3) Drive quota alert
        job_drive_quota_alert()
