import os
import logging
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session
from app import app, db, bcrypt
from app.models import Admin, Department, Lecturer, Person, Program, Subject
from app.excel_generator import generate_excel
from werkzeug.utils import secure_filename
from app.auth import login_user, register_user, login_admin, logout_session

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configurations
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

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
    # Remove admins from the query
    departments = Department.query.all()
    lecturers = Lecturer.query.all()
    persons = Person.query.all()
    programs = Program.query.all()
    subjects = Subject.query.all()
    return render_template('admin.html', departments=departments, 
                         lecturers=lecturers, persons=persons, 
                         programs=programs, subjects=subjects)

@app.route('/logout')
def logout():
    logout_session()
    return redirect(url_for('login'))

@app.route('/api/delete/<table_type>', methods=['POST'])
def delete_records(table_type):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    data = request.get_json()
    ids = data.get('ids', [])

    try:
        if table_type == 'admins':
            Admin.query.filter(Admin.admin_id.in_(ids)).delete()
        elif table_type == 'departments':
            Department.query.filter(Department.department_code.in_(ids)).delete()
        elif table_type == 'lecturers':
            Lecturer.query.filter(Lecturer.lecturer_id.in_(ids)).delete()
        elif table_type == 'persons':
            Person.query.filter(Person.user_id.in_(ids)).delete()
        elif table_type == 'programs':
            Program.query.filter(Program.program_code.in_(ids)).delete()
        elif table_type == 'subjects':
            Subject.query.filter(Subject.subject_code.in_(ids)).delete()
        
        db.session.commit()
        return jsonify({'message': 'Records deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table_type>/<id>', methods=['GET', 'PUT'])
def handle_record(table_type, id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    model_map = {
        'admins': Admin,
        'departments': Department,
        'lecturers': Lecturer,
        'persons': Person,
        'programs': Program,
        'subjects': Subject
    }

    model = model_map.get(table_type)
    if not model:
        return jsonify({'error': 'Invalid table type'}), 400

    if request.method == 'GET':
        record = model.query.get(id)
        if record:
            return jsonify({column.name: getattr(record, column.name) 
                          for column in model.__table__.columns})
        return jsonify({'error': 'Record not found'}), 404

    elif request.method == 'PUT':
        try:
            record = model.query.get(id)
            if not record:
                return jsonify({'error': 'Record not found'}), 404

            data = request.get_json()
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)

            db.session.commit()
            return jsonify({'success': True, 'message': 'Record updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
