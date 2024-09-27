from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

class Lecturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    level = db.Column(db.String(100))
    email = db.Column(db.String(150), nullable=True)  # Can be nullable or add stricter constraints
    hourly_rate = db.Column(db.Float, nullable=True)  # Float is more appropriate for rates

class Subject(db.Model):
    code = db.Column(db.String(10), primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Ensure title is not nullable
