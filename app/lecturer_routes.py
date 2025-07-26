import os, logging, pytz
from flask import jsonify, render_template, request, redirect, url_for, session, current_app
from app import app, db
from app.auth import logout_session
from app.database import handle_db_connection
from app.models import Department, Subject, Lecturer, LecturerSubject, ProgramOfficer, Head, Other, ClaimApproval
from app.excel_generator import generate_claim_excel
from flask_bcrypt import Bcrypt
from flask_mail import Message
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from datetime import datetime
bcrypt = Bcrypt()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/lecturerHomepage', methods=['GET', 'POST'])
@handle_db_connection
def lecturerHomepage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    
    levels = db.session.query(LecturerSubject.subject_level).distinct().all()
    lecturerSubjects = LecturerSubject.query.filter_by(lecturer_id=session.get('lecturer_id')).all()
    
    return render_template('lecturerHomepage.html', levels=levels, lecturerSubjects=lecturerSubjects)

@app.route('/get_subjects/<level>')
@handle_db_connection
def get_subjects(level):
    try:
        subjects = db.session.query(LecturerSubject).filter(LecturerSubject.subject_level == level).all()

        return jsonify({
            'success': True,
            'subjects': [{
                'subject_code': s.subject_code,
                'subject_title': s.subject_title
            } for s in subjects]
        })
    except Exception as e:
        error_msg = f"Error getting subjects by level: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg,
            'subjects': []
        })
    
@app.route('/get_subject_info/<code>')
@handle_db_connection
def get_subject_info(code):
    try:
        subject = db.session.query(LecturerSubject).filter(LecturerSubject.subject_code == code).first()
        if subject:
            return jsonify({
                'success': True,
                'start_date': subject.start_date.isoformat() if subject.start_date else '',
                'hourly_rate': subject.hourly_rate
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Subject with code {code} not found.',
                'start_date': '',
                'hourly_rate': None
            })
    except Exception as e:
        error_msg = f"Error getting subject info for {code}: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg,
            'start_date': '',
            'hourly_rate': None
        })

@app.route('/lecturerConversionResult', methods=['POST'])
@handle_db_connection
def lecturerConversionResult():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    try:
        # Debug: Print all form data
        print("Form Data:", request.form)
        
        # Get form data  
        lecturer = Lecturer.query.get(session.get('lecturer_email'))
        name = lecturer.name if lecturer else None
        department_code = lecturer.department_code if lecturer else None

        subject_level = request.form.get('subject_level') 
        subject_code = request.form.get('subject_code')
        hourly_rate = safe_int(request.form.get('hourly_rate'), 0)

        # Helper function to safely convert to int
        def safe_int(value, default=0):
            try:
                return int(value) if value and value.strip() else default
            except (ValueError, TypeError):
                return default

        # Extract claim details from form
        claim_details = []
        i = 1
        while True:
            if not subject_code:
                break            
     
            claim_data = {
                'date': request.form.get(f'date{i}'),
                'lecture_hours': safe_int(request.form.get(f'lectureHours{i}'), 0),
                'tutorial_hours': safe_int(request.form.get(f'tutorialHours{i}'), 0),
                'practical_hours': safe_int(request.form.get(f'practicalHours{i}'), 0),
                'blended_hours': safe_int(request.form.get(f'blendedHours{i}'), 0),
                'remarks': request.form.get(f'remarks{i}'),
            }
            claim_details.append(claim_data)
            i += 1

        if not claim_details:
            return jsonify(success=False, error="No claim details provided"), 400
        
        # program_officer = ProgramOfficer.query.filter_by(department_code=department_code).first()
        # subject = Subject.query.filter_by(subject_code=request.form.get('subjectCode1')).first()
        # head = Head.query.filter_by(head_id=subject.head_id).first()
        department = Department.query.filter_by(department_code=department_code).first()
        # ad = Other.query.filter_by(role="Academic Director").first()
        hr = Other.query.filter_by(role="Human Resources").filter(Other.email != "tingting.eng@newinti.edu.my").first()

        # po_name = program_officer.name if program_officer else 'N/A'
        # head_name = head.name if head else 'N/A'
        dean_name = department.dean_name if department else 'N/A'
        # ad_name = ad.name if ad else 'N/A'
        hr_name = hr.name if hr else 'N/A'
        
        # Generate Excel file
        output_path, sign_col = generate_claim_excel(
            name=name,
            department_code=department_code,
            subject_level=subject_level,
            subject_code=subject_code,
            hourly_rate=hourly_rate,
            claim_details=claim_details,
            # po_name=po_name,
            # head_name=head_name,
            dean_name=dean_name,
            # ad_name=ad_name,
            hr_name=hr_name
        )

        file_name = os.path.basename(output_path)
        file_url, file_id = upload_to_drive(output_path, file_name)

        # Save to database
        approval = ClaimApproval(
            lecturer_name=name,
            department_code=department_code,
            sign_col=sign_col,
            lecturer_email=lecturer.email,
            # po_email=program_officer.email,
            # head_email=head.email if head else None,
            dean_email=department.dean_email if department else None,
            # ad_email=ad.email if ad else None,
            hr_email=hr.email if hr else None,
            file_id=file_id,
            file_name=file_name,
            file_url=file_url,
            status="Pending Acknowledgement by Lecturer",
            last_updated = get_current_datetime()
        )

        db.session.add(approval)
        db.session.commit()

        return jsonify(success=True, file_url=file_url)
        
    except Exception as e:
        logging.error(f"Error in result route: {e}")
        return jsonify(success=False, error=str(e)), 500


@app.route('/lecturerConversionResultPage')
def lecturerConversionResultPage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    
    approval = ClaimApproval.query.filter_by(lecturer_email=session.get('lecturer_email')).order_by(ClaimApproval.approval_id.desc()).first()
    return render_template('lecturerConversionResultPage.html', file_url=approval.file_url)

@app.route('/lecturerApprovalsPage')
@handle_db_connection
def lecturerApprovalsPage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))

    lecturer_email = session.get('lecturer_email')
    approvals = ClaimApproval.query.filter_by(lecturer_email=lecturer_email).all()
    
    return render_template('lecturerApprovalsPage.html', approvals=approvals)

@app.route('/check_claim_status/<int:approval_id>')
def check_claim_status(approval_id):
    approval = ClaimApproval.query.get_or_404(approval_id)
    return jsonify({'status': approval.status})

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

def get_current_datetime():
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now_myt = datetime.now(malaysia_tz)
    return now_myt.strftime('%a, %d %b %y, %I:%M:%S %p')

@app.route('/lecturerProfilePage')
def lecturerProfilePage():
    lecturer_email = session.get('lecturer_email') 

    if not lecturer_email:
        return redirect(url_for('loginPage'))  

    return render_template('lecturerProfilePage.html', lecturer_email=lecturer_email)
    
@app.route('/lecturerLogout')
def lecturerLogout():
    logout_session()
    return redirect(url_for('loginPage'))
