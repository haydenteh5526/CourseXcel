import os, io, logging, pytz, base64

from openpyxl.drawing.image import Image as ExcelImage
from flask import jsonify, render_template, request, redirect, url_for, session, flash
from app import app, db, mail
from app.models import Department, Lecturer, LecturerFile, ProgramOfficer, HOP, Other, Approval
from app.excel_generator import generate_excel
from app.auth import login_po, logout_session
from app.database import handle_db_connection
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
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

def get_drive_service():
    SERVICE_ACCOUNT_FILE = '/home/TomazHayden/coursexcel-459515-3d151d92b61f.json'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, file_name):
    try:
        service = get_drive_service()
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        # Make file publicly accessible
        service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'},
        ).execute()

        file_id = file.get('id')
        file_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        return file_url, file_id
    except Exception as e:
        logging.error(f"Failed to upload to Google Drive: {e}")
        raise

def get_current_datetime():
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now_myt = datetime.now(malaysia_tz)
    return now_myt.strftime('%a, %d %b %y, %I:%M:%S %p')

@app.route('/poLoginPage', methods=['GET', 'POST'])
def poLoginPage():
    if 'po_id' in session:
        return redirect(url_for('poHomepage'))

    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if login_po(email, password):
            return redirect(url_for('poHomepage'))
        else:
            error_message = 'Invalid email or password.'
    return render_template('poLoginPage.html', error_message=error_message)

@app.route('/poHomepage', methods=['GET', 'POST'])
@handle_db_connection
def poHomepage():
    if 'po_id' not in session:
        return redirect(url_for('poLoginPage'))

    return render_template('poHomepage.html')

@app.route('/poFormPage', methods=['GET', 'POST'])
@handle_db_connection
def poFormPage():
    if 'po_id' not in session:
        return redirect(url_for('poLoginPage'))
    
    try:
        # Clean up temp folder first
        cleanup_temp_folder()
        
        # Get all departments and lecturers with their details
        departments = Department.query.all()
        lecturers = Lecturer.query.all()
        
        return render_template('poFormPage.html', 
                             departments=departments,
                             lecturers=lecturers)
    except Exception as e:
        print(f"Error in main route: {str(e)}")
        return str(e), 500
    
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
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error getting lecturer details: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })
    
@app.route('/poLecturersPage', methods=['GET', 'POST'])
@handle_db_connection
def poLecturersPage():
    if 'po_id' not in session:
        return redirect(url_for('poLoginPage'))

    # Set default tab if none exists
    if 'po_lecturerspage_tab' not in session:
        session['po_lecturerspage_tab'] = 'lecturers'
    
    lecturers = Lecturer.query.all()  
    lecturers_file = LecturerFile.query.all()
  
    return render_template('poLecturersPage.html', 
                           lecturers=lecturers,
                        lecturers_file=lecturers_file)

@app.route('/set_lecturerspage_tab', methods=['POST'])
def set_lecturerspage_tab():
    if 'po_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['lecturerspage_tab'] = data.get('lecturerspage_current_tab')
    return jsonify({'success': True})

