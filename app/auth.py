from flask import session
from app import db, bcrypt
from app.models import Person  # Assuming you have an Person model

def login_user(email, password):
    user = Person.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.user_id
        session['user_email'] = user.email
        return True
    return False

def register_user(email, password):
    existing_user = Person.query.filter_by(email=email).first()
    if existing_user:
        return False
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = Person(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return True

def logout_user():
    session.pop('user_id', None)
    session.pop('user_email', None)
