import logging
from flask import render_template, request, redirect, url_for, session
from app import app
from app.auth import login_lecturer, logout_session
from flask_bcrypt import Bcrypt
from app.database import handle_db_connection
bcrypt = Bcrypt()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/lecturer_login', methods=['GET', 'POST'])
def lecturer_login():
    if 'lecturer_id' in session:
        return redirect(url_for('lecturer_home'))

    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if login_lecturer(email, password):
            return redirect(url_for('lecturer_home'))
        else:
            error_message = 'Invalid email or password.'
    return render_template('lecturer_login.html', error_message=error_message)

@app.route('/lecturer_home', methods=['GET', 'POST'])
@handle_db_connection
def lecturer_home():
    if 'lecturer_id' not in session:
        return redirect(url_for('lecturer_login'))
    
    return render_template('lecturer_home.html')

@app.route('/lecturer_profile')
def lecturer_profile():
    lecturer_email = session.get('lecturer_email')  # get from session

    if not lecturer_email:
        return redirect(url_for('lecturer_login'))  # if not logged in, go login

    return render_template('lecturer_profile.html', lecturer_email=lecturer_email)
    
@app.route('/lecturer_logout')
def lecturer_logout():
    logout_session()
    return redirect(url_for('lecturer_login'))