@app.route('/poConversionResult', methods=['POST'])
@handle_db_connection
def poConversionResultP():
    if 'po_id' not in session:
        return redirect(url_for('poLoginPage'))
    try:
        # Debug: Print all form data
        print("Form Data:", request.form)
        
        # Get form data
        school_centre = request.form.get('school_centre')
        lecturer_id = request.form.get('lecturer_id')
        
        lecturer = Lecturer.query.get(lecturer_id)
        name = lecturer.name if lecturer else None
        
        designation = request.form.get('designation')
        ic_number = request.form.get('ic_number')

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
     
            course_data = {
                'program_level': request.form.get(f'programLevel{i}'),
                'subject_code': subject_code,
                'subject_title': request.form.get(f'subjectTitle{i}'),
                'start_date': request.form.get(f'teachingPeriodStart{i}'),
                'end_date': request.form.get(f'teachingPeriodEnd{i}'),
                'hourly_rate': safe_int(request.form.get(f'hourlyRate{i}'),0),
                'lecture_hours': safe_int(request.form.get(f'lectureHours{i}'), 0),
                'tutorial_hours': safe_int(request.form.get(f'tutorialHours{i}'), 0),
                'practical_hours': safe_int(request.form.get(f'practicalHours{i}'), 0),
                'blended_hours': safe_int(request.form.get(f'blendedHours{i}'), 1),
                'lecture_weeks': safe_int(request.form.get(f'lectureWeeks{i}'), 14),
                'tutorial_weeks': safe_int(request.form.get(f'tutorialWeeks{i}'), 0),
                'practical_weeks': safe_int(request.form.get(f'practicalWeeks{i}'), 0),
                'elearning_weeks': safe_int(request.form.get(f'elearningWeeks{i}'), 14)
            }
            course_details.append(course_data)
            i += 1

        if not course_details:
            return jsonify(success=False, error="No course details provided"), 400
        
        program_officer = ProgramOfficer.query.get(session.get('po_id'))
        hop = HOP.query.filter_by(level=request.form.get('programLevel1'), department_code=school_centre).first()
        department = Department.query.filter_by(department_code=school_centre).first()
        ad = Other.query.filter_by(role="Academic Director").first()
        hr = Other.query.filter_by(role="Human Resources").first()

        po_name = program_officer.name if program_officer else 'N/A'
        hop_name = hop.name if hop else 'N/A'
        dean_name = department.dean_name if department else 'N/A'
        ad_name = ad.name if ad else 'N/A'
        hr_name = hr.name if hr else 'N/A'
        
        # Generate Excel file
        output_path, po_sign_col, hop_sign_col, hop_date_col, dean_sign_col, dean_date_col, ad_sign_col, ad_date_col, hr_sign_col, hr_date_col = generate_excel(
            school_centre=school_centre,
            name=name,
            designation=designation,
            ic_number=ic_number,
            course_details=course_details,
            po_name=po_name,
            hop_name=hop_name,
            dean_name=dean_name,
            ad_name=ad_name,
            hr_name=hr_name
        )

        file_name = os.path.basename(output_path)
        file_url = upload_to_drive(output_path, file_name)

        # Save to database
        approval = Approval(
            po_email=program_officer.email,
            po_sign_col=po_sign_col,
            hop_email=hop.email if hop else None,
            hop_sign_col=hop_sign_col,
            hop_date_col=hop_date_col,
            dean_email=department.dean_email if department else None,
            dean_sign_col=dean_sign_col,
            dean_date_col=dean_date_col,
            ad_email=ad.email if ad else None,
            ad_sign_col=ad_sign_col,
            ad_date_col=ad_date_col,
            hr_email=hr.email if hr else None,
            hr_sign_col=hr_sign_col,
            hr_date_col=hr_date_col,
            file_name=file_name,
            file_url=file_url,
            status="Pending Acknowledgment by Program Officer",
            last_updated = get_current_datetime()
        )

        db.session.add(approval)
        db.session.commit()

        return jsonify(success=True, file_url=file_url)
        
    except Exception as e:
        logging.error(f"Error in result route: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/poConversionResultPage')
def poConversionResultPage():
    if 'po_id' not in session:
        return redirect(url_for('poLoginPage'))
    
    approval = Approval.query.filter_by(po_email=session.get('po_email')).order_by(Approval.approval_id.desc()).first()
    return render_template('poConversionResultPage.html', file_url=approval.file_url)


@app.route('/poApprovalsPage')
@handle_db_connection
def poApprovalsPage():
    if 'po_id' not in session:
        return redirect(url_for('poLoginPage'))

    po_email = session.get('po_email')
    approvals = Approval.query.filter_by(po_email=po_email).all()
    
    return render_template('poApprovalsPage.html', approvals=approvals)

@app.route('/check_approval_status/<int:approval_id>')
def check_approval_status(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    return jsonify({'status': approval.status})

def download_from_drive(file_name):
    drive_service = get_drive_service()
    
    # Search for the file by name in Drive
    results = drive_service.files().list(
        q=f"name='{file_name}' and trashed=false",
        spaces='drive',
        fields='files(id, name)').execute()
    files = results.get('files', [])

    if not files:
        raise FileNotFoundError(f"File '{file_name}' not found in Google Drive")

    file_id = files[0]['id']

    # Prepare local path
    output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "temp")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    local_path = os.path.join(output_folder, file_name)

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(local_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.close()
    return local_path


@app.route('/upload_signature/<approval_id>', methods=['POST'])
@handle_db_connection
def upload_signature(approval_id):
    try:
        data = request.get_json()
        image_data = data.get("image")

        if not image_data or "," not in image_data:
            logging.error("No image data or invalid format")
            return jsonify(success=False, error="Invalid image data format")

        # Decode base64 image
        header, encoded = image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(binary_data))

        # Save signature image temporarily
        temp_folder = os.path.join("temp")
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        temp_image_path = os.path.join(temp_folder, f"signature_{approval_id}.png")
        image.save(temp_image_path)

        # Fetch approval record
        approval = Approval.query.get(approval_id)
        if not approval:
            return jsonify(success=False, error="Approval record not found")

        # Download original Excel file
        local_excel_path = download_from_drive(approval.file_name)

        # Open and modify Excel
        wb = load_workbook(local_excel_path)
        ws = wb.active

        # Insert signature image
        signature_img = ExcelImage(temp_image_path)
        signature_img.width = 200
        signature_img.height = 30
        ws.add_image(signature_img, approval.po_sign_col)

        # Save updated Excel file with same file name
        updated_excel_path = os.path.join(temp_folder, approval.file_name)
        wb.save(updated_excel_path)

        # Upload updated file with same name to Drive
        new_file_url, new_file_id = upload_to_drive(updated_excel_path, approval.file_name)

        # If file URL changed, delete old one
        if new_file_url != approval.file_url:
            old_file_name = approval.file_name
            drive_service = get_drive_service()
            results = drive_service.files().list(
                q=f"name='{old_file_name}' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            files = results.get('files', [])
            for file in files:
                if file['id'] != new_file_id:  # Do not delete the new file
                    drive_service.files().delete(fileId=file['id']).execute()

        approval.file_url = new_file_url
        db.session.commit()

        return jsonify(success=True)

    except Exception as e:
        logging.error(f"Error uploading signature: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/approve_requisition/<approval_id>', methods=['POST'])
@handle_db_connection
def approve_requisition(approval_id):
    try:
        approval = Approval.query.get(approval_id)
        if not approval:
            return jsonify(success=False, error="Approval record not found")

        approval.status = "Pending Acknowledgement by Head of Programme"
        approval.last_updated = get_current_datetime()
        db.session.commit()

        subject = f"Part-time Lecturer Requisition Approval Request"
        body = (
            f"Dear Head of Programme,\n\n"
            f"There is a part-time requisition request pending your review and approval.\n"
            f"Please review the requisition document here:\n{approval.file_url}\n\n"
            "Please click the link below to approve or reject the request.\n\n"
            "Thank you.\n"
            "The CourseXcel Team"
        )

        send_email(approval.hop_email, subject, body)

        return jsonify(success=True)

    except Exception as e:
        logging.error(f"Error in approval: {e}")
        return jsonify(success=False, error=str(e)), 500

def send_email(recipient, subject, body):
    try:
        msg = Message(subject, recipients=[recipient], body=body)
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")
        return False

@app.route('/poProfilePage')
def poProfilePage():
    po_email = session.get('po_email')  # get from session

    if not po_email:
        return redirect(url_for('poLoginPage'))  # if not logged in, go login

    return render_template('poProfilePage.html', po_email=po_email)
    
@app.route('/poLogout')
def poLogout():
    logout_session()
    return redirect(url_for('poLoginPage'))

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
