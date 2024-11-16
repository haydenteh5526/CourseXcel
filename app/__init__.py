from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

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

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Clean up connections
db.session.remove()
db.engine.dispose()

from app import routes, subject_routes