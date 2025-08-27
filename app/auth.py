from app import bcrypt
from app.models import Admin, Lecturer, ProgramOfficer
from flask import session

def login_user(email, password):
    for role, model, id_key, email_key in [
        ('admin', Admin, 'admin_id', 'admin_email'),
        ('program_officer', ProgramOfficer, 'po_id', 'po_email'),
        ('lecturer', Lecturer, 'lecturer_id', 'lecturer_email')
    ]:
        user = model.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session[id_key] = getattr(user, id_key)
            session[email_key] = user.email
            return role
    return None

def logout_session():
    session.clear()