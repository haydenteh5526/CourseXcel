from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import User, Lecturer, Subject
from app.extract_table_from_pdf import extract_table_from_pdf, convert_tables_to_excel

# Define the Blueprint
main_bp = Blueprint('main', __name__)

# Configuration values
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}

# Check if folders exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def allowed_file(filename):
    """Check if the file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------- ROUTES -------- #

# Home / Login Route
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.main_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

# Main Dashboard Route
@main_bp.route('/main', methods=['GET', 'POST'])
def main_dashboard():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('main.login'))

    lecturers = Lecturer.query.all()
    subjects = Subject.query.all()

    if request.method == 'POST':
        # Handle file upload
        file = request.files.get('pdfFile')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Extract tables and convert to Excel
            tables = extract_table_from_pdf(filepath)
            if tables:
                output_path = os.path.join(OUTPUT_FOLDER, 'output.xlsx')
                convert_tables_to_excel(tables, output_path)

                flash('PDF file processed successfully and converted to Excel!', 'success')
                return redirect(url_for('main.download_file', filename='output.xlsx'))
            else:
                flash('No tables found in the uploaded PDF.', 'warning')
        else:
            flash('Please upload a valid PDF file.', 'danger')

    return render_template('main.html', lecturers=lecturers, subjects=subjects)

# Download Excel File Route
@main_bp.route('/download/<filename>')
def download_file(filename):
    """Serve the converted Excel file for download."""
    return send_from_directory(OUTPUT_FOLDER, filename)

# Dynamic Lecturer Information Route
@main_bp.route('/get_lecturer_info', methods=['POST'])
def get_lecturer_info():
    """Fetch and return information about a specific lecturer."""
    data = request.json
    lecturer = Lecturer.query.get(data['lecturer_id'])
    if lecturer:
        return jsonify(level=lecturer.level, email=lecturer.email, hourlyRate=lecturer.hourly_rate)
    return jsonify(message='Lecturer not found'), 404

# Dynamic Subject Information Route
@main_bp.route('/get_subject_info', methods=['POST'])
def get_subject_info():
    """Fetch and return information about a specific subject."""
    data = request.json
    subject = Subject.query.get(data['subject_code'])
    if subject:
        return jsonify(title=subject.title)  # Add startDate and endDate if applicable
    return jsonify(message='Subject not found'), 404

# Logout Route
@main_bp.route('/logout')
def logout():
    """Log out the user and clear the session."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))

# Redirect root URL to login
@main_bp.route('/')
def index():
    return redirect(url_for('main.login'))
