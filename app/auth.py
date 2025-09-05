from app import bcrypt
from app.models import Admin, Lecturer, ProgramOfficer
from flask import session

def login_user(email, password):
    for role, model, id_key, email_key in [
        ('admin', Admin, 'admin_id', 'admin_email'),
        ('program_officer', ProgramOfficer, 'po_id', 'po_email'),
        ('lecturer', Lecturer, 'lecturer_id', 'lecturer_email'),
    ]:
        # use the model's actual email field name
        user = model.query.filter_by(**{email_key: email}).first()
        if user is None:
            continue

        if bcrypt.check_password_hash(user.password, password):
            session.permanent = True
            session[id_key] = getattr(user, id_key)              
            session[email_key] = getattr(user, email_key)        
            return role
    return None
