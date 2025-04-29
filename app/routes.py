import os, logging, io
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session, render_template_string
from app import app, db, mail
from app.models import Admin, Department, Lecturer, ProgramOfficer, Subject
from app.excel_generator import generate_excel
from app.auth import login_po, register_po, login_admin, logout_session
from app.subject_routes import *
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from app.database import handle_db_connection
bcrypt = Bcrypt()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurations
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('po_login'))

@app.route('/po_login', methods=['GET', 'POST'])
def po_login():
    if 'po_id' in session:
        return redirect(url_for('po_main'))

    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if login_po(email, password):
            return redirect(url_for('po_main'))
        else:
            error_message = 'Invalid email or password.'
    return render_template('po_login.html', error_message=error_message)

@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    role = data.get('role')

    if not email or not role:
        return jsonify({'success': False, 'message': 'Email and role required'})

    # Determine whether admin or program officer and query accordingly
    if role == 'admin':
        user = Admin.query.filter_by(email=email).first()
    elif role == 'program_officer':
        user = ProgramOfficer.query.filter_by(email=email).first()
    else:
        return jsonify({'success': False, 'message': 'Invalid role'})

    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps(email, salt='reset-password')
    reset_url = url_for('reset_password', token=token, _external=True)

    msg = Message(f'CourseXcel - Password Reset Request', recipients=[email])
    msg.body = f'''Hi,

We received a request to reset your password for your CourseXcel account.

To reset your password, please click the link below:
{reset_url}

If you did not request this change, please ignore this email.

Thank you,
The CourseXcel Team
'''
    mail.send(msg)

    return jsonify({'success': True, 'message': 'Reset link sent to your email'})

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='reset-password', max_age=3600)
    except Exception:
        return 'The reset link is invalid or has expired.', 400

    # Improved role detection logic
    user = Admin.query.filter_by(email=email).first()
    if user:
        role = 'admin'
    else:
        user = ProgramOfficer.query.filter_by(email=email).first()
        if user:
            role = 'program_officer'
        else:
            return 'User role could not be identified.', 400

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            return 'Passwords do not match.', 400

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        user.password = hashed_password
        db.session.commit()

        login_url = "/admin_login" if role == 'admin' else "/po_login"
        return f'''
            <script>
                alert("Password has been reset successfully.");
                window.location.href = "{login_url}";
            </script>
        '''

    html_content = '''
        <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                padding: 2rem;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background-color: #f9f9f9;
            }
            form {
                width: 100%;
                max-width: 400px;
                background: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h2 {
                text-align: center;
                margin-bottom: 30px;
            }
            .input-group {
                position: relative;
                margin-bottom: 25px;
            }
            .input-group input {
                width: 100%;
                padding: 10px 40px 10px 10px;
                font-size: 16px;
                border: none;
                border-bottom: 1px solid #ddd;
                background: transparent;
                outline: none;
            }
            .input-group label {
                position: absolute;
                top: -10px;
                left: 0;
                font-size: 12px;
                color: #777;
            }
            .input-group button {
                position: absolute;
                right: 0;
                top: 50%;
                transform: translateY(-50%);
                border: none;
                background: none;
                cursor: pointer;
                font-size: 16px;
            }
            .reset-btn {
                width: 100%;
                padding: 12px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                cursor: pointer;
                display: block;
                margin-top: 10px;
            }
        </style>

        <form method="post" onsubmit="return validatePasswords()">
            <h2>Reset Password</h2>

            <div class="input-group">
                <input type="password" name="new_password" id="new_password" required>
                <label for="new_password">New Password</label>
                <button type="button" onclick="togglePassword('new_password', this)">
                    <i class="fas fa-eye"></i>
                </button>
            </div>    

            <div class="input-group">
                <input type="password" name="confirm_password" id="confirm_password" required>
                <label for="confirm_password">Confirm Password</label>
                <button type="button" onclick="togglePassword('confirm_password', this)">
                    <i class="fas fa-eye"></i>
                </button>
            </div>    

            <button class="reset-btn" type="submit">Reset Password</button>
        </form>

        <script>
        function togglePassword(inputId, button) {
            var input = document.getElementById(inputId);
            var icon = button.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        }

        function validatePasswords() {
            const newPassword = document.getElementById('new_password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            if (newPassword !== confirmPassword) {
                alert('Passwords do not match!');
                return false;
            }
            return true;
        }
        </script>
        '''

    return render_template_string(html_content)

@app.route('/po_main', methods=['GET', 'POST'])
@handle_db_connection
def po_main():
    if 'po_id' not in session:
        return redirect(url_for('po_login'))
    
    try:
        # Clean up temp folder first
        cleanup_temp_folder()
        
        # Get all departments and lecturers with their details
        departments = Department.query.all()
        lecturers = Lecturer.query.all()
        
        return render_template('po_main.html', 
                             departments=departments,
                             lecturers=lecturers)
    except Exception as e:
        print(f"Error in main route: {str(e)}")
        return str(e), 500
    
@app.route('/po_profile')
def po_profile():
    po_email = session.get('po_email')  # get from session

    if not po_email:
        return redirect(url_for('po_login'))  # if not logged in, go login

    return render_template('po_profile.html', po_email=po_email)

