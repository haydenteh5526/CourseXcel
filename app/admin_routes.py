import logging, os
from app import app, db, mail
from app.auth import login_user
from app.database import handle_db_connection
from app.excel_generator import generate_report_excel
from app.models import Admin, ClaimApproval, ClaimAttachment, ClaimReport, Department, Head, Lecturer, LecturerClaim, LecturerSubject, Other, ProgramOfficer, Rate, RequisitionApproval, RequisitionAttachment, RequisitionReport, Subject 
from flask import jsonify, render_template, request, redirect, url_for, session, render_template_string
from flask_bcrypt import Bcrypt
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from sqlalchemy import desc, func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
bcrypt = Bcrypt()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurations
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return redirect(url_for('loginPage'))

@app.route('/loginPage', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        role = login_user(email, password)

        if role == 'admin':
            return redirect(url_for('adminHomepage'))
        elif role == 'program_officer':
            return redirect(url_for('poHomepage'))
        elif role == 'lecturer':
            return redirect(url_for('lecturerHomepage'))
        else:
            error_message = 'Invalid email or password.'
            return render_template('loginPage.html', error_message=error_message)

    return render_template('loginPage.html')

@app.route('/adminHomepage', methods=['GET', 'POST'])
@handle_db_connection
def adminHomepage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))

    drive_service = get_drive_service()

    if request.method == 'POST':  # To delete files
        file_ids = request.form.getlist('file_ids')  # Collect file IDs from the form
        for file_id in file_ids:
            try:
                drive_service.files().delete(fileId=file_id).execute()  # Delete the file by ID
            except Exception as e:
                print(f"Error deleting file with ID {file_id}: {e}")

    # Get the list of files to show
    results = drive_service.files().list(
        pageSize=20,
        fields="files(id, name, webViewLink)"
    ).execute()

    files = results.get('files', [])

    about = drive_service.about().get(fields="storageQuota").execute()
    storage_quota = about.get('storageQuota', {})

    # Convert bytes to GB for readability
    def bytes_to_gb(byte_str):
        return round(int(byte_str) / (1024**3), 2)

    used_gb = bytes_to_gb(storage_quota.get('usage', '0'))
    total_gb = bytes_to_gb(storage_quota.get('limit', '0'))

    # Pass to template
    return render_template('adminHomepage.html', files=files, used_gb=used_gb, total_gb=total_gb)
    
@app.route('/adminSubjectsPage', methods=['GET', 'POST'])
@handle_db_connection
def adminSubjectsPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'adminSubjectsPage_currentTab' not in session:
        session['adminSubjectsPage_currentTab'] = 'subjects'
        
    subjects = Subject.query.options(joinedload(Subject.head)).order_by(Subject.subject_code.asc()).all() 
    departments = Department.query.order_by(Department.department_name.asc()).all() 
    rates = Rate.query.order_by(Rate.amount.asc()).all() 

    return render_template('adminSubjectsPage.html', 
                           subjects=subjects,
                           departments=departments,
                           rates=rates)

@app.route('/set_adminSubjectsPage_tab', methods=['POST'])
def set_adminSubjectsPage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['adminSubjectsPage_currentTab'] = data.get('adminSubjectsPage_currentTab')
    return jsonify({'success': True})

@app.route('/adminUsersPage', methods=['GET', 'POST'])
@handle_db_connection
def adminUsersPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'adminUsersPage_currentTab' not in session:
        session['adminUsersPage_currentTab'] = 'lecturers'

    lecturers = Lecturer.query.order_by(Lecturer.name.asc()).all()        
    heads = Head.query.order_by(Head.name.asc()).all()
    programOfficers = ProgramOfficer.query.order_by(ProgramOfficer.name.asc()).all()
    others = Other.query.order_by(Other.name.asc()).all()

    return render_template('adminUsersPage.html', 
                           lecturers=lecturers, 
                           heads=heads,
                           programOfficers=programOfficers,
                           others=others)

