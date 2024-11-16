from flask import session
from app import db, bcrypt
from app.models import Person, Admin

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

def login_admin(email, password):
    admin = Admin.query.filter_by(email=email).first()
    if admin and bcrypt.check_password_hash(admin.password, password):
        session['admin_id'] = admin.admin_id
        session['admin_email'] = admin.email
        return True
    return False

def logout_session():
    session.clear()