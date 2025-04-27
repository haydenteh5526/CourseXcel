from flask import session
from app import db, bcrypt
from app.models import Person, Admin
from app.database import handle_db_connection

@handle_db_connection
def login_po(email, password):
    po = Person.query.filter_by(email=email).first()
    if po and bcrypt.check_password_hash(po.password, password):
        session['po_id'] = po.po_id
        session['po_email'] = po.email
        return True
    return False

@handle_db_connection
def register_po(email, password):
    existing_po = Person.query.filter_by(email=email).first()
    if existing_po:
        return False
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_po = Person(email=email, password=hashed_password)
    db.session.add(new_po)
    db.session.commit()
    return True

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