@app.route('/result', methods=['POST'])
@handle_db_connection
def result():
    if 'po_id' not in session:
        return redirect(url_for('po_login'))
    try:
        # Debug: Print all form data
        print("Form Data:", request.form)
        
        # Get form data
        school_centre = request.form.get('school_centre')
        lecturer_id = request.form.get('lecturer_id')
        
        # Get the actual lecturer name
        if lecturer_id == 'new_lecturer':
            name = request.form.get('name')
            print(f"New lecturer name: {name}")
        else:
            lecturer = Lecturer.query.get(lecturer_id)
            name = lecturer.name if lecturer else None
            print(f"Existing lecturer name: {name}")
        
        designation = request.form.get('designation')
        ic_number = request.form.get('ic_number')

        print(f"Final lecturer name being used: {name}")

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
            name=name,
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
    if 'po_id' not in session:
        return redirect(url_for('po_login'))
    filename = request.args.get('filename')
    return render_template('result.html', filename=filename)

@app.route('/download')
def download():
    if 'po_id' not in session:
        return redirect(url_for('po_login'))

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

@app.route('/api/change_po_password', methods=['POST'])
@handle_db_connection
def change_po_password():
    try:
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return jsonify({
                'success': False,
                'message': 'New password is required'
            })
        
        # Get the current po from session
        po_email = session.get('po_email') 
        
        if not po_email:
            return jsonify({
                'success': False,
                'message': 'Not logged in'
            })
        
        po = ProgramOfficer.query.filter_by(email=po_email).first()
        if not po:
            return jsonify({
                'success': False,
                'message': 'PO not found'
            })
        
        # Hash the new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update password
        po.password = hashed_password
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
    
@app.route('/po_logout')
def po_logout():
    logout_session()
    return redirect(url_for('po_login'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error_message = None
    if 'admin_id' in session:
        return redirect(url_for('admin_main'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if login_admin(email, password):
            return redirect(url_for('admin_main'))
        else:
            error_message = 'Invalid email or password.'

    return render_template('admin_login.html', error_message=error_message)

@app.route('/admin_main', methods=['GET', 'POST'])
@handle_db_connection
def admin_main():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Set default tab if none exists
    if 'admin_current_tab' not in session:
        session['admin_current_tab'] = 'departments'
        
    departments = Department.query.all()
    lecturers = Lecturer.query.all()
    program_officers = ProgramOfficer.query.all()
    subjects = Subject.query.all()
    return render_template('admin_main.html', 
                         departments=departments, 
                         lecturers=lecturers, 
                         program_officers=program_officers, 
                         subjects=subjects)

@app.route('/set_admin_tab', methods=['POST'])
def set_admin_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['admin_current_tab'] = data.get('current_tab')
    return jsonify({'success': True})

@app.route('/admin_logout')
def admin_logout():
    logout_session()
    return redirect(url_for('admin_login'))

@app.route('/api/delete/<table_type>', methods=['POST'])
@handle_db_connection
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
        elif table_type == 'program_officers':
            ProgramOfficer.query.filter(ProgramOfficer.po_id.in_(ids)).delete()
        elif table_type == 'subjects':
            Subject.query.filter(Subject.subject_code.in_(ids)).delete()
        
        db.session.commit()
        return jsonify({'message': 'Records deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/<table_type>/<id>', methods=['GET', 'PUT'])
@handle_db_connection
def handle_record(table_type, id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    model_map = {
        'admins': Admin,
        'departments': Department,
        'lecturers': Lecturer,
        'program_officers': ProgramOfficer,
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

@app.route('/get_lecturer_details/<int:lecturer_id>')
@handle_db_connection
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
                'name': lecturer.name,
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
@handle_db_connection
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
@handle_db_connection
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
                name=data['name'],
                level=data['level'],
                department_code=data['department_code'],
                ic_no=data['ic_no']
            )
        elif table_type == 'program_officers':
            new_record = ProgramOfficer(
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
@handle_db_connection
def check_lecturer_exists(ic_number):
    try:
        existing_lecturer = Lecturer.query.filter_by(ic_no=ic_number).first()
        if existing_lecturer:
            return jsonify({
                'exists': True,
                'lecturer': {
                    'lecturer_id': existing_lecturer.lecturer_id,
                    'name': existing_lecturer.name,
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
@handle_db_connection
def create_lecturer():
    if 'po_id' not in session:
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
                    'name': existing_lecturer.name
                }
            }), 400
            
        new_lecturer = Lecturer(
            name=data['name'],
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

@app.route('/save_record', methods=['POST'])
@handle_db_connection
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

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_record/<table>/<id>')
@handle_db_connection
def get_record(table, id):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    try:
        # Map table names to models
        table_models = {
            'departments': Department,
            'lecturers': Lecturer,
            'program_officers': ProgramOfficer,
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
@handle_db_connection
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

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            if register_po(email, password):
                flash('Registration successful!')
            else:
                flash('Email already exists.', 'error')
        else:
            flash('Passwords do not match.', 'error')
    return render_template('admin_register.html')

@app.route('/admin_profile')
def admin_profile():
    admin_email = session.get('admin_email')  # get from session

    if not admin_email:
        return redirect(url_for('admin_login'))  # if not logged in, go login

    return render_template('admin_profile.html', admin_email=admin_email)

@app.route('/api/change_admin_password', methods=['POST'])
@handle_db_connection
def change_admin_password():
    try:
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return jsonify({
                'success': False,
                'message': 'New password is required'
            })
        
        # Get the current admin from session
        admin_email = session.get('admin_email') 
        
        if not admin_email:
            return jsonify({
                'success': False,
                'message': 'Not logged in'
            })
        
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            return jsonify({
                'success': False,
                'message': 'Admin not found'
            })
        
        # Hash the new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update password
        admin.password = hashed_password
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
