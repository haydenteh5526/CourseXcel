from flask import session
from app import db, bcrypt
from app.models import ProgramOfficer, Lecturer, Admin
from app.database import handle_db_connection

@handle_db_connection
def login_po(email, password):
    po = ProgramOfficer.query.filter_by(email=email).first()
    if po and bcrypt.check_password_hash(po.password, password):
        session['po_id'] = po.po_id
        session['po_email'] = po.email
        return True
    return False

@handle_db_connection
def login_lecturer(email, password):
    lecturer = Lecturer.query.filter_by(email=email).first()
    if lecturer and bcrypt.check_password_hash(lecturer.password, password):
        session['lecturer_id'] = lecturer.lecturer_id
        session['lecturer_email'] = lecturer.email
        return True
    return False

@handle_db_connection
def login_admin(email, password):
    admin = Admin.query.filter_by(email=email).first()
    if admin and bcrypt.check_password_hash(admin.password, password):
        session['admin_id'] = admin.admin_id
        session['admin_email'] = admin.email
        return True
    return False

def logout_session():
    session.clear()