@app.route('/set_adminUsersPage_tab', methods=['POST'])
def set_adminUsersPage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['adminUsersPage_currentTab'] = data.get('adminUsersPage_currentTab')
    return jsonify({'success': True})

@app.route('/adminApprovalsPage', methods=['GET', 'POST'])
@handle_db_connection
def adminApprovalsPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'adminApprovalsPage_currentTab' not in session:
        session['adminApprovalsPage_currentTab'] = 'requisitionApprovals'

    departments = Department.query.all()
    lecturers = Lecturer.query.order_by(Lecturer.name).all()

    requisitionApprovals = RequisitionApproval.query.order_by(RequisitionApproval.approval_id.desc()).all()
    requisitionAttachments = RequisitionAttachment.query.order_by(RequisitionAttachment.requisition_id.desc()).all()
    claimApprovals = ClaimApproval.query.order_by(ClaimApproval.approval_id.desc()).all()
    claimAttachments = ClaimAttachment.query.order_by(ClaimAttachment.claim_id.desc()).all()

    # Get all LecturerSubject records linked to completed requisitions
    subjects = (
        db.session.query(
            LecturerSubject,
            Lecturer,
            Subject.subject_code,
            Subject.subject_title,
            Subject.subject_level
        )
        .join(Lecturer, LecturerSubject.lecturer_id == Lecturer.lecturer_id)
        .join(Subject, LecturerSubject.subject_id == Subject.subject_id)
        .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
        .filter(RequisitionApproval.status == 'Completed')
        .order_by(desc(RequisitionApproval.approval_id))
        .all()
    )

    claimDetails = []
    for ls, lecturer, code, title, level in subjects:
        # Sum all claimed hours for this lecturer/subject
        claimed = (
            db.session.query(
                func.coalesce(func.sum(LecturerClaim.lecture_hours), 0),
                func.coalesce(func.sum(LecturerClaim.tutorial_hours), 0),
                func.coalesce(func.sum(LecturerClaim.practical_hours), 0),
                func.coalesce(func.sum(LecturerClaim.blended_hours), 0)
            )
            .filter_by(lecturer_id=lecturer.lecturer_id, subject_id=ls.subject_id)
            .first()
        )

        remaining = {
            'lecturer': lecturer,
            'subject_code': code,
            'subject_title': title,
            'subject_level': level,
            'start_date': ls.start_date,
            'end_date': ls.end_date,
            'hourly_rate': ls.rate.amount if ls.rate else 0,
            'lecture_hours': ls.total_lecture_hours - claimed[0],
            'tutorial_hours': ls.total_tutorial_hours - claimed[1],
            'practical_hours': ls.total_practical_hours - claimed[2],
            'blended_hours': ls.total_blended_hours - claimed[3],
        }
        claimDetails.append(remaining)

    return render_template('adminApprovalsPage.html', 
                           departments=departments,
                           lecturers=lecturers,
                           requisitionApprovals=requisitionApprovals,
                           requisitionAttachments=requisitionAttachments,
                           claimApprovals=claimApprovals,
                           claimAttachments=claimAttachments,
                           claimDetails=claimDetails)

@app.route('/set_adminApprovalsPage_tab', methods=['POST'])
def set_adminApprovalsPage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['adminApprovalsPage_currentTab'] = data.get('adminApprovalsPage_currentTab')
    return jsonify({'success': True})

@app.route('/adminReportPage')
@handle_db_connection
def adminReportPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'adminReportsPage_currentTab' not in session:
        session['adminReportsPage_currentTab'] = 'requisitionReports'
    
    departments = Department.query.all()
    requisitionReports = RequisitionReport.query.order_by(RequisitionReport.report_id.desc()).all()
    claimReports = ClaimReport.query.order_by(ClaimReport.report_id.desc()).all()

    return render_template('adminReportPage.html', 
                           departments=departments,
                           requisitionReports=requisitionReports,
                           claimReports=claimReports)

