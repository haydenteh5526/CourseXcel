from app import bcrypt
from app.models import Admin, Lecturer, ProgramOfficer
from flask import session

def login_user(email, password):
    """
    Authenticate a user (Admin, Program Officer, or Lecturer) based on email and password.
    On successful login, stores user session data and returns their role.
    """

    # Iterate through each role and its corresponding model
    for role, model, id_key, email_key in [
        ('admin', Admin, 'admin_id', 'admin_email'),
        ('program_officer', ProgramOfficer, 'po_id', 'po_email'),
        ('lecturer', Lecturer, 'lecturer_id', 'lecturer_email')
    ]:
        # Query the database for a user with the provided email
        user = model.query.filter_by(email=email).first()

        # If user exists and password matches
        if user and bcrypt.check_password_hash(user.password, password):
            # Enable a persistent session (remains after browser close)
            session.permanent = True

            # Store key identifiers in session for later access
            session[id_key] = getattr(user, id_key)   # e.g., session['admin_id']
            session[email_key] = user.email           # e.g., session['admin_email']

            # Return the role name to indicate successful login
            return role

    # If no matching credentials found for any role
    return None
