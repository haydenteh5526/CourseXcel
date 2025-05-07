import os, logging
from flask import jsonify, render_template, request, redirect, url_for, session, render_template_string
from app import app, db, mail
from app.models import Admin, Department, Lecturer, ProgramOfficer, Subject
from app.auth import login_admin, logout_session
from app.subjectsList_routes import *
from app.lecturerList_routes import *
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
    return redirect(url_for('adminLoginPage'))

@app.route('/adminLoginPage', methods=['GET', 'POST'])
def adminLoginPage():
    if 'admin_id' in session:
        return redirect(url_for('adminHomepage'))

    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if login_admin(email, password):
            return redirect(url_for('adminHomepage'))
        else:
            error_message = 'Invalid email or password.'
    return render_template('adminLoginPage.html', error_message=error_message)

@app.route('/adminHomepage', methods=['GET', 'POST'])
@handle_db_connection
def adminHomepage():
    if 'admin_id' not in session:
        return redirect(url_for('adminLoginPage'))

    return render_template('adminHomepage.html')

@app.route('/adminSubjectsPage', methods=['GET', 'POST'])
@handle_db_connection
def adminSubjectsPage():
    if 'admin_id' not in session:
        return redirect(url_for('adminLoginPage'))
    
    # Set default tab if none exists
    if 'admin_subjectspage_tab' not in session:
        session['admin_subjectspage_tab'] = 'departments'
        
    departments = Department.query.all()
    subjects = Subject.query.all()
    return render_template('adminSubjectsPage.html', 
                         departments=departments, 
                         subjects=subjects)

@app.route('/set_subjectspage_tab', methods=['POST'])
def set_subjectspage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['subjectspage_tab'] = data.get('subjectspage_current_tab')
    return jsonify({'success': True})

@app.route('/adminUsersPage', methods=['GET', 'POST'])
@handle_db_connection
def adminUsersPage():
    if 'admin_id' not in session:
        return redirect(url_for('adminLoginPage'))
    
    # Set default tab if none exists
    if 'admin_userspage_tab' not in session:
        session['admin_userspage_tab'] = 'lecturers'
        
    lecturers = Lecturer.query.all()
    program_officers = ProgramOfficer.query.all()
    return render_template('adminUsersPage.html', 
                         lecturers=lecturers, 
                         program_officers=program_officers)

@app.route('/set_userspage_tab', methods=['POST'])
def set_userspage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['userspage_tab'] = data.get('userspage_current_tab')
    return jsonify({'success': True})

@app.route('/adminProfilePage')
def adminProfilePage():
    admin_email = session.get('admin_email')  # get from session

    if not admin_email:
        return redirect(url_for('adminLoginPage'))  # if not logged in, go login

    return render_template('adminProfilePage.html', admin_email=admin_email)

@app.route('/adminLogout')
def adminLogout():
    logout_session()
    return redirect(url_for('adminLoginPage'))

@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    role = data.get('role')

    if not email or not role:
        return jsonify({'success': False, 'message': 'Email and role required'})

    # Determine whether admin or program officer and query accordingly
    role_model_map = {
        'program_officer': ProgramOfficer,
        'lecturer': Lecturer,
        'admin': Admin
    }

    model = role_model_map.get(role)
    if not model:
        return jsonify({'success': False, 'message': 'Invalid role'})

    user = model.query.filter_by(email=email).first()
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
    for model in [ProgramOfficer, Lecturer, Admin]:
        user = model.query.filter_by(email=email).first()
        if user:
            break
    else:
        return 'Role could not be identified.', 400

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            return 'Passwords do not match', 400

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        user.password = hashed_password
        db.session.commit()

        return f'''
            <script>
                alert("Password has been reset successfully. You may now close this tab.");
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
                padding: 10px 40px 10px 0;
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

            <button class="reset-btn" type="submit">Confirm</button>
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
                alert('Passwords do not match');
                return false;
            }
            return true;
        }
        </script>
        '''

    return render_template_string(html_content)
    
@app.route('/api/change_password', methods=['POST'])
@handle_db_connection
def change_password():
    try:
        data = request.get_json()
        new_password = data.get('new_password')
        role = data.get('role')

        if not new_password or not role:
            return jsonify({'success': False, 'message': 'New password and role are required'})

        # Map role to model and session key
        role_config = {
            'program_officer': (ProgramOfficer, 'po_email'),
            'lecturer': (Lecturer, 'lecturer_email'),
            'admin': (Admin, 'admin_email')
        }

        if role not in role_config:
            return jsonify({'success': False, 'message': 'Invalid role'})

        Model, session_key = role_config[role]
        email = session.get(session_key)

        if not email:
            return jsonify({'success': False, 'message': 'Not logged in'})

        user = Model.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': f'{role.replace("_", " ").title()} not found'})

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        return jsonify({'success': True, 'message': 'Password changed successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 

@app.route('/api/delete_record/<table_type>', methods=['POST'])
@handle_db_connection
def delete_record(table_type):
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
        return jsonify({'message': 'Record(s) deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_record/<table_type>/<id>', methods=['GET', 'PUT'])
@handle_db_connection
def update_record(table_type, id):
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

@app.route('/api/create_record/<table_type>', methods=['POST'])
@handle_db_connection
def create_record(table_type):
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
            if Lecturer.query.filter_by(email=data['email']).first():
                return jsonify({
                    'success': False,
                    'error': f"Lecturer with email '{data['email']}' already exists"
                }), 400
            
        elif table_type == 'program_officers':
            if ProgramOfficer.query.filter_by(email=data['email']).first():
                return jsonify({
                    'success': False,
                    'error': f"Program Officer with email '{data['ic_no']}' already exists"
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
                email=data['email'],
                password=generate_password_hash('default_password'),
                level=data['level'],
                department_code=data['department_code'],
                ic_no=data['ic_no'],
                hop=data['hop'],
                dean=data['dean']
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
