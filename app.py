from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, jsonify
from extract_table_from_pdf import process_pdf_to_excel
import os
import pdfplumber
import pandas as pd
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# Create upload and output directories if they don't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['OUTPUT_FOLDER']):
    os.makedirs(app.config['OUTPUT_FOLDER'])

# Import models after initializing SQLAlchemy
from models import User, Lecturer, Subject

# Utility function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# Route for main dashboard
@app.route('/main', methods=['GET', 'POST'])
def main_dashboard():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    lecturers = Lecturer.query.all()
    subjects = Subject.query.all()

    if request.method == 'POST':
        file = request.files['pdfFile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process PDF and convert to Excel
            excel_output_path = process_pdf_to_excel(filepath, app.config['OUTPUT_FOLDER'])

            flash('File converted successfully!', 'success')
            return redirect(url_for('download_file', filename=os.path.basename(excel_output_path)))
        else:
            flash('Invalid file format. Please upload a PDF.', 'danger')

    return render_template('main.html', lecturers=lecturers, subjects=subjects)

# Route to provide lecturer information dynamically
@app.route('/get_lecturer_info', methods=['POST'])
def get_lecturer_info():
    data = request.json
    lecturer = Lecturer.query.get(data['lecturer_id'])
    return jsonify(level=lecturer.level, email=lecturer.email, hourlyRate=lecturer.hourly_rate)

# Route to provide subject information dynamically
@app.route('/get_subject_info', methods=['POST'])
def get_subject_info():
    data = request.json
    subject = Subject.query.get(data['subject_code'])
    return jsonify(title=subject.title, startDate="", endDate="")

# Function to extract table data from PDF
def extract_pdf_data(filepath):
    extracted_data = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                extracted_data.extend(table)
    return extracted_data

# Function to convert extracted data to Excel
def convert_to_excel(data, output_folder):
    df = pd.DataFrame(data)
    excel_filename = "output.xlsx"
    excel_filepath = os.path.join(output_folder, excel_filename)
    df.to_excel(excel_filepath, index=False, header=False)
    return excel_filename

# Route to download Excel file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

# Route for logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
