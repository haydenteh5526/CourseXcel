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
            # Check if 2FA is enabled
            if user.two_factor_enabled and user.two_factor_secret:
                session.clear()
                session['pending_role'] = role
                session['pending_user_id'] = getattr(user, id_key)
                session['pending_email'] = user.email
                return '2fa_required'  # signal for 2FA step

            # Normal login (no 2FA)
            session.permanent = True
            session[id_key] = getattr(user, id_key)
            session[email_key] = user.email
            return role
    return None
