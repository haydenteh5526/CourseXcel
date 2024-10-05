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
UPLOAD_FOLDER = 'uploads'
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
        # Here you can process the email and password
        email = request.form['email']
        password = request.form['password']
        
        # Perform any authentication if needed
        
        return redirect(url_for('main'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear session data to log out user
    session.clear()
    return redirect(url_for('login'))

@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/result', methods=['POST'])
def result():
    try:
        # Validate form data
        lecturer_name = request.form.get('lecturer_name')
        designation = request.form.get('designation')
        ic_number = request.form.get('ic_number')  # Assuming it's provided in the form

        if not lecturer_name or not designation:
            return jsonify(success=False, error="Missing lecturer name or designation"), 400
        
        # Extract course details from form
        course_details = []
        for i in range(1, 5):  # Assuming up to 4 courses
            course_data = {
                'program_level': request.form.get(f'programLevel{i}'),
                'subject_code': request.form.get(f'subjectCode{i}'),
                'subject_title': request.form.get(f'subjectTitle{i}'),
                'weeks': int(request.form.get(f'weeks{i}', 0)),
                'start_date': request.form.get(f'teachingPeriodStart{i}'),
                'end_date': request.form.get(f'teachingPeriodEnd{i}')
            }
            # Ensure all details are present before adding to the list
            if all(course_data.values()):
                course_details.append(course_data)
        
        # Get the file from form data
        file = request.files.get('pdfFile1')
        if not file or not allowed_file(file.filename):
            return jsonify(success=False, error="Missing or invalid PDF file"), 400
        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Call conversion function with all necessary arguments
        output_filename = conversion(filename, lecturer_name, designation)
        
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
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'outputs', filename)
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
    # Run the Flask app
    app.run(debug=True)
