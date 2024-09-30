from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'b5489cc109dde265cf0a7a4a1c924fe3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://if0_37251857:ShKv8cddwqF@sql205.infinityfree.com/if0_37251857_coursepdfextractor'

db = SQLAlchemy()

from coursepdfextractor import routes