@app.route('/set_adminReportsPage_tab', methods=['POST'])
def set_adminReportsPage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['adminReportsPage_currentTab'] = data.get('adminReportsPage_currentTab')
    return jsonify({'success': True})

@app.route('/reportConversionResult', methods=['POST'])
@handle_db_connection
def reportConversionResult():
    if 'admin_id' not in session:
        return jsonify(success=False, error="Session expired. Please log in again."), 401
    
    try:
        print("Form Data:", request.form)
        report_type = request.form.get('report_type')

        if report_type == "requisition":
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date') 

            q = (
                db.session.query(
                    Department.department_code.label("department_code"),
                    Lecturer.name.label("lecturer_name"),
                    func.count(LecturerSubject.subject_id).label("total_subjects"),
                    func.coalesce(func.sum(LecturerSubject.total_lecture_hours), 0).label("lecture_hours"),
                    func.coalesce(func.sum(LecturerSubject.total_tutorial_hours), 0).label("tutorial_hours"),
                    func.coalesce(func.sum(LecturerSubject.total_practical_hours), 0).label("practical_hours"),
                    func.coalesce(func.sum(LecturerSubject.total_blended_hours), 0).label("blended_hours"),
                    func.coalesce(func.max(Rate.amount), 0).label("rate"),
                    func.coalesce(func.sum(LecturerSubject.total_cost), 0).label("total_cost"),
                )
                .join(Lecturer, Lecturer.department_id == Department.department_id)
                .join(LecturerSubject, LecturerSubject.lecturer_id == Lecturer.lecturer_id)
                .join(RequisitionApproval, RequisitionApproval.approval_id == LecturerSubject.requisition_id)
                .outerjoin(Rate, Rate.rate_id == LecturerSubject.rate_id)
                .filter(LecturerSubject.start_date >= start_date)
                .filter(LecturerSubject.end_date <= end_date)
                .group_by(Department.department_code, Lecturer.name)
                .order_by(Department.department_code.asc(), Lecturer.name.asc())
            )

            report_details = []
            for r in q.all():
                report_details.append({
                    "department_code": r.department_code or "",
                    "lecturer_name": r.lecturer_name or "",
                    "total_subjects": int(r.total_subjects or 0),
                    "total_lecture_hours": int(r.lecture_hours or 0),
                    "total_tutorial_hours": int(r.tutorial_hours or 0),
                    "total_practical_hours": int(r.practical_hours or 0),
                    "total_blended_hours": int(r.blended_hours or 0),
                    "rate": int(r.rate or 0),
                    "total_cost": int(r.total_cost or 0),
                })

            # Generate Excel
            output_path = generate_report_excel(
                start_date=start_date,
                end_date=end_date,
                report_details=report_details
            )

            file_name = os.path.basename(output_path)
            file_url, file_id = upload_to_drive(output_path, file_name)

            # Save to RequisitionReport table
            requisition_report = RequisitionReport(
                file_id=file_id,
                file_name=file_name,
                file_url=file_url,
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(requisition_report)
            db.session.commit()

        return jsonify(success=True, file_url=file_url)
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in result route: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/reportConversionResultPage')
def reportConversionResultPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))

    requisitionReport = RequisitionReport.query.order_by(RequisitionReport.report_id.desc()).first()

    # Keep original link for preview
    view_url = requisitionReport.file_url

    # Default to original in case it's not Google Sheets
    download_url = view_url

    # Convert Google Sheets preview to downloadable link
    if "docs.google.com" in view_url and "/d/" in view_url:
        file_id = view_url.split("/d/")[1].split("/")[0]
        download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"

    return render_template("reportConversionResultPage.html", 
                           view_url=view_url,
                           download_url=download_url
                           )
    
@app.route('/adminProfilePage')
def adminProfilePage():
    admin_email = session.get('admin_email')

    if not admin_email:
        return redirect(url_for('loginPage'))  

    return render_template('adminProfilePage.html', admin_email=admin_email)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('loginPage'))

