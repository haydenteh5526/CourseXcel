import os
import logging
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session
from app import app, db, bcrypt
from app.models import Admin, Department, Lecturer, Person, Program, Subject
from app.excel_generator import generate_excel  # Updated import
from werkzeug.utils import secure_filename
from app.auth import login_user, register_user

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configurations
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')  # Use app.root_path for absolute path
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure that the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key_here'  # Ensure to use a strong secret key for session management

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('main'))  # Redirect to main page if already logged in

    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if login_user(email, password):
            return redirect(url_for('main'))
        else:
            error_message = 'Invalid email or password.'
    return render_template('login.html', error_message=error_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if register_user(email, password):
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists.', 'error')
    return render_template('register.html')  # Create this template

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/result', methods=['POST'])
def result():
    try:
        # Debug: Print all form data
        print("Form Data:", request.form)
        
        # Get form data
        school_centre = request.form.get('school_centre')
        lecturer_name = request.form.get('lecturer_name')
        if lecturer_name == 'new_lecturer':
            lecturer_name = request.form.get('new_lecturer_name')
        designation = request.form.get('designation')
        ic_number = request.form.get('ic_number')

        # Extract course details from form
        course_details = []
        for i in range(1, 6):  # Maximum 5 courses
            subject_code = request.form.get(f'subjectCode{i}')
            if not subject_code:
                continue
                
            # Debug: Print individual course data
            print(f"Course {i} data:")
            print(f"Lecture weeks: {request.form.get(f'lectureWeeks{i}')}")
            print(f"Tutorial weeks: {request.form.get(f'tutorialWeeks{i}')}")
            print(f"Practical weeks: {request.form.get(f'practicalWeeks{i}')}")
            
            course_data = {
                'program_level': request.form.get(f'programLevel{i}'),
                'subject_code': subject_code,
                'subject_title': request.form.get(f'subjectTitle{i}'),
                'lecture_weeks': int(request.form.get(f'lectureWeeks{i}', 0)),
                'tutorial_weeks': int(request.form.get(f'tutorialWeeks{i}', 0)),
                'practical_weeks': int(request.form.get(f'practicalWeeks{i}', 0)),
                'elearning_weeks': int(request.form.get(f'elearningWeeks{i}', 14)),
                'start_date': request.form.get(f'teachingPeriodStart{i}'),
                'end_date': request.form.get(f'teachingPeriodEnd{i}'),
                'hourly_rate': int(request.form.get(f'hourlyRate{i}', 60))  # Add this line
            }
            course_details.append(course_data)

        # Debug: Print processed course details
        print("Processed course details:", course_details)

        if not course_details:
            return jsonify(success=False, error="No course details provided"), 400

        # Generate Excel file
        output_filename = generate_excel(
            school_centre=school_centre,
            lecturer_name=lecturer_name,
            designation=designation,
            ic_number=ic_number,
            course_details=course_details
        )
        
        return jsonify(success=True, filename=output_filename)
    except Exception as e:
        logging.error(f"Error in result route: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/result_page')
def result_page():
    filename = request.args.get('filename')
    return render_template('result.html', filename=filename)

@app.route('/download')
def download():
    filename = request.args.get('filename')
    if filename:
        file_path = os.path.join(app.root_path, 'outputs', filename)  # Ensure the correct path
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            logging.error(f"Download error: {e}")
            flash('Error occurred while trying to download the file', 'danger')
            return redirect(url_for('result_page', filename=filename))
    else:
        flash('No file to download', 'warning')
        return redirect(url_for('result_page'))

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Fetch all records from all tables
    admins = Admin.query.all()
    departments = Department.query.all()
    lecturers = Lecturer.query.all()
    persons = Person.query.all()
    programs = Program.query.all()
    subjects = Subject.query.all()
    return render_template('admin.html', admins=admins, departments=departments, 
                           lecturers=lecturers, persons=persons, programs=programs, 
                           subjects=subjects)
