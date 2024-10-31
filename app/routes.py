import os
import logging
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session
from app import app, db
from app.models import Admin, Department, Lecturer, Person, Subject
from app.excel_generator import generate_excel
from werkzeug.utils import secure_filename
from app.auth import login_user, register_user, login_admin, logout_session
from app.subject_routes import *
import pandas as pd
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

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
            return redirect(url_for('admin'))
        else:
            flash('Email already exists.', 'error')
    return render_template('register.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get all departments and lecturers with their details
        departments = Department.query.all()
        lecturers = Lecturer.query.all()
        
        # Debug print
        print("Lecturers:", [{"id": l.lecturer_id, "name": l.lecturer_name, 
                             "designation": l.level, "ic": l.ic_no} for l in lecturers])
        
        return render_template('main.html', 
                             departments=departments,
                             lecturers=lecturers)
    except Exception as e:
        print(f"Error in main route: {str(e)}")
        return str(e), 500

@app.route('/result', methods=['POST'])
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    try:
        # Debug: Print all form data
        print("Form Data:", request.form)
        
        # Get form data
        school_centre = request.form.get('school_centre')
        lecturer_id = request.form.get('lecturer_id')
        
        # Get the actual lecturer name
        if lecturer_id == 'new_lecturer':
            lecturer_name = request.form.get('lecturer_name')
            print(f"New lecturer name: {lecturer_name}")
        else:
            # Get lecturer from database
            lecturer = Lecturer.query.get(lecturer_id)
            lecturer_name = lecturer.lecturer_name if lecturer else None
            print(f"Existing lecturer name: {lecturer_name}")
        
        designation = request.form.get('designation')
        ic_number = request.form.get('ic_number')

        print(f"Final lecturer name being used: {lecturer_name}")

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
                'hourly_rate': int(request.form.get(f'hourlyRate{i}', 60)),
                'lecture_hours': int(request.form.get(f'lectureHours{i}', 0)),
                'tutorial_hours': int(request.form.get(f'tutorialHours{i}', 0)),
                'practical_hours': int(request.form.get(f'practicalHours{i}', 0)),
                'blended_hours': int(request.form.get(f'blendedHours{i}', 1))
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
    subjects = Subject.query.all()
    return render_template('admin.html', departments=departments, 
                         lecturers=lecturers, persons=persons, 
                         subjects=subjects)

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


@app.route('/admin/get-data')
def get_admin_data():
    try:
        data = {
            'subjects': [
                {
                    'subject_code': subj.subject_code,
                    'description': subj.subject_title,
                    'lecture_hours': subj.lecture_hours,
                    'tutorial_hours': subj.tutorial_hours,
                    'practical_hours': subj.practical_hours,
                    'blended_hours': subj.blended_hours,
                    'lecture_weeks': subj.lecture_weeks,
                    'tutorial_weeks': subj.tutorial_weeks,
                    'practical_weeks': subj.practical_weeks,
                    'blended_weeks': subj.blended_weeks,
                }
                for subj in Subject.query.all()
            ],
            # ... other tables data ...
        }
        return jsonify(data)
    except Exception as e:
        print(f"Error in get_admin_data: {str(e)}")  # For debugging
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/get_lecturer_details/<int:lecturer_id>')
def get_lecturer_details(lecturer_id):
    try:
        print(f"Fetching details for lecturer ID: {lecturer_id}")
        lecturer = Lecturer.query.get(lecturer_id)
        
        if not lecturer:
            print(f"Lecturer not found with ID: {lecturer_id}")
            return jsonify({
                'success': False,
                'message': 'Lecturer not found'
            })
        
        response_data = {
            'success': True,
            'lecturer': {
                'lecturer_name': lecturer.lecturer_name,
                'level': lecturer.level,
                'ic_no': lecturer.ic_no
            }
        }
        print(f"Returning lecturer data: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error getting lecturer details: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/<table_type>', methods=['POST'])
def create_record(table_type):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        
        if table_type == 'departments':
            new_record = Department(
                department_code=data['department_code'],
                department_name=data['department_name']
            )
        elif table_type == 'lecturers':
            new_record = Lecturer(
                lecturer_name=data['lecturer_name'],
                level=data['level'],
                department_code=data['department_code'],
                ic_no=data['ic_no']
            )
        elif table_type == 'persons':
            new_record = Person(
                email=data['email'],
                password=generate_password_hash('default_password'),
                department_code=data['department_code']
            )
        elif table_type == 'subjects':
            new_record = Subject(
                subject_code=data['subject_code'],
                subject_title=data['subject_title'],
                subject_level=data['subject_level'],
                lecture_hours=int(data['lecture_hours']),
                tutorial_hours=int(data['tutorial_hours']),
                practical_hours=int(data['practical_hours']),
                blended_hours=int(data['blended_hours']),
                lecture_weeks=int(data['lecture_weeks']),
                tutorial_weeks=int(data['tutorial_weeks']),
                practical_weeks=int(data['practical_weeks']),
                blended_weeks=int(data['blended_weeks'])
            )
        else:
            return jsonify({'success': False, 'error': 'Invalid table type'}), 400

        db.session.add(new_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'New {table_type[:-1]} created successfully'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error creating record: {str(e)}")  # For debugging
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/create_lecturer', methods=['POST'])
def create_lecturer():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.json
        new_lecturer = Lecturer(
            lecturer_name=data['lecturer_name'],
            level=data['level'],
            ic_no=data['ic_no'],
            department_code=data['department_code'],
        )
        
        db.session.add(new_lecturer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'lecturer_id': new_lecturer.lecturer_id,
            'message': 'Lecturer created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/change_password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('new_password')
        
        if not email or not new_password:
            return jsonify({
                'success': False,
                'message': 'Email and new password are required'
            })
            
        user = Person.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            })
            
        # Generate password hash using Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update the password hash in the database
        user.password = hashed_password
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/save_record', methods=['POST'])
def save_record():
    try:
        data = request.get_json()
        table = data.pop('table', None)
        
        if table == 'subjects':
            subject_code = data.get('subject_code')
            subject_levels = data.pop('subject_levels', [])
            
            # Create or update subject using existing logic
            subject = Subject.query.get(subject_code)
            if not subject:
                subject = Subject()
            
            # Update fields using existing logic
            for key, value in data.items():
                if hasattr(subject, key):
                    if key.endswith(('_hours', '_weeks')):
                        value = int(value or 0)
                    setattr(subject, key, value)
            
            db.session.add(subject)
            
            # Handle subject levels
            db.session.execute(
                subject_levels.delete().where(
                    subject_levels.c.subject_code == subject_code
                )
            )
            
            for level in subject_levels:
                db.session.execute(
                    subject_levels.insert().values(
                        subject_code=subject_code,
                        level=level
                    )
                )
            
            db.session.commit()
            return jsonify({'success': True})
            
        # Existing logic for other tables
        # ...

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
