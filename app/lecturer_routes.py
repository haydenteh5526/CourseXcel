import os, io, logging, pytz, base64
from openpyxl.drawing.image import Image as ExcelImage
from flask import jsonify, render_template, request, redirect, url_for, session, current_app, render_template_string, abort
from app import app, db, mail
from app.auth import logout_session
from app.database import handle_db_connection
from app.models import Admin, Department, Subject, Lecturer, LecturerSubject, ProgramOfficer, Head, Other, ClaimApproval, LecturerClaim
from app.excel_generator import generate_claim_excel
from flask_bcrypt import Bcrypt
from flask_mail import Message
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from datetime import datetime
from io import BytesIO
from PIL import Image
from openpyxl import load_workbook
bcrypt = Bcrypt()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/lecturerHomepage', methods=['GET', 'POST'])
@handle_db_connection
def lecturerHomepage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Get distinct subject levels for this lecturer
    levels = (
        db.session.query(Subject.subject_level)
        .join(LecturerSubject, Subject.subject_id == LecturerSubject.subject_id)
        .filter(LecturerSubject.lecturer_id == session.get('lecturer_id'))
        .distinct()
        .all()
    )
    levels = [level[0] for level in levels] # Flatten the result from [(level1,), (level2,)] to [level1, level2]

    lecturerSubjects = LecturerSubject.query.filter_by(lecturer_id=session.get('lecturer_id')).all()
    
    return render_template('lecturerHomepage.html', levels=levels, lecturerSubjects=lecturerSubjects)

