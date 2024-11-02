import os
import logging
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session
from app import app, db
from app.models import Admin, Department, Lecturer, Person, Subject
from app.excel_generator import generate_excel
from app.auth import login_user, register_user, login_admin, logout_session
from app.subject_routes import *
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt
import io

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
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            if register_user(email, password):
                flash('Registration successful!')
            else:
                flash('Email already exists.', 'error')
        else:
            flash('Passwords do not match.', 'error')
    return render_template('register.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Clean up temp folder first
        cleanup_temp_folder()
        
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
            lecturer = Lecturer.query.get(lecturer_id)
            lecturer_name = lecturer.lecturer_name if lecturer else None
            print(f"Existing lecturer name: {lecturer_name}")
        
        designation = request.form.get('designation')
        ic_number = request.form.get('ic_number')

        print(f"Final lecturer name being used: {lecturer_name}")

        # Helper function to safely convert to int
        def safe_int(value, default=0):
            try:
                if not value or value.strip() == '':
                    return default
                return int(value)
            except (ValueError, TypeError):
                return default

        # Extract course details from form
        course_details = []
        i = 1
        while True:
            subject_code = request.form.get(f'subjectCode{i}')
            if not subject_code:
                break
                
            # Debug: Print individual course data
            print(f"Course {i} data:")
            print(f"Lecture weeks: {request.form.get(f'lectureWeeks{i}')}")
            print(f"Tutorial weeks: {request.form.get(f'tutorialWeeks{i}')}")
            print(f"Practical weeks: {request.form.get(f'practicalWeeks{i}')}")
            
            course_data = {
                'program_level': request.form.get(f'programLevel{i}'),
                'subject_code': subject_code,
                'subject_title': request.form.get(f'subjectTitle{i}'),
                'lecture_weeks': safe_int(request.form.get(f'lectureWeeks{i}'), 14),
                'tutorial_weeks': safe_int(request.form.get(f'tutorialWeeks{i}'), 0),
                'practical_weeks': safe_int(request.form.get(f'practicalWeeks{i}'), 0),
                'elearning_weeks': safe_int(request.form.get(f'elearningWeeks{i}'), 14),
                'start_date': request.form.get(f'teachingPeriodStart{i}'),
                'end_date': request.form.get(f'teachingPeriodEnd{i}'),
                'hourly_rate': safe_int(request.form.get(f'hourlyRate{i}'),0),
                'lecture_hours': safe_int(request.form.get(f'lectureHours{i}'), 0),
                'tutorial_hours': safe_int(request.form.get(f'tutorialHours{i}'), 0),
                'practical_hours': safe_int(request.form.get(f'practicalHours{i}'), 0),
                'blended_hours': safe_int(request.form.get(f'blendedHours{i}'), 1)
            }
            course_details.append(course_data)
            i += 1

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
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get filename from request
    filename = request.args.get('filename')
    if not filename:
        flash('No file to download', 'warning')
        return redirect(url_for('result_page'))

    # Construct file path
    file_path = os.path.join(app.root_path, 'temp', filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('File not found', 'error')
        return redirect(url_for('result_page'))

    try:
        # Read the file into memory
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Delete the file immediately after reading
        delete_file(file_path)
        
        # Send the in-memory file data
        return send_file(
            io.BytesIO(file_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Error during download: {e}")
        delete_file(file_path)  # Try to clean up if something went wrong
        flash('Error downloading file', 'error')
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
            return redirect(url_for('admin'))
        else:
            error_message = 'Invalid email or password.'

    return render_template('admin-login.html', error_message=error_message)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Set default tab if none exists
    if 'admin_current_tab' not in session:
        session['admin_current_tab'] = 'departments'
        
    departments = Department.query.all()
    lecturers = Lecturer.query.all()
    persons = Person.query.all()
    subjects = Subject.query.all()
    return render_template('admin.html', 
                         departments=departments, 
                         lecturers=lecturers, 
                         persons=persons, 
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

@app.route('/check_record_exists/<table>/<key>/<value>')
def check_record_exists(table, key, value):
    try:
        exists = False
        if table == 'departments':
            exists = Department.query.filter_by(department_code=value).first() is not None
        elif table == 'lecturers':
            exists = Lecturer.query.filter_by(ic_no=value).first() is not None
        elif table == 'subjects':
            exists = Subject.query.filter_by(subject_code=value).first() is not None
            
        return jsonify({'exists': exists})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table_type>', methods=['POST'])
def create_record(table_type):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        
        # Check for existing records based on primary key
        if table_type == 'departments':
            if Department.query.filter_by(department_code=data['department_code']).first():
                return jsonify({
                    'success': False,
                    'error': f"Department with code '{data['department_code']}' already exists"
                }), 400
                
        elif table_type == 'lecturers':
            if Lecturer.query.filter_by(ic_no=data['ic_no']).first():
                return jsonify({
                    'success': False,
                    'error': f"Lecturer with IC number '{data['ic_no']}' already exists"
                }), 400
                
        elif table_type == 'subjects':
            if Subject.query.filter_by(subject_code=data['subject_code']).first():
                return jsonify({
                    'success': False,
                    'error': f"Subject with code '{data['subject_code']}' already exists"
                }), 400

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
        return jsonify({
            'success': False,
            'error': f"Error creating record: {str(e)}"
        }), 500

@app.route('/check_lecturer_exists/<ic_number>')
def check_lecturer_exists(ic_number):
    try:
        existing_lecturer = Lecturer.query.filter_by(ic_no=ic_number).first()
        if existing_lecturer:
            return jsonify({
                'exists': True,
                'lecturer': {
                    'lecturer_id': existing_lecturer.lecturer_id,
                    'lecturer_name': existing_lecturer.lecturer_name,
                    'level': existing_lecturer.level,
                    'department_code': existing_lecturer.department_code
                }
            })
        return jsonify({'exists': False})
    except Exception as e:
        return jsonify({
            'error': str(e),
            'exists': False
        }), 500

@app.route('/create_lecturer', methods=['POST'])
def create_lecturer():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.json
        
        # Check for existing lecturer with same IC number
        existing_lecturer = Lecturer.query.filter_by(ic_no=data['ic_no']).first()
        if existing_lecturer:
            return jsonify({
                'success': False,
                'message': f"Lecturer with IC number {data['ic_no']} already exists.",
                'existing_lecturer': {
                    'lecturer_id': existing_lecturer.lecturer_id,
                    'lecturer_name': existing_lecturer.lecturer_name
                }
            }), 400
            
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
            'message': f"Error creating new lecturer: {str(e)}"
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

@app.route('/set_admin_tab', methods=['POST'])
def set_admin_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['admin_current_tab'] = data.get('current_tab')
    return jsonify({'success': True})

@app.route('/get_record/<table>/<id>')
def get_record(table, id):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    try:
        # Map table names to models
        table_models = {
            'departments': Department,
            'lecturers': Lecturer,
            'persons': Person,
            'subjects': Subject
        }
        
        # Get the appropriate model
        model = table_models.get(table)
        if not model:
            return jsonify({
                'success': False,
                'message': f'Invalid table: {table}'
            }), 400
            
        # Query the record
        record = model.query.get(id)
        if not record:
            return jsonify({
                'success': False,
                'message': f'Record not found in {table} with id {id}'
            }), 404
            
        # Convert record to dictionary
        record_dict = {}
        for column in model.__table__.columns:
            value = getattr(record, column.name)
            # Convert any non-serializable types to string
            if not isinstance(value, (str, int, float, bool, type(None))):
                value = str(value)
            record_dict[column.name] = value
            
        # Special handling for subjects with levels
        if table == 'subjects':
            # Use the get_levels() method from the Subject model
            record_dict['levels'] = record.get_levels()
            
        logger.info(f"Returning record: {record_dict}")
        return jsonify({
            'success': True,
            'record': record_dict
        })
        
    except Exception as e:
        logger.error(f"Error in get_record: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/get_departments')
def get_departments():
    try:
        departments = Department.query.all()
        return jsonify({
            'success': True,
            'departments': [{'department_code': d.department_code, 
                           'department_name': d.department_name} 
                          for d in departments]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_ic_numbers')
def get_ic_numbers():
    try:
        # Fetch unique IC numbers from your database
        ic_numbers = db.session.query(Lecturer.ic_no).distinct().all()
        return jsonify({
            'success': True,
            'ic_numbers': [ic[0] for ic in ic_numbers]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def delete_file(file_path):
    """Helper function to delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted successfully: {file_path}")
            return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False

def cleanup_temp_folder():
    """Clean up all files in the temp folder"""
    temp_folder = os.path.join(app.root_path, 'temp')
    if os.path.exists(temp_folder):
        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {e}")
