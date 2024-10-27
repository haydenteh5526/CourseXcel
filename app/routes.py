import os
import logging
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session
from app import app, db, bcrypt
from app.models import Admin, Department, Lecturer, Person, Program, Subject
from app.excel_generator import generate_excel
from werkzeug.utils import secure_filename
from app.auth import login_user, register_user, login_admin, logout_session
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurations
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key_here'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main'))

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
    return render_template('register.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('main.html')

@app.route('/result', methods=['POST'])
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    filename = request.args.get('filename')
    return render_template('result.html', filename=filename)

@app.route('/download')
def download():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    filename = request.args.get('filename')
    if filename:
        file_path = os.path.join(app.root_path, 'outputs', filename)
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            logging.error(f"Download error: {e}")
            flash('Error occurred while trying to download the file', 'danger')
            return redirect(url_for('result_page', filename=filename))
    else:
        flash('No file to download', 'warning')
        return redirect(url_for('result_page'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error_message = None
    if 'admin_id' in session:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if login_admin(email, password):
            flash('Logged in as admin successfully.', 'success')
            return redirect(url_for('admin'))
        else:
            error_message = 'Invalid email or password.'

    return render_template('admin-login.html', error_message=error_message)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    admins = Admin.query.all()
    departments = Department.query.all()
    lecturers = Lecturer.query.all()
    persons = Person.query.all()
    programs = Program.query.all()
    subjects = Subject.query.all()
    return render_template('admin.html', admins=admins, departments=departments, 
                           lecturers=lecturers, persons=persons, programs=programs, 
                           subjects=subjects)

@app.route('/logout')
def logout():
    logout_session()
    return redirect(url_for('login'))

@app.route('/admin/upload-course-structure', methods=['POST'])
def upload_course_structure():
    if 'admin_id' not in session:
        logger.error('Unauthorized access attempt')
        return jsonify({'success': False, 'error': 'Not authorized'})
        
    try:
        if 'file' not in request.files:
            logger.error('No file in request')
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        level = request.form.get('level')
        
        logger.info(f'Processing file: {file.filename} for level: {level}')
        
        if file.filename == '':
            logger.error('No file selected')
            return jsonify({'success': False, 'error': 'No file selected'})
            
        if not allowed_file(file.filename):
            logger.error(f'Invalid file type: {file.filename}')
            return jsonify({'success': False, 'error': 'Invalid file type'})

        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f'File saved temporarily at: {filepath}')

        try:
            # Read Excel file
            df = pd.read_excel(filepath)
            logger.info(f'Excel file read successfully. Columns: {df.columns.tolist()}')
            
            # Check required columns
            required_columns = ['Subject Code', 'Subject Description', 'Lecture Hours', 
                              'Tutorial Hours', 'Practical Hours']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f'Missing columns: {missing_columns}')
                return jsonify({
                    'success': False, 
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                })

            # Process each row
            rows_processed = 0
            for _, row in df.iterrows():
                if pd.isna(row['Subject Code']):
                    continue

                try:
                    # Create or update subject
                    subject = Subject.query.filter_by(subject_code=row['Subject Code']).first()
                    if not subject:
                        subject = Subject(
                            subject_code=row['Subject Code'],
                            subject_title=row['Subject Description'],
                            program_level=level,
                            L=row['Lecture Hours'].split('x')[0] if isinstance(row['Lecture Hours'], str) else row['Lecture Hours'],
                            T=row['Tutorial Hours'].split('x')[0] if isinstance(row['Tutorial Hours'], str) else row['Tutorial Hours'],
                            P=row['Practical Hours'].split('x')[0] if isinstance(row['Practical Hours'], str) else row['Practical Hours']
                        )
                        db.session.add(subject)
                        logger.info(f'Added new subject: {subject.subject_code}')
                    else:
                        subject.subject_title = row['Subject Description']
                        subject.program_level = level
                        subject.L = row['Lecture Hours'].split('x')[0] if isinstance(row['Lecture Hours'], str) else row['Lecture Hours']
                        subject.T = row['Tutorial Hours'].split('x')[0] if isinstance(row['Tutorial Hours'], str) else row['Tutorial Hours']
                        subject.P = row['Practical Hours'].split('x')[0] if isinstance(row['Practical Hours'], str) else row['Practical Hours']
                        logger.info(f'Updated subject: {subject.subject_code}')
                    
                    rows_processed += 1
                except Exception as row_error:
                    logger.error(f'Error processing row: {row["Subject Code"]}, Error: {str(row_error)}')

            # Commit changes
            db.session.commit()
            logger.info(f'Successfully processed {rows_processed} subjects')
            
            # Clean up
            os.remove(filepath)
            logger.info('Temporary file removed')
            
            return jsonify({
                'success': True,
                'message': f'Successfully processed {rows_processed} subjects for {level} level'
            })

        except Exception as e:
            logger.error(f'Error processing file: {str(e)}')
            db.session.rollback()
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'error': str(e)})

    except Exception as e:
        logger.error(f'General error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})
