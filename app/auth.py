from flask import session
from app import db, bcrypt
from app.models import ProgramOfficer, Lecturer, Admin

def login_user(email, password):
    for role, model, id_key in [
        ('admin', Admin, 'admin_id'),
        ('program_officer', ProgramOfficer, 'po_id'),
        ('lecturer', Lecturer, 'lecturer_id')
    ]:
        user = model.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session[id_key] = getattr(user, id_key)
            session[f'{role}_email'] = user.email
            return role
    return None

def logout_session():
    session.clear()