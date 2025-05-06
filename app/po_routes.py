import os, logging, io
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session
from app import app, db
from app.models import Department, Lecturer
from app.excel_generator import generate_excel
from app.auth import login_po, logout_session
from flask_bcrypt import Bcrypt
from app.database import handle_db_connection
bcrypt = Bcrypt()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    lecturers = Lecturer.query.all()
        
    return render_template('poLecturersPage.html', 
                           lecturers=lecturers)

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
        
        # Get the actual lecturer name
        if lecturer_id == 'new_lecturer':
            name = request.form.get('name')
        else:
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

@app.route('/poConversionResultDownload')
def poConversionResultDownload():
    if 'po_id' not in session:
        return redirect(url_for('poLoginPage'))
    filename = request.args.get('filename')
    return render_template('poConversionResultPage.html', filename=filename)


@app.route('/download')
def download():
    if 'po_id' not in session:
        return redirect(url_for('poLoginPage'))

    # Get filename from request
    filename = request.args.get('filename')
    if not filename:
        flash('No file to download', 'warning')
        return redirect(url_for('poConversionResultDownload'))

    # Construct file path
    file_path = os.path.join(app.root_path, 'temp', filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash('File not found', 'error')
        return redirect(url_for('poConversionResultDownload'))

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
        return redirect(url_for('poConversionResultDownload'))
    
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
