# /home/TomazHayden/CourseXcel/run_jobs.py
import pathlib
from datetime import datetime, timedelta, timezone

from app import app
from app.po_routes import check_overdue_requisitions
from app.lecturer_routes import check_overdue_claims

from app.admin_routes import drive_quota_status, email_admin_low_storage
from app.models import Admin

# --- simple file-based rate limit so we don't spam admins ---
CACHE_DIR = pathlib.Path("/home/TomazHayden/.cache/coursexcel")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LAST_ALERT_FILE = CACHE_DIR / "last_quota_alert.txt"

def _should_send_quota_alert(every_hours=6) -> bool:
    """Send at most once every `every_hours`."""
    try:
        if LAST_ALERT_FILE.exists():
            ts = LAST_ALERT_FILE.read_text().strip()
            last = datetime.fromisoformat(ts)  # datetime object (naive or aware depending on stored format)
            return datetime.now(timezone.utc) - last >= timedelta(hours=every_hours)
        return True
    except Exception:
        # if anything odd, allow sending (fail open)
        return True

def _mark_quota_alert_sent():
    try:
        LAST_ALERT_FILE.write_text(datetime.now(timezone.utc).isoformat())
    except Exception:
        pass

def job_drive_quota_alert():
    """Checks Google Drive quota and emails all admins if over threshold."""
    quota = drive_quota_status()  # should return dict with 'limited' and 'over_threshold'
    limited = quota.get("limited", False)
    over = quota.get("over_threshold", False)

    if limited and over and _should_send_quota_alert(every_hours=6):
        admins = Admin.query.all()
        for a in admins:
            if getattr(a, "email", None):
                email_admin_low_storage(a.email, quota)
        _mark_quota_alert_sent()

if __name__ == "__main__":
    # Run all jobs under Flask app context (required for DB + Mail)
    with app.app_context():
        # remind approvers on requisitions pending >48h
        check_overdue_requisitions()

        # remind approvers on claims pending >48h
        check_overdue_claims()

        # alert admins if Drive quota exceeds configured threshold
        job_drive_quota_alert()
