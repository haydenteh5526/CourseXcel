import logging, socket
from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

# ============================================================
#  Force IPv4 for DNS lookups
# ============================================================
# PythonAnywhere sometimes defaults to IPv6 resolution which can cause issues
# with MySQL or SMTP servers. This override forces the resolver to use IPv4.
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if family == 0:  # AF_UNSPEC → default "any" family → change to IPv4
        family = socket.AF_INET
    return _orig_getaddrinfo(host, port, family, type, proto, flags)
socket.getaddrinfo = _ipv4_only_getaddrinfo

# ============================================================
#  Logging Configuration
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)

# ============================================================
#  Flask App Initialization
# ============================================================
app = Flask(__name__)
app.logger.info("[BACKEND] Flask app initialized.")
app.config['SECRET_KEY'] = 'b5489cc109dde265cf0a7a4a1c924fe3'

# Session management (2-hour expiry for inactivity)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Drive quota alert settings (custom app logic)
app.config['DRIVE_QUOTA_THRESHOLD'] = 0.85        # 85% full triggers alert
app.config['DRIVE_QUOTA_CACHE_SECONDS'] = 600     # cache quota check per session for 10 minutes

# ============================================================
#  Database Settings 
# ============================================================
# MySQL connection via PythonAnywhere
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://TomazHayden:roottoor@TomazHayden.mysql.pythonanywhere-services.com/TomazHayden$CourseXcel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload settings
app.config['UPLOAD_FOLDER'] = 'uploads'

# SQLAlchemy engine options to manage connection pool stability
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 200,  # recycle connections after 200s
    'pool_pre_ping': True, # check connections before using
    'pool_size': 10,      # max 10 persistent connections
    'max_overflow': 5     # allow 5 extra temporary connections
}

# ============================================================
#  Mail Settings
# ============================================================
# Gmail SMTP (app password based)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'ameliadavid7275@gmail.com'
app.config['MAIL_PASSWORD'] = 'ppqn jaqi fibe grol'
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@coursexcel.com'

# Encryption key for sensitive data
app.config['CRYPTO_KEY'] = 'H0GcXQQYagGXqWZBmM84fLqsMQo_R4ZUyk2EVJfIHcY='

# ============================================================
#  Extensions
# ============================================================
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# ============================================================
#  Routes
# ============================================================
# Import routes after app/db/mail are initialized to avoid circular imports
from app import shared_routes, admin_routes, po_routes, lecturer_routes, subjectsList_routes, usersList_routes