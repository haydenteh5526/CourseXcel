import os
import logging
from flask import render_template, request, redirect, send_file, url_for, flash, session
from app import app
from app.models import User, Lecturer, Subject
from app.test_pdf_to_excel import conversion
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

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
        lecturer_name = request.form['lecturerName']
        designation = request.form['designation']
        
        # Get the file (assuming only one PDF for simplicity)
        file = request.files['pdfFile1']  # Adjust index based on your form's naming convention

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Call conversion function
            output_filename = conversion(filename, lecturer_name, designation)

            # Redirect to result page with the output filename
            return redirect(url_for('result_page', filename=output_filename))
    except Exception as e:
        logging.error(f"An error occurred during conversion: {e}")
        return redirect(url_for('main'))  # Redirect back to main in case of failure

    return render_template('result.html')

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