@app.route('/get_subjects/<level>')
@handle_db_connection
def get_subjects(level):
    try:
        # Proper join between LecturerSubject and Subject, and filter on Subject.subject_level
        subjects = (
            db.session.query(LecturerSubject)
            .join(Subject)
            .filter(Subject.subject_level == level)
            .all()
        )

        return jsonify({
            'success': True,
            'subjects': [{
                'subject_code': s.subject.subject_code,
                'subject_title': s.subject.subject_title
            } for s in subjects if s.subject]  # Ensure subject is not None
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
        subject = db.session.query(LecturerSubject).join(LecturerSubject.subject).filter(Subject.subject_code == code).first()
        
        if subject:
            return jsonify({
                'success': True,
                'start_date': subject.start_date.isoformat() if subject.start_date else '',
                'end_date': subject.end_date.isoformat() if subject.end_date else '',
                'total_lecture_hours': subject.total_lecture_hours,
                'total_tutorial_hours': subject.total_lecture_hours,
                'total_practical_hours': subject.total_lecture_hours,
                'total_blended_hours': subject.total_lecture_hours,
                'hourly_rate': subject.hourly_rate
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Subject with code {code} not found.',
                'start_date': '',
                'end_date': '',
                'total_lecture_hours': None,
                'total_tutorial_hours': None,
                'total_practical_hours': None,
                'total_blended_hours': None,
                'hourly_rate': None
            })
    except Exception as e:
        error_msg = f"Error getting subject info for {code}: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg,
            'start_date': '',
            'end_date': '',
            'total_lecture_hours': None,
            'total_tutorial_hours': None,
            'total_practical_hours': None,
            'total_blended_hours': None,
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
        department_code = lecturer.department.department_code if lecturer else None

        subject_level = request.form.get('subject_level') 
        subject_code = request.form.get('subject_code')
        total_lecture_hours = safe_int(request.form.get('totalLectureHours'), 0)
        total_tutorial_hours = safe_int(request.form.get('totalTutorialHours'), 0)
        total_practical_hours = safe_int(request.form.get('totalPracticalHours'), 0)
        total_blended_hours = safe_int(request.form.get('totalBlendedHours'), 0)
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
        
        claimed_lecture = sum(item['lecture_hours'] for item in claim_details)
        claimed_tutorial = sum(item['tutorial_hours'] for item in claim_details)
        claimed_practical = sum(item['practical_hours'] for item in claim_details)
        claimed_blended = sum(item['blended_hours'] for item in claim_details)

        remaining_lecture = total_lecture_hours - claimed_lecture
        remaining_tutorial = total_tutorial_hours - claimed_tutorial
        remaining_practical = total_practical_hours - claimed_practical
        remaining_blended = total_blended_hours - claimed_blended
       
        # Get department from lecturer
        department = Department.query.filter_by(department_code=department_code).first()
        department_id = department.department_id if department else None

        po = ProgramOfficer.query.filter_by(department_id=department_id).first()
        subject = Subject.query.filter_by(subject_code=request.form.get('subjectCode1')).first()
        head = Head.query.filter_by(head_id=subject.head_id).first()
        ad = Other.query.filter_by(role="Academic Director").first()
        hr = Other.query.filter_by(role="Human Resources").filter(Other.email != "tingting.eng@newinti.edu.my").first()

        po_name = po.name if po else 'N/A'
        head_name = head.name if head else 'N/A'
        dean_name = department.dean_name if department else 'N/A'
        ad_name = ad.name if ad else 'N/A'
        hr_name = hr.name if hr else 'N/A'

        # Generate Excel file
        output_path, sign_col = generate_claim_excel(
            name=name,
            department_code=department_code,
            subject_level=subject_level,
            subject_code=subject_code,
            hourly_rate=hourly_rate,
            claim_details=claim_details,
            remaining_lecture=remaining_lecture,
            remaining_tutorial=remaining_tutorial,
            remaining_practical=remaining_practical,
            remaining_blended=remaining_blended,
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
            department_id=department_id,
            lecturer_id=session.get('lecturer_id'),
            po_id=po.po_id if po else None,
            sign_col=sign_col,
            file_id=file_id,
            file_name=file_name,
            file_url=file_url,
            status="Pending Acknowledgement by Lecturer",
            last_updated = get_current_datetime()
        )

        db.session.add(approval)
        db.session.flush()  # Get approval_id before committing
        
        approval_id = approval.approval_id

        # Add lecturer_claim entries with claim_id
        for claim_data in claim_details:
            subject_code = claim_data['subject_code']
            subject = Subject.query.filter_by(subject_code=subject_code).first()

            hourly_rate = safe_int(claim_data.get('hourly_rate'), 0)
            total_cost = hourly_rate * (
                total_lecture_hours +
                total_tutorial_hours +
                total_practical_hours +
                total_blended_hours
            )

            lecturer_claim = LecturerClaim(
                lecturer_id=session.get('lecturer_id'),
                claim_id=approval_id,
                subject_id=subject.subject_id if subject else None,
                date=claim_data['end_date'],
                lecture_hours=claimed_lecture,
                tutorial_hours=claimed_tutorial,
                practical_hours=claimed_practical,
                blended_hours=claimed_blended,
                hourly_rate=hourly_rate,
                total_cost=total_cost
            )
            db.session.add(lecturer_claim)

        db.session.commit()

        return jsonify(success=True, file_url=file_url)
        
    except Exception as e:
        logging.error(f"Error in result route: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/lecturerConversionResultPage')
def lecturerConversionResultPage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    
    approval = ClaimApproval.query.filter_by(lecturer_id=session.get('lecturer_id')).order_by(ClaimApproval.approval_id.desc()).first()
    return render_template('lecturerConversionResultPage.html', file_url=approval.file_url)

@app.route('/lecturerApprovalsPage')
@handle_db_connection
def lecturerApprovalsPage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))

    approvals = ClaimApproval.query.filter_by(lecturer_id=session.get('lecturer_id')).all()
    return render_template('lecturerApprovalsPage.html', approvals=approvals)

@app.route('/check_claim_status/<int:approval_id>')
def check_claim_status(approval_id):
    approval = ClaimApproval.query.get_or_404(approval_id)
    return jsonify({'status': approval.status})

@app.route('/api/lecturer_review_claim/<approval_id>', methods=['POST'])
@handle_db_connection
def lecturer_review_claim(approval_id):
    try:
        data = request.get_json()
        signature_data = data.get("image")

        if not signature_data or "," not in signature_data:
            return jsonify(success=False, error="Invalid image data format")

        # Fetch approval record
        approval = ClaimApproval.query.get(approval_id)
        if not approval:
            return jsonify(success=False, error="Approval record not found")

        # Process signature and upload updated file
        process_signature_and_upload(approval, signature_data, "A")

        # Update status after signature inserted
        approval.status = "Pending Acknowledgement by PO"
        approval.last_updated = get_current_datetime()
        db.session.commit()

        try:
            notify_approval(approval, approval.program_officer.email if approval.program_officer else None, "po_review_claim", "Program Officer")
        except Exception as e:
            logging.error(f"Failed to notify PO: {e}")    

        return jsonify(success=True)

    except Exception as e:
        logging.error(f"Error uploading signature: {e}")
        return jsonify(success=False, error=str(e)), 500
    
@app.route('/api/po_review_claim/<approval_id>', methods=['GET', 'POST'])
def po_review_claim(approval_id):
    approval = ClaimApproval.query.get(approval_id)
    if not approval:
        abort(404, description="Approval record not found")

    voided_response = is_already_voided(approval)
    if voided_response:
        return voided_response

    if request.method == 'GET':
        if is_already_reviewed(approval, ["Rejected by PO", "Pending Acknowledgement by Dean / HOS"]):
            return render_template_string(f"""
                <h2 style="text-align: center; color: red;">This request has already been reviewed.</h2>
                <p style="text-align: center;">Status: {approval.status}</p>
            """)
        return render_template("reviewClaimApprovalRequest.html", approval=approval)

    # POST logic
    action = request.form.get('action')
    if action == 'approve':
        try:
            process_signature_and_upload(approval, request.form.get('signature_data'), "C")
            approval.status = "Pending Acknowledgement by Dean / HOS"
            approval.last_updated = get_current_datetime()
            db.session.commit()

            try:
                notify_approval(approval, approval.department.dean_email if approval.department else None, "dean_review_claim", "Dean / HOS")
            except Exception as e:
                logging.error(f"Failed to notify Dean: {e}")

            return '''<script>alert("Request approved successfully. You may now close this window.")</script>'''
        except Exception as e:
            return str(e), 500

    elif action == 'reject':
        reason = request.form.get('reject_reason')
        if not reason:
            return "Rejection reason required", 400
        
        approval.status = f"Rejected by PO: {reason.strip()}"
        approval.last_updated = get_current_datetime()

        # Delete linked lecturer_claim entries
        LecturerClaim.query.filter_by(claim_id=approval.approval_id).delete()

        db.session.commit()

        try:
            send_rejection_email("PO", approval, reason.strip())
        except Exception as e:
            logging.error(f"Failed to send rejection email: {e}")

        return '''<script>alert("Request rejected successfully. You may now close this window.")</script>'''
    
    return "Invalid action", 400

@app.route('/api/dean_review_claim/<approval_id>', methods=['GET', 'POST'])
def dean_review_claim(approval_id):
    approval = ClaimApproval.query.get(approval_id)
    if not approval:
        abort(404, description="Approval record not found")

    voided_response = is_already_voided(approval)
    if voided_response:
        return voided_response

    if request.method == 'GET':
        if is_already_reviewed(approval, ["Rejected by Dean / HOS", "Pending Acknowledgement by HR"]):
            return render_template_string(f"""
                <h2 style="text-align: center; color: red;">This request has already been reviewed.</h2>
                <p style="text-align: center;">Status: {approval.status}</p>
            """)
        return render_template("reviewClaimApprovalRequest.html", approval=approval)
    
    # POST logic
    action = request.form.get('action')
    if action == 'approve':
        try:
            process_signature_and_upload(approval, request.form.get('signature_data'), "C")
            approval.status = "Pending Acknowledgement by HR"
            approval.last_updated = get_current_datetime()
            db.session.commit()

            hr = Other.query.filter(Other.role == "Human Resources", Other.email != "tingting.eng@newinti.edu.my").first()

            try:
                notify_approval(approval, hr.email if hr else None, "hr_review_claim", "HR")
            except Exception as e:
                logging.error(f"Failed to notify HR: {e}")

            return '''<script>alert("Request approved successfully. You may now close this window.")</script>'''
        except Exception as e:
            return str(e), 500

    elif action == 'reject':
        reason = request.form.get('reject_reason')
        if not reason:
            return "Rejection reason required", 400
        
        approval.status = f"Rejected by Dean / HOS: {reason.strip()}"
        approval.last_updated = get_current_datetime()

        # Delete linked lecturer_claim entries
        LecturerClaim.query.filter_by(claim_id=approval.approval_id).delete()

        db.session.commit()

        try:
            send_rejection_email("Dean", approval, reason.strip())
        except Exception as e:
            logging.error(f"Failed to send rejection email: {e}")

        return '''<script>alert("Request rejected successfully. You may now close this window.")</script>'''
    
    return "Invalid action", 400

@app.route('/api/hr_review_claim/<approval_id>', methods=['GET', 'POST'])
def hr_review_claim(approval_id):
    approval = ClaimApproval.query.get(approval_id)
    if not approval:
        abort(404, description="Approval record not found")

    voided_response = is_already_voided(approval)
    if voided_response:
        return voided_response

    if request.method == 'GET':
        if is_already_reviewed(approval, ["Rejected by HR", "Completed"]):
            return render_template_string(f"""
                <h2 style="text-align: center; color: red;">This request has already been reviewed.</h2>
                <p style="text-align: center;">Status: {approval.status}</p>
            """)
        return render_template("reviewClaimApprovalRequest.html", approval=approval)

    action = request.form.get('action')
    if action == 'approve':
        try:
            process_signature_and_upload(approval, request.form.get('signature_data'), "F")
            approval.status = "Completed"
            approval.last_updated = get_current_datetime()
            db.session.commit()

            try:
                subject = "Part-time Lecturer Claim Approval Request Completed"
                body = (
                    f"Dear All,\n\n"
                    f"The part-time lecturer claim request has been fully approved by all parties.\n\n"
                    f"Please click the link below to access the final approved file:\n"
                    f"{approval.file_url}\n\n"
                    "Thank you for your cooperation.\n\n"
                    "Best regards,\n"
                    "The CourseXcel Team"
                )
                
                # Get final HR and admin
                final_hr_email = "tingting.eng@newinti.edu.my"
                admin = Admin.query.filter_by(admin_id=1).first()

                # Base recipients from related models
                recipients = [
                    approval.program_officer.email if approval.program_officer else None,
                    approval.department.dean_email if approval.department else None,
                ]

                # Get "Other" roles
                ad = Other.query.filter_by(role="Academic Director").first()
                hr = Other.query.filter_by(role="Human Resources").filter(Other.email != final_hr_email).first()

                # Append AD and first HR if exists
                if ad and ad.email:
                    recipients.append(ad.email)
                if hr and hr.email:
                    recipients.append(hr.email)

                # Append final HR and admin
                recipients.append(final_hr_email)
                if admin and admin.email:
                    recipients.append(admin.email)

                # Filter out any Nones or duplicates
                recipients = list(filter(None, set(recipients)))

                send_email(recipients, subject, body)
            except Exception as e:
                logging.error(f"Failed to notify All: {e}")

            return '''<script>alert("Request approved successfully. You may now close this window.")</script>'''
        except Exception as e:
            return str(e), 500

    elif action == 'reject':
        reason = request.form.get('reject_reason')
        if not reason:
            return "Rejection reason required", 400
        
        approval.status = f"Rejected by HR: {reason.strip()}"
        approval.last_updated = get_current_datetime()

        # Delete linked lecturer_claim entries
        LecturerClaim.query.filter_by(claim_id=approval.approval_id).delete()
 
        db.session.commit()

        try:
            send_rejection_email("HR", approval, reason.strip())
        except Exception as e:
            logging.error(f"Failed to send rejection email: {e}")
        
        return '''<script>alert("Request rejected successfully. You may now close this window.")</script>'''
    
    return "Invalid action", 400

@app.route('/api/void_claim/<approval_id>', methods=['POST'])
@handle_db_connection
def void_claim(approval_id):
    try:
        data = request.get_json()
        reason = data.get("reason", "").strip()

        if not reason:
            return jsonify(success=False, error="Reason for voiding is required."), 400

        approval = ClaimApproval.query.get(approval_id)
        if not approval:
            return jsonify(success=False, error="Approval record not found."), 404

        current_status = approval.status

        # Allow voiding only at specific stages
        if current_status in [
            "Pending Acknowledgement by PO",
            "Pending Acknowledgement by Dean / HOS",
            "Pending Acknowledgement by HR"
        ]:
            approval.status = f"Voided: {reason}"

            # Delete related LecturerClaim records
            LecturerClaim.query.filter_by(claim_id=approval_id).delete(synchronize_session=False)
        else:
            return jsonify(success=False, error="Request cannot be voided at this stage."), 400

        approval.last_updated = get_current_datetime()
        db.session.commit()

        hr = Other.query.filter(Other.role == "Human Resources", Other.email != "tingting.eng@newinti.edu.my").first()

        # Determine recipients based on current stage
        recipients = []
        if current_status == "Pending Acknowledgement by PO":
            recipients = [approval.program_officer.email]
        elif current_status == "Pending Acknowledgement by Dean / HOS":
            recipients = [approval.program_officer.email, approval.department.dean_email]
        elif current_status == "Pending Acknowledgement by HR":
            recipients = [approval.program_officer.email, approval.department.dean_email, hr.email]

        recipients = list(set(filter(None, recipients)))  # Remove duplicates and None

        # Send notification emails
        subject = "Part-time Lecturer Claim Request Voided"
        body = (
            f"Dear All,\n\n"
            f"The part-time lecturer claim request has been voided by the Requester.\n"
            f"Reason: {reason}\n\n"
            f"Please review the file here:\n{approval.file_url}\n"
            "Please do not take any further action on this request.\n\n"
            "Thank you,\n"
            "The CourseXcel Team"
        )

        if recipients:
            success = send_email(recipients, subject, body)
            if not success:
                logging.error(f"Failed to send void notification email to: {recipients}")
        
        return jsonify(success=True)

    except Exception as e:
        logging.error(f"Error voiding claim: {e}")
        return jsonify(success=False, error="Internal server error."), 500

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

def download_from_drive(file_id):
    drive_service = get_drive_service()

    request = drive_service.files().export_media(fileId=file_id,
        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "temp")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    local_path = os.path.join(output_folder, f"{file_id}.xlsx")

    fh = io.FileIO(local_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.close()
    return local_path

def get_current_datetime():
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now_myt = datetime.now(malaysia_tz)
    return now_myt.strftime('%a, %d %b %y, %I:%M:%S %p')
          
def save_signature_image(signature_data, approval_id, temp_folder):
    try:
        header, encoded = signature_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(binary_data))
        temp_image_path = os.path.join(temp_folder, f"signature_{approval_id}.png")
        image.save(temp_image_path)
        return temp_image_path
    except Exception as e:
        logging.error(f"Signature decoding error: {e}")
        return None

def insert_signature_and_date(local_excel_path, signature_path, cell_prefix, row, updated_path):
    wb = load_workbook(local_excel_path)
    ws = wb.active

    # Insert signature
    sign_cell = f"{cell_prefix}{row}"
    signature_img = ExcelImage(signature_path)
    signature_img.width = 100
    signature_img.height = 30
    ws.add_image(signature_img, sign_cell)

    # Insert date
    date_cell = f"{cell_prefix}{row + 4}"
    malaysia_time = datetime.now(pytz.timezone('Asia/Kuala_Lumpur'))
    ws[date_cell] = f"Date: {malaysia_time.strftime('%d/%m/%Y')}"

    wb.save(updated_path)

def process_signature_and_upload(approval, signature_data, col_letter):
    temp_folder = os.path.join("temp")
    os.makedirs(temp_folder, exist_ok=True)

    temp_image_path = save_signature_image(signature_data, approval.approval_id, temp_folder)
    if not temp_image_path:
        raise ValueError("Invalid signature image data")

    local_excel_path = download_from_drive(approval.file_id)
    updated_excel_path = os.path.join(temp_folder, approval.file_name)

    try:
        insert_signature_and_date(local_excel_path, temp_image_path, col_letter, approval.sign_col, updated_excel_path)
        new_file_url, new_file_id = upload_to_drive(updated_excel_path, approval.file_name)

        # Delete old versions from Drive except the new one
        drive_service = get_drive_service()

        # Delete old file by stored file ID (approval.file_id) if different from new_file_id
        if approval.file_id and approval.file_id != new_file_id:
            try:
                drive_service.files().delete(fileId=approval.file_id).execute()
                logging.info(f"Deleted old file with ID {approval.file_id}")
            except Exception as e:
                logging.warning(f"Failed to delete old file {approval.file_id}: {e}")
                
        # Update DB record
        approval.file_url = new_file_url
        approval.file_id = new_file_id
        approval.last_updated = get_current_datetime()
        db.session.commit()

    finally:
        # Clean up temp files safely even if an exception occurs
        for path in [temp_image_path, local_excel_path, updated_excel_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logging.warning(f"Failed to remove temp file {path}: {e}")

def is_already_voided(approval):
    if "Voided" in approval.status:
        return render_template_string(f"""
            <h2 style="text-align: center; color: red;">This request has already been voided.</h2>
            <p style="text-align: center;">Status: {approval.status}</p>
        """)
    return None

def is_already_reviewed(approval, expected_statuses):
    return any(status in approval.status for status in expected_statuses)

def send_email(recipients, subject, body):
    try:
        # Ensure recipients is always a list
        if isinstance(recipients, str):
            recipients = [recipients]

        msg = Message(subject, recipients=recipients, body=body)
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")
        return False
    
def notify_approval(approval, recipient_email, next_review_route, greeting):
    if not recipient_email:
        logging.error("No recipient email provided for approval notification.")
        return

    review_url = url_for(next_review_route, approval_id=approval.approval_id, _external=True)

    subject = f"Part-time Lecturer Claim Approval Request - {approval.lecturer.name} ({approval.subject_level})"
    body = (
        f"Dear {greeting},\n\n"
        f"There is a part-time lecturer claim request pending your review and approval.\n\n"
        f"Please review the file here:\n{approval.file_url}\n\n"
        f"Please click the link below to approve or reject the request.\n"
        f"{review_url}\n\n"
        "Thank you,\n"
        "The CourseXcel Team"
    )

    send_email(recipient_email, subject, body)

def send_rejection_email(role, approval, reason):
    subject = "Part-time Lecturer Claim Request Rejected"

    role_names = {
        "PO": "Program Officer",
        "Dean": "Dean / Head of School",
        "HR": "HR"
    }

    recipients_map = {
        "PO": [approval.lecturer.email] if approval.lecturer else [],
        "Dean": [
            approval.lecturer.email if approval.lecturer else None,
            approval.program_officer.email if approval.program_officer else None
        ],
        "HR": [
            approval.lecturer.email if approval.lecturer else None,
            approval.program_officer.email if approval.program_officer else None,
            approval.department.dean_email if approval.department else None
        ]
    }

     # Clean up None values and deduplicate
    recipients = list(set(filter(None, recipients_map.get(role, []))))

    rejected_by = role_names.get(role, "Unknown Role")
    greeting = "Dear Requester" if role == "PO" else "Dear All"

    body = (
        f"{greeting},\n\n"
        f"The part-time lecturer claim approval request has been rejected by the {rejected_by}.\n\n"
        f"Reason for rejection: {reason}\n\n"
        f"You can review the file here:\n{approval.file_url}\n\n"
        "Please take necessary actions.\n\n"
        "Thank you,\n"
        "The CourseXcel Team"
    )

    send_email(recipients, subject, body)
