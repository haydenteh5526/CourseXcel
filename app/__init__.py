from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b5489cc109dde265cf0a7a4a1c924fe3'
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
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ameliadavid7275@gmail.com'
app.config['MAIL_PASSWORD'] = 'dhxu lmsf umti znpo' 
app.config['MAIL_DEFAULT_SENDER'] = 'ameliadavid7275@gmail.com'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Create application context before cleanup
with app.app_context():
    # Clean up connections
    db.session.remove()
    db.engine.dispose()

from app import admin_routes, po_routes, lecturer_routes, subjectsList_routes, lecturersList_routes