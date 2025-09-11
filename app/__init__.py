import socket

# Force IPv4 resolver override
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if family == 0:  # AF_UNSPEC → prefer IPv4
        family = socket.AF_INET
    return _orig_getaddrinfo(host, port, family, type, proto, flags)
socket.getaddrinfo = _ipv4_only_getaddrinfo

from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b5489cc109dde265cf0a7a4a1c924fe3'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

app.config['DRIVE_QUOTA_THRESHOLD'] = 0.00001 # 0.85        # 85% full triggers alert
app.config['DRIVE_QUOTA_CACHE_SECONDS'] = 1 #600     # cache quota check per session for 10 minutes

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://TomazHayden:roottoor@TomazHayden.mysql.pythonanywhere-services.com/TomazHayden$CourseXcel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 200,
    'pool_pre_ping': True,
    'pool_size': 10,
    'max_overflow': 5
}

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'ameliadavid7275@gmail.com'
app.config['MAIL_PASSWORD'] = 'ppqn jaqi fibe grol'
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@coursexcel.com'

app.config['CRYPTO_KEY'] = 'H0GcXQQYagGXqWZBmM84fLqsMQo_R4ZUyk2EVJfIHcY='

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Create application context before cleanup
with app.app_context():
    # Clean up connections
    db.session.remove()
    db.engine.dispose()

from app import admin_routes, po_routes, lecturer_routes, subjectsList_routes, usersList_routes
