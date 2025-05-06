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

@app.route('/lecturerLoginPage', methods=['GET', 'POST'])
def lecturerLoginPage():
    if 'lecturer_id' in session:
        return redirect(url_for('lecturerHomepage'))

    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if login_lecturer(email, password):
            return redirect(url_for('lecturerHomepage'))
        else:
            error_message = 'Invalid email or password.'
    return render_template('lecturerLoginPage.html', error_message=error_message)

@app.route('/lecturerHomepage', methods=['GET', 'POST'])
@handle_db_connection
def lecturerHomepage():
    if 'lecturer_id' not in session:
        return redirect(url_for('lecturerLoginPage'))
    
    return render_template('lecturerHomepage.html')

@app.route('/lecturerProfilePage')
def lecturerProfilePage():
    lecturer_email = session.get('lecturer_email')  # get from session

    if not lecturer_email:
        return redirect(url_for('lecturerLoginPage'))  # if not logged in, go login

    return render_template('lecturerProfilePage.html', lecturer_email=lecturer_email)
    
@app.route('/lecturerLogout')
def lecturerLogout():
    logout_session()
    return redirect(url_for('lecturerLoginPage'))
