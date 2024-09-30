from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    level = db.Column(db.String(100))
    email = db.Column(db.String(150))
    hourly_rate = db.Column(db.Float)

class Subject(db.Model):
    code = db.Column(db.String(10), primary_key=True)
    title = db.Column(db.String(200))
