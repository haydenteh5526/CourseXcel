import io, logging, os, re, time, zipfile
from app import app, db, mail
from app.auth import login_user
from app.database import handle_db_connection
from app.excel_generator import generate_report_excel
from app.models import Admin, ClaimApproval, ClaimAttachment, ClaimReport, Department, Head, Lecturer, LecturerClaim, LecturerSubject, Other, ProgramOfficer, Rate, RequisitionApproval, RequisitionAttachment, RequisitionReport, Subject 
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import current_app, jsonify, redirect, render_template, render_template_string, request, send_file, session, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Message
from io import BytesIO
from itsdangerous import URLSafeTimedSerializer
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from openpyxl import load_workbook
from openpyxl.workbook.protection import WorkbookProtection
from openpyxl.utils.protection import hash_password
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
            # Check Drive quota
            quota = drive_quota_status() 
            limited = quota.get("limited", False)
            over = quota.get("over_threshold", False)

            if limited and over:
                admin_email = session.get("admin_email")
                if admin_email:
                    email_admin_low_storage(admin_email, quota)
            return redirect(url_for('adminHomepage'))

        elif role == 'program_officer':
            return redirect(url_for('poHomepage'))
        elif role == 'lecturer':
            return redirect(url_for('lecturerHomepage'))
        else:
            return render_template('loginPage.html', error_message='Invalid email or password.')

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
    # return render_template('adminHomepage.html')
    
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
        report_type = request.form.get('report_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Choose query and generator based on report type
        if report_type == "requisition":
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
            report_model = RequisitionReport

        elif report_type == "claim":
            q = (
                db.session.query(
                    Department.department_code.label("department_code"),
                    Lecturer.name.label("lecturer_name"),
                    func.count(LecturerClaim.subject_id).label("total_subjects"),
                    func.coalesce(func.sum(LecturerClaim.lecture_hours), 0).label("lecture_hours"),
                    func.coalesce(func.sum(LecturerClaim.tutorial_hours), 0).label("tutorial_hours"),
                    func.coalesce(func.sum(LecturerClaim.practical_hours), 0).label("practical_hours"),
                    func.coalesce(func.sum(LecturerClaim.blended_hours), 0).label("blended_hours"),
                    func.coalesce(func.max(Rate.amount), 0).label("rate"),
                    func.coalesce(func.sum(LecturerClaim.total_cost), 0).label("total_cost"),
                )
                .join(Lecturer, LecturerClaim.lecturer_id == Lecturer.lecturer_id)
                .join(Department, Lecturer.department_id == Department.department_id)
                .join(ClaimApproval, ClaimApproval.approval_id == LecturerClaim.claim_id)
                .outerjoin(Rate, Rate.rate_id == LecturerClaim.rate_id)
                .filter(LecturerClaim.date >= start_date)
                .filter(LecturerClaim.date <= end_date)
                .group_by(Department.department_code, Lecturer.name)
                .order_by(Department.department_code.asc(), Lecturer.name.asc())
            )
            report_model = ClaimReport

        else:
            return jsonify(success=False, error="Invalid report type."), 400

        # Build report_details
        report_details = [
            {
                "department_code": r.department_code or "",
                "lecturer_name": r.lecturer_name or "",
                "total_subjects": int(r.total_subjects or 0),
                "total_lecture_hours": int(r.lecture_hours or 0),
                "total_tutorial_hours": int(r.tutorial_hours or 0),
                "total_practical_hours": int(r.practical_hours or 0),
                "total_blended_hours": int(r.blended_hours or 0),
                "rate": int(r.rate or 0),
                "total_cost": int(r.total_cost or 0),
            }
            for r in q.all()
        ]

        # Check for empty result before generating
        if not report_details:
            return jsonify(success=False, error="No matching data found for the selected date range."), 404

        # Generate Excel
        output_path = generate_report_excel(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            report_details=report_details
        )

        file_name = os.path.basename(output_path)
        file_url, file_id = upload_to_drive(output_path, file_name)

        # Save to correct model
        new_report = report_model(
            file_id=file_id,
            file_name=file_name,
            file_url=file_url,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_report)
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

    report_type = request.args.get("type", "requisition")  # default
    if report_type == "claim":
        latest_report = ClaimReport.query.order_by(ClaimReport.report_id.desc()).first()
    else:
        latest_report = RequisitionReport.query.order_by(RequisitionReport.report_id.desc()).first()

    if not latest_report:
        return "No reports found", 404

    # Keep original link for preview
    view_url = latest_report.file_url

    # Default to original in case it's not Google Sheets
    download_url = view_url

    # Convert Google Sheets preview to downloadable link
    if "docs.google.com" in view_url and "/d/" in view_url:
        file_id = view_url.split("/d/")[1].split("/")[0]
        download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"

    return render_template("reportConversionResultPage.html",
                           view_url=view_url,
                           download_url=download_url,
                           report_type=report_type)

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
    

@app.route('/api/download_files_zip', methods=['POST'])
@handle_db_connection
def download_files_zip():
    """
    Conditions to download:
    1) RequisitionApproval.status == 'Completed'
    2) max(LecturerSubject.end_date) <= today - 4 months
    3) sum(LecturerSubject.total_cost) - sum(LecturerClaim.total_cost where same requisition_id) == 0
    If passes, include into ZIP with structure:

      Requisition_{dd MMM yyyy}/<Department Name>/Approvals/*.xlsx
                                                 /Attachments/*.pdf

      Claim_{dd MMM yyyy}/<Department Name>/Approvals/*.xlsx
                                          /Attachments/*.pdf
    """
    try:
        today = date.today()
        cutoff = today - relativedelta(months=1)
        stamp = format_dd_MMM_yyyy(today)

        # Aggregations
        # LecturerSubject per requisition: max end_date, sum total_cost
        ls_agg = (
            db.session.query(
                LecturerSubject.requisition_id.label('rid'),
                func.max(LecturerSubject.end_date).label('max_end'),
                func.coalesce(func.sum(LecturerSubject.total_cost), 0).label('ls_total')
            )
            .group_by(LecturerSubject.requisition_id)
            .subquery()
        )

        # LecturerClaim per requisition: sum total_cost
        lc_agg = (
            db.session.query(
                LecturerClaim.requisition_id.label('rid'),
                func.coalesce(func.sum(LecturerClaim.total_cost), 0).label('lc_total')
            )
            .group_by(LecturerClaim.requisition_id)
            .subquery()
        )

        # Base query: requisitions that have LS rows (inner join), optional LC (left join)
        q = (
            db.session.query(RequisitionApproval, ls_agg.c.max_end, ls_agg.c.ls_total,
                             func.coalesce(lc_agg.c.lc_total, 0).label('lc_total'))
            .join(ls_agg, ls_agg.c.rid == RequisitionApproval.approval_id)
            .outerjoin(lc_agg, lc_agg.c.rid == RequisitionApproval.approval_id)
            .filter(func.lower(func.coalesce(RequisitionApproval.status, '')) == 'completed')
            .filter(ls_agg.c.max_end <= cutoff)
            .filter((ls_agg.c.ls_total - func.coalesce(lc_agg.c.lc_total, 0)) == 0)
        )

        rows = q.all()
        if not rows:
            return jsonify({'error': 'No requisition or claim files meet the download criteria.'}), 400
        
        mem_zip = BytesIO()
        with zipfile.ZipFile(mem_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            req_root = f"Requisition_{stamp}"
            claim_root = f"Claim_{stamp}"

            for req, max_end, ls_total, lc_total in rows:
                dept = getattr(req, 'department', None)
                dept_name = getattr(dept, 'department_code', None) or getattr(dept, 'department_name', None)
                dept_name = safe_name(dept_name or "Unknown_Department")

                # --- Requisition approval (Google Sheet -> XLSX via Drive API) ---
                if req.file_url and (req.file_name or '').lower().endswith(('.xlsx', '.xlsm', '.xls')):
                    add_drive_approval_xlsx_to_zip(
                        zf,
                        req.file_url,
                        f"{req_root}/{dept_name}/Approvals/{safe_name(req.file_name)}"
                    )

                # --- Requisition attachments (PDF via Drive API) ---
                for att in (req.requisition_attachments or []):
                    if att.attachment_url and (att.attachment_name or '').lower().endswith('.pdf'):
                        add_drive_attachment_pdf_to_zip(
                            zf,
                            att.attachment_url,
                            f"{req_root}/{dept_name}/Attachments/{safe_name(att.attachment_name)}"
                        )

                # --- Related ClaimApprovals via LecturerClaim.claim_id ---
                claim_ids = {
                    cid for (cid,) in db.session.query(LecturerClaim.claim_id)
                                                .filter(LecturerClaim.requisition_id == req.approval_id)
                                                .distinct()
                                                .all()
                }

                if claim_ids:
                    claims = ClaimApproval.query.filter(ClaimApproval.approval_id.in_(list(claim_ids))).all()
                    for ca in claims:
                        # Only include completed claims
                        if (ca.status or '').lower() != 'completed':
                            continue

                        if ca.file_url and (ca.file_name or '').lower().endswith(('.xlsx', '.xlsm', '.xls')):
                            add_drive_approval_xlsx_to_zip(
                                zf,
                                ca.file_url,
                                f"{claim_root}/{dept_name}/Approvals/{safe_name(ca.file_name)}"
                            )
                        for catt in (ca.claim_attachments or []):
                            if catt.attachment_url and (catt.attachment_name or '').lower().endswith('.pdf'):
                                add_drive_attachment_pdf_to_zip(
                                    zf,
                                    catt.attachment_url,
                                    f"{claim_root}/{dept_name}/Attachments/{safe_name(catt.attachment_name)}"
                                )

        mem_zip.seek(0)
        return send_file(
            mem_zip,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"Approvals_and_Attachments_{stamp}.zip"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/cleanup_downloaded_files', methods=['POST'])
@handle_db_connection
def cleanup_downloaded_files():
    try:
        today = date.today()
        cutoff = today - relativedelta(months=4)  

        # Aggregations (same as download_files_zip)
        ls_agg = (
            db.session.query(
                LecturerSubject.requisition_id.label('rid'),
                func.max(LecturerSubject.end_date).label('max_end'),
                func.coalesce(func.sum(LecturerSubject.total_cost), 0).label('ls_total')
            )
            .group_by(LecturerSubject.requisition_id)
            .subquery()
        )

        lc_agg = (
            db.session.query(
                LecturerClaim.requisition_id.label('rid'),
                func.coalesce(func.sum(LecturerClaim.total_cost), 0).label('lc_total')
            )
            .group_by(LecturerClaim.requisition_id)
            .subquery()
        )

        q = (
            db.session.query(RequisitionApproval, ls_agg.c.max_end, ls_agg.c.ls_total,
                             func.coalesce(lc_agg.c.lc_total, 0).label('lc_total'))
            .join(ls_agg, ls_agg.c.rid == RequisitionApproval.approval_id)
            .outerjoin(lc_agg, lc_agg.c.rid == RequisitionApproval.approval_id)
            .filter(func.lower(func.coalesce(RequisitionApproval.status, '')) == 'completed')
            .filter(ls_agg.c.max_end <= cutoff)
            .filter((ls_agg.c.ls_total - func.coalesce(lc_agg.c.lc_total, 0)) == 0)
        )

        rows = q.all()
        if not rows:
            return jsonify({'error': 'No matching records to clean up.'}), 400

        # Track ids for response
        deleted_requisition_ids = []
        deleted_claim_ids = set()

        # Delete Google Drive files first (best-effort)
        for req, max_end, ls_total, lc_total in rows:
            # Requisition approvals (Excel on Drive)
            if req.file_url:
                drive_delete_by_url(req.file_url)

            # Requisition attachments (PDFs on Drive)
            for att in (req.requisition_attachments or []):
                if att.attachment_url:
                    drive_delete_by_url(att.attachment_url)

            # Related claims (only Completed)
            claim_ids = {
                cid for (cid,) in db.session.query(LecturerClaim.claim_id)
                                            .filter(LecturerClaim.requisition_id == req.approval_id)
                                            .distinct()
                                            .all()
            }
            if claim_ids:
                claims = ClaimApproval.query.filter(ClaimApproval.approval_id.in_(list(claim_ids))).all()
                for ca in claims:
                    if (ca.status or '').lower() != 'completed':
                        continue
                    if ca.file_url:
                        drive_delete_by_url(ca.file_url)
                    for catt in (ca.claim_attachments or []):
                        if catt.attachment_url:
                            drive_delete_by_url(catt.attachment_url)
                    deleted_claim_ids.add(ca.approval_id)

        # Delete DB rows (claims first, then requisitions)
        if deleted_claim_ids:
            ClaimApproval.query.filter(ClaimApproval.approval_id.in_(list(deleted_claim_ids))).delete(synchronize_session=False)

        for req, *_ in rows:
            deleted_requisition_ids.append(req.approval_id)
        RequisitionApproval.query.filter(RequisitionApproval.approval_id.in_(deleted_requisition_ids)).delete(synchronize_session=False)

        db.session.commit()
        return jsonify({
            'success': True,
            'deleted_requisition_ids': deleted_requisition_ids,
            'deleted_claim_ids': sorted(list(deleted_claim_ids))
        })
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
    
def get_drive_service():
    SERVICE_ACCOUNT_FILE = '/home/TomazHayden/coursexcel-459515-3d151d92b61f.json'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def bytes_human(n: int) -> str:
    for unit in ['B','KB','MB','GB','TB','PB']:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} EB"

def drive_get_quota():
    """Return (usage, limit, usage_in_drive, usage_in_trash) as ints. Limit may be 0/None for unlimited."""
    svc = get_drive_service()
    about = svc.about().get(fields="storageQuota").execute()
    q = about.get("storageQuota", {})
    usage = int(q.get("usage") or 0)
    limit = int(q.get("limit") or 0)  # 0 or missing can mean 'unlimited' for some orgs
    usage_in_drive = int(q.get("usageInDrive") or 0)
    usage_in_trash = int(q.get("usageInDriveTrash") or 0)
    return usage, limit, usage_in_drive, usage_in_trash

def drive_quota_status(threshold: float = None):
    """Return dict with status and message. Cache briefly in session to avoid frequent API calls."""
    threshold = threshold or float(current_app.config.get("DRIVE_QUOTA_THRESHOLD", 0.85))
    cache_secs = int(current_app.config.get("DRIVE_QUOTA_CACHE_SECONDS", 600))
    now = int(time.time())

    # lightweight per-session cache
    cache = session.get("_drive_quota_cache")
    if cache and (now - cache.get("ts", 0) < cache_secs):
        return cache["data"]

    usage, limit, usage_in_drive, usage_in_trash = drive_get_quota()
    if not limit:  # unlimited or unknown limit
        data = {
            "limited": False,
            "percent": None,
            "usage": usage,
            "limit": limit,
            "message": "Drive storage appears unlimited (no limit reported)."
        }
    else:
        pct = usage / limit
        data = {
            "limited": True,
            "percent": pct,
            "usage": usage,
            "limit": limit,
            "message": f"Using {bytes_human(usage)} of {bytes_human(limit)} ({pct*100:.1f}%).",
            "over_threshold": pct >= threshold
        }

    session["_drive_quota_cache"] = {"ts": now, "data": data}
    return data

def email_admin_low_storage(admin_email: str, quota: dict):
    if not admin_email:
        return
    mail = current_app.extensions.get("mail")
    if not mail:
        return
    subject = "CourseXcel: Google Drive storage nearing capacity"
    body = (
        f"Dear Admin,\n\n"
        f"Our Google Drive storage is nearing capacity. {quota['message']}\n\n"
        "Please take the following actions:\n"
        f"• Generate reports: {url_for('adminReportPage', _external=True)}\n"
        f"• Export and clear completed approvals: {url_for('adminHomepage', _external=True)}\n\n"
        "Thank you,\n"
        "The CourseXcel Team"
    )
    
    msg = Message(subject=subject, recipients=[admin_email], body=body)
    mail.send(msg)

def safe_name(s: str) -> str: 
    if not s: 
        return "Unknown" 
    return re.sub(r'[\\/:*?"<>|\r\n]+', '_', s).strip() 

def format_dd_MMM_yyyy(d: date) -> str: 
    return d.strftime('%d %b %Y')

# Extract fileId from common URLs
def extract_drive_file_id(url: str) -> str | None:
    # Sheets url
    m = re.search(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if m: return m.group(1)
    # Drive file url
    m = re.search(r"drive\.google\.com/file/d/([a-zA-Z0-9-_]+)", url)
    if m: return m.group(1)
    # open?id=<ID>
    m = re.search(r"[?&]id=([a-zA-Z0-9-_]+)", url)
    if m: return m.group(1)
    return None

# Get metadata (name, mimeType)
def drive_get_metadata(file_id: str) -> dict:
    svc = get_drive_service()
    return svc.files().get(fileId=file_id, fields="id, name, mimeType").execute()

# Download (export for Google-native, get_media for binary) into memory
def drive_download_bytes(file_id: str, export_mime: str | None = None) -> bytes:
    svc = get_drive_service()
    if export_mime:
        request = svc.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        request = svc.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        # (optional) you can inspect status.progress() here if you want
    fh.seek(0)
    return fh.read()

# Write approvals (Sheets -> XLSX) into ZIP by URL
APP_SHEET_PW = os.environ.get("EXCEL_SHEET_PW", "approval_excel_sheet_password")
APP_BOOK_PW  = os.environ.get("EXCEL_BOOK_PW", "approval_workbook_password")

def add_drive_approval_xlsx_to_zip(zf, url: str, arcname: str):
    file_id = extract_drive_file_id(url)
    if not file_id:
        return
    meta = drive_get_metadata(file_id)

    # Export Google Sheet → XLSX
    if meta.get("mimeType") == "application/vnd.google-apps.spreadsheet":
        data = drive_download_bytes(
            file_id,
            export_mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        # If it isn’t a Google Sheet, try direct bytes (already an Excel file in Drive)
        data = drive_download_bytes(file_id)

    # Protect the workbook/sheets
    data = protect_excel_bytes(data, sheet_password=APP_SHEET_PW, workbook_password=APP_BOOK_PW)

    # Ensure .xlsx extension
    if not arcname.lower().endswith(".xlsx"):
        base, _, _ = arcname.rpartition(".")
        arcname = (base or arcname) + ".xlsx"

    zf.writestr(arcname, data)

# Write attachments (PDF) into ZIP by URL
def add_drive_attachment_pdf_to_zip(zf, url: str, arcname: str):
    file_id = extract_drive_file_id(url)
    if not file_id:
        return
    meta = drive_get_metadata(file_id)
    mt = meta.get("mimeType", "")

    # Google-native → export to PDF
    if mt.startswith("application/vnd.google-apps."):
        data = drive_download_bytes(file_id, export_mime="application/pdf")
        # Ensure .pdf extension
        if not arcname.lower().endswith(".pdf"):
            base, _, _ = arcname.rpartition(".")
            arcname = (base or arcname) + ".pdf"
        zf.writestr(arcname, data)
        return

    # Non-native binary (likely already a PDF on Drive) → get_media
    data = drive_download_bytes(file_id, export_mime=None)
    # Keep arcname; optionally force .pdf if you know all should be PDF
    zf.writestr(arcname, data)

def protect_excel_bytes(xlsx_bytes: bytes,
                        sheet_password: str | None = None,
                        workbook_password: str | None = None) -> bytes:
    """
    - Locks every sheet (no edits).
    - Optionally sets sheet and workbook structure passwords.
    - Returns protected XLSX bytes.
    """
    bio = io.BytesIO(xlsx_bytes)
    wb = load_workbook(bio, data_only=False)

    for ws in wb.worksheets:
        # Lock the sheet and disallow edits
        ws.protection.sheet = True
        ws.protection.enable()
        ws.protection.formatCells = False
        ws.protection.formatColumns = False
        ws.protection.formatRows = False
        ws.protection.insertColumns = False
        ws.protection.insertRows = False
        ws.protection.insertHyperlinks = False
        ws.protection.deleteColumns = False
        ws.protection.deleteRows = False
        ws.protection.sort = False
        ws.protection.autoFilter = False
        ws.protection.pivotTables = False
        ws.protection.objects = True
        ws.protection.scenarios = True
        # Allow selecting cells so users can view content comfortably
        ws.protection.selectLockedCells = True
        ws.protection.selectUnlockedCells = True

        if sheet_password:
            # Sets hashed password inside the file (no prompt unless unprotecting)
            ws.protection.set_password(sheet_password)

    # Protect workbook structure (e.g., adding/removing sheets)
    wb.security = WorkbookProtection(lockStructure=True, lockWindows=False)
    if workbook_password:
        wb.security.workbookPassword = hash_password(workbook_password)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.read()

def drive_delete_by_url(url: str) -> bool:
    file_id = extract_drive_file_id(url)
    if not file_id:
        return False
    try:
        svc = get_drive_service()
        svc.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        logging.error(f"Drive delete failed for {url}: {e}")
        return False

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