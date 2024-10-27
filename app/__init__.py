from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b5489cc109dde265cf0a7a4a1c924fe3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:haydenteh%405526@localhost/coursepdfextractor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
app.app_context().push()
bcrypt = Bcrypt(app)
    
from app import routes