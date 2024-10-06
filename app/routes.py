import os
import logging
from flask import jsonify, render_template, request, redirect, send_file, url_for, flash, session
from app import app
from app.models import User, Lecturer, Subject
from app.test_pdf_to_excel import conversion
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configurations
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')  # Use app.root_path for absolute path
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure that the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key_here'  # Ensure to use a strong secret key for session management

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Perform any authentication if needed
        return redirect(url_for('main'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/result', methods=['POST'])
def result():
    try:
        logging.info('Entering result route.')
        # Validate form data
        lecturer_name = request.form.get('lecturer_name')
        designation = request.form.get('designation')
        ic_number = request.form.get('ic_number')

        if not lecturer_name or not designation or not ic_number:
            return jsonify(success=False, error="Missing lecturer name, designation, or IC number"), 400
        
        # Extract course details from form
        course_details = []
        for i in range(1, 5):  # Assuming up to 4 courses
            program_level = request.form.get(f'programLevel{i}')
            subject_code = request.form.get(f'subjectCode{i}')
            subject_title = request.form.get(f'subjectTitle{i}')
            lecture_weeks = request.form.get(f'lectureWeeks{i}')
            tutorial_weeks = request.form.get(f'tutorialWeeks{i}')
            practical_weeks = request.form.get(f'practicalWeeks{i}')
            start_date = request.form.get(f'teachingPeriodStart{i}')
            end_date = request.form.get(f'teachingPeriodEnd{i}')

            # Check if all details are valid for this course
            if program_level and subject_code and subject_title and lecture_weeks and tutorial_weeks and practical_weeks and start_date and end_date:
                course_data = {
                    'program_level': program_level,
                    'subject_code': subject_code,
                    'subject_title': subject_title,
                    'lecture_weeks': int(lecture_weeks),
                    'tutorial_weeks': int(tutorial_weeks),
                    'practical_weeks': int(practical_weeks),
                    'start_date': start_date,
                    'end_date': end_date
                }
                course_details.append(course_data)
        
        # Check if at least one course has valid data
        if not course_details:
            return jsonify(success=False, error="No valid course details found."), 400

        # Get the file from form data
        pdf_files = []
        for i in range(1, len(course_details) + 1):
            file = request.files.get(f'pdfFile{i}')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save file to correct directory
                file.save(file_path)
                logging.info(f"File saved to: {file_path}")
                pdf_files.append(file_path)
            else:
                return jsonify(success=False, error=f"Missing or invalid PDF file for course {i}"), 400
        
        # Pass correct file path to conversion
        output_filename = conversion(
            pdf_paths=pdf_files,  # Pass the list of file paths
            lecturer_name=lecturer_name,
            designation=designation,
            ic_number=ic_number,
            course_details=course_details
        )
        
        return jsonify(success=True, filename=output_filename)
    except Exception as e:
        logging.error(f"An error occurred during conversion: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/result_page')
def result_page():
    filename = request.args.get('filename')
    return render_template('result.html', filename=filename)

@app.route('/download')
def download():
    filename = request.args.get('filename')
    if filename:
        file_path = os.path.join(app.root_path, 'outputs', filename)  # Ensure the correct path
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            logging.error(f"An error occurred while trying to download file: {e}")
            flash('Error occurred while trying to download the file', 'danger')
            return redirect(url_for('result_page', filename=filename))
    else:
        flash('No file to download', 'warning')
        return redirect(url_for('result_page'))

if __name__ == "__main__":
    app.run(debug=True)
