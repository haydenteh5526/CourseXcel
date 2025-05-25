import os, logging, io
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session
from app import app, db
from app.models import Department, Lecturer, LecturerFile, ProgramOfficer, HOP, Other, Approval
from app.excel_generator import generate_excel
from app.auth import login_po, logout_session
from app.database import handle_db_connection
from flask_bcrypt import Bcrypt
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
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
        return file_url
    except Exception as e:
        logging.error(f"Failed to upload to Google Drive: {e}")
        raise


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

@app.route('/poConversionResultPage', methods=['POST'])
@handle_db_connection
def poConversionResultPage():
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
        output_path = generate_excel(
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
            hop_email=hop.email if hop else None,
            dean_email=department.dean_email if department else None,
            ad_email=ad.email if ad else None,
            hr_email=hr.email if hr else None,
            file_name=file_name,
            file_url=file_url,
            status="Pending Acknowledgment by Program Officer"
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
    file_url = request.args.get('file_url')
    return render_template('poConversionResultPage.html', file_url=file_url)

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