@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'success': False, 'message': 'Email is required.'})

    # Check if user exists in any model
    user = Admin.query.filter_by(email=email).first() \
        or ProgramOfficer.query.filter_by(email=email).first() \
        or Lecturer.query.filter_by(email=email).first()

    if not user:
        return jsonify({'success': False, 'message': 'User not found. Please ensure you insert the correct email.'}), 404

    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps(email, salt='reset-password')
    reset_url = url_for('reset_password', token=token, _external=True)

    msg = Message(f'CourseXcel - Password Reset Request', recipients=[email])
    msg.body = f'''Hi,

We received a request to reset your password for your CourseXcel account.

To reset your password, click the link below:
{reset_url}

If you did not request this, you can safely ignore this email.

Thank you,
The CourseXcel Team
'''
    mail.send(msg)

    return jsonify({'success': True, 'message': 'Reset link sent to your email.'})

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='reset-password', max_age=3600)
    except Exception:
        return 'The reset link is invalid or has expired.', 400

    # Improved role detection logic
    for model in [Admin, ProgramOfficer, Lecturer]:
        user = model.query.filter_by(email=email).first()
        if user:
            break
    else:
        return 'Role could not be identified.', 400

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            return 'Passwords do not match.', 400

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        user.password = hashed_password
        db.session.commit()

        return f'''
            <script>
                alert("Password has been reset successfully. You may now close this tab and try logging in with your new password.");
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
            return jsonify({'success': False, 'message': 'New password and role are required.'})

        # Map role to model and session key
        role_config = {
            'admin': (Admin, 'admin_email'),
            'program_officer': (ProgramOfficer, 'po_email'),
            'lecturer': (Lecturer, 'lecturer_email')
        }

        if role not in role_config:
            return jsonify({'success': False, 'message': 'Invalid role.'})

        Model, session_key = role_config[role]
        email = session.get(session_key)

        if not email:
            return jsonify({'success': False, 'message': 'Not logged in.'})

        user = Model.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': f'{role.replace("_", " ").title()} not found.'})

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        return jsonify({'success': True, 'message': 'Password changed successfully.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}) 
    
@app.route('/api/download_files_clear_storage', methods=['POST'])
@handle_db_connection
def download_files_clear_storage():
    try:
       
        return jsonify({'message': ''})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/check_record_exists/<table>', methods=['GET'])
@handle_db_connection
def check_record_exists(table):
    field = request.args.get('field')
    value = request.args.get('value')

    # Map tables to models and allowed fields (whitelist to avoid injection)
    TABLES = {
        'subjects': (Subject, {'subject_code'}),
        'departments': (Department, {'department_code', 'dean_email'}),
        'lecturers': (Lecturer, {'ic_no', 'email'}),
        'heads': (Head, {'email'}),
        'programOfficers': (ProgramOfficer, {'email'}),
        'others': (Other, {'email'}),
    }

    if table not in TABLES:
        return jsonify({'error': 'Unknown table'}), 400

    model, allowed_fields = TABLES[table]

    if not field or field not in allowed_fields:
        return jsonify({'error': 'Invalid or missing field'}), 400
    if value is None:
        return jsonify({'error': 'Missing value'}), 400

    try:
        exists = model.query.filter(getattr(model, field) == value).first() is not None
        return jsonify({'exists': exists})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create_record/<table_type>', methods=['POST'])
@handle_db_connection
def create_record(table_type):
    try:
        data = request.form.to_dict()  

        # ======= Check for Existing Records ========
        if table_type == 'subjects':
            if Subject.query.filter_by(subject_code=data['subject_code']).first():
                return jsonify({'success': False, 'error': f"Subject with code '{data['subject_code']}' already exists."}), 400
    
        elif table_type == 'rates':
            if Rate.query.filter_by(amount=data['amount']).first():
                return jsonify({'success': False, 'error': f"Rate with amount '{data['amount']}' already exists."}), 400
            
        elif table_type == 'departments':
            if Department.query.filter_by(department_code=data['department_code']).first():
                return jsonify({'success': False, 'error': f"Department with code '{data['department_code']}' already exists."}), 400
            
            if Department.query.filter_by(dean_email=data['dean_email']).first():
                return jsonify({'success': False, 'error': f"Department with dean '{data['dean_email']}' already exists."}), 400
                
        elif table_type == 'lecturers':
            # Check if any lecturer already has the same IC number after decrypting it
            ic_no = data['ic_no']  # Get the IC number from the request
            
            lecturer = Lecturer.query.all()  # Retrieve all lecturers from the database
            for existing_lecturer in lecturer:
                decrypted_ic = existing_lecturer.get_ic_no()  # Decrypt the stored IC number
                if decrypted_ic == ic_no:
                    return jsonify({'success': False, 'error': f"Lecturer with IC number '{ic_no}' already exists."}), 400

            # Check if lecturer exists with the same email
            if Lecturer.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'error': f"Lecturer with email '{data['email']}' already exists."}), 400

        elif table_type == 'heads':
            if Head.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'error': f"Head with email '{data['email']}' already exists."}), 400
            
        elif table_type == 'programOfficers':
            if ProgramOfficer.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'error': f"Program Officer with email '{data['email']}' already exists."}), 400  
            
        elif table_type == 'others':
            if Other.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'error': f"Entry with email '{data['email']}' already exists."}), 400  
            
        # ======= Record Creation ========
        if table_type == 'subjects':
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
                blended_weeks=int(data['blended_weeks']),
                head_id=data['head_id'],
            )

        elif table_type == 'rates':
            new_record = Rate(
                amount=int(data['amount']),
                status=(None if (s := data.get('status')) in (None, '') else bool(int(s)))
            )
       
        elif table_type == 'departments':
            new_record = Department(
                department_code=data['department_code'],
                department_name=data['department_name'],
                dean_name=data['dean_name'],
                dean_email=data['dean_email']
            )

        elif table_type == 'lecturers':
            new_record = Lecturer(
                name=data['name'],
                email=data['email'],
                password=bcrypt.generate_password_hash('default_password').decode('utf-8'),
                level=data['level'],
                department_id=data['department_id']
            )
            new_record.set_ic_no(data['ic_no'])

        elif table_type == 'heads':
            new_record = Head(
                name=data['name'],
                email=data['email'],
                level=data['level'],
                department_id=data['department_id']
            )

        elif table_type == 'programOfficers':
            new_record = ProgramOfficer(
                name=data['name'],
                email=data['email'],
                password = bcrypt.generate_password_hash('default_password').decode('utf-8'),
                department_id=data['department_id']
            )

        elif table_type == 'others':
            new_record = Other(
                name=data['name'],
                email=data['email'],
                role=data['role']
            )

        else:
            return jsonify({'success': False, 'error': 'Invalid table type'}), 400

        db.session.add(new_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'New {table_type[:-1]} created successfully.'
        })

    except IntegrityError as e:
        db.session.rollback()
        error_msg = str(e.orig)

        if "foreign key constraint fails" in error_msg:
            return jsonify({
                'success': False,
                'error': "One of the linked values is invalid. Please make sure related data (like Department or Head) exists before creating this record."
            }), 400

        elif "Duplicate entry" in error_msg:
            return jsonify({
                'success': False,
                'error': "This record already exists. Please check for duplicate entries."
            }), 400

        return jsonify({
            'success': False,
            'error': "A database integrity error occurred. Please check your input and try again."
        }), 400

    except Exception as e:
        db.session.rollback()
        print(f"Error creating record: {str(e)}")
        return jsonify({
            'success': False,
            'error': "An unexpected error occurred while creating the record. Please try again."
        }), 500

@app.route('/api/update_record/<table_type>/<id>', methods=['PUT'])
@handle_db_connection
def update_record(table_type, id):
    model_map = {
        'subjects': Subject,
        'departments': Department,
        'lecturers': Lecturer,
        'heads': Head,
        'programOfficers': ProgramOfficer,
        'others': Other
    }

    model = model_map.get(table_type)
    if not model:
        return jsonify({'error': 'Invalid table type'}), 400
    
    try:
        record = model.query.get(id)
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        data = request.form.to_dict()  

        # Apply updates for other fields
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        # Encrypt IC Number before updating
        if 'ic_no' in data:
            record.set_ic_no(data['ic_no'])  # Encrypt the IC number before saving

        db.session.commit()
        return jsonify({'success': True, 'message': 'Record updated successfully.'})
    
    except Exception as e:
        app.logger.error(f"Error updating record: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        
@app.route('/api/delete_record/<table_type>', methods=['POST'])
@handle_db_connection
def delete_record(table_type):
    data = request.get_json()
    ids = data.get('ids', [])

    try:
        if table_type == 'subjects':
            Subject.query.filter(Subject.subject_id.in_(ids)).delete()

        elif table_type == 'departments':
            Department.query.filter(Department.department_id.in_(ids)).delete()
    
        elif table_type == 'lecturers':
            Lecturer.query.filter(Lecturer.lecturer_id.in_(ids)).delete()

        elif table_type == 'heads':
            Head.query.filter(Head.head_id.in_(ids)).delete()

        elif table_type == 'programOfficers':
            ProgramOfficer.query.filter(ProgramOfficer.po_id.in_(ids)).delete()
        
        elif table_type == 'others':
            Other.query.filter(Other.other_id.in_(ids)).delete()

        db.session.commit()
        return jsonify({'message': 'Record(s) deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/change_rate_status/<int:id>', methods=['PUT'])
def change_rate_status(id):
    try:
        rate = Rate.query.get_or_404(id)
        # Toggle; if status is None, treat as False
        rate.status = not bool(rate.status)
        db.session.commit()
        return jsonify({'success': True, 'status': bool(rate.status), 'message': 'Rate status updated successfully.'})
    except Exception as e:
        app.logger.error(f"Error changing rate status: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
def get_drive_service():
    SERVICE_ACCOUNT_FILE = '/home/TomazHayden/coursexcel-459515-3d151d92b61f.json'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, file_name):
    try:
        service = get_drive_service()

        file_metadata = {
            'name': file_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet'  # Convert to Google Sheets
        }

        media = MediaFileUpload(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        # Make file publicly accessible
        service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'},
        ).execute()

        file_id = file.get('id')
        file_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"

        return file_url, file_id

    except Exception as e:
        logging.error(f"Failed to upload to Google Drive: {e}")
        raise

@app.route('/get_record/<table>/<id>')
@handle_db_connection
def get_record(table, id):   
    try:
        # Map table names to models
        table_models = {
            'subjects': Subject,
            'rates': Rate,
            'departments': Department,
            'lecturers': Lecturer,
            'programOfficers': ProgramOfficer,
            'heads': Head,
            'others': Other
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

            # If the table is 'lecturers', use the get_ic_no() to decrypt IC number
            if table == 'lecturers' and column.name == 'ic_no' and value:
                value = record.get_ic_no()
            
            # Convert any non-serializable types to string
            if not isinstance(value, (str, int, float, bool, type(None))):
                value = str(value)
            record_dict[column.name] = value
            
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
            'departments': [{'department_id': d.department_id, 
                            'department_code': d.department_code, 
                           'department_name': d.department_name} 
                          for d in departments]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_heads')
@handle_db_connection
def get_heads():
    try:
        heads = Head.query.all()
        return jsonify({
            'success': True,
            'heads': [{'head_id': h.head_id,
                             'name': h.name} 
                          for h in heads]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})