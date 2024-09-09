from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from config import Config
from models import db, User, Lecturer, Subject
from extract_table_from_pdf import extract_table_from_pdf, convert_tables_to_excel
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Ensure required directories exist
os.makedirs('samplePDFs', exist_ok=True)
os.makedirs('static/outputs', exist_ok=True)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "Please log in to access this page"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                session['user_id'] = user.id
                return jsonify({"success": True, "message": "Logged in successfully!"})
            else:
                return jsonify({"success": False, "message": "Invalid email or password"}), 401
        except SQLAlchemyError as e:
            app.logger.error(f"Database error during login: {str(e)}")
            return jsonify({"success": False, "message": "An error occurred. Please try again."}), 500
    
    return render_template('login.html')

@app.route('/main', methods=['GET', 'POST'])
@login_required
def main():
    try:
        lecturers = Lecturer.query.all()
        subjects = Subject.query.all()
    except SQLAlchemyError as e:
        app.logger.error(f"Database error in main route: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while fetching data."}), 500
    
    if request.method == 'POST':
        if 'pdfFile' not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400
        file = request.files['pdfFile']
        if file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400
        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join('samplePDFs', file.filename)
            file.save(pdf_path)
            tables = extract_table_from_pdf(pdf_path)
            if tables:
                excel_path = os.path.join('static', 'outputs', f"{os.path.splitext(file.filename)[0]}.xlsx")
                convert_tables_to_excel(tables, excel_path)
                session['excel_path'] = excel_path
                return jsonify({"success": True, "message": "PDF converted successfully!"})
            else:
                return jsonify({"success": False, "message": "No tables found in the PDF"}), 400
        else:
            return jsonify({"success": False, "message": "Invalid file type"}), 400
    
    return render_template('main.html', lecturers=lecturers, subjects=subjects)

@app.route('/get_lecturer_info', methods=['POST'])
@login_required
def get_lecturer_info():
    lecturer_id = request.json['lecturer_id']
    try:
        lecturer = Lecturer.query.get(lecturer_id)
        if lecturer:
            return jsonify({
                'level': lecturer.level,
                'email': lecturer.email,
                'hourlyRate': f'${lecturer.hourly_rate:.2f}'
            })
    except SQLAlchemyError as e:
        app.logger.error(f"Database error in get_lecturer_info: {str(e)}")
    return jsonify({}), 404

@app.route('/get_subject_info', methods=['POST'])
@login_required
def get_subject_info():
    subject_code = request.json['subject_code']
    try:
        subject = Subject.query.filter_by(code=subject_code).first()
        if subject:
            return jsonify({
                'title': subject.title,
                'startDate': subject.start_date.isoformat(),
                'endDate': subject.end_date.isoformat()
            })
    except SQLAlchemyError as e:
        app.logger.error(f"Database error in get_subject_info: {str(e)}")
    return jsonify({}), 404

@app.route('/result')
@login_required
def result():
    excel_path = session.get('excel_path')
    if not excel_path:
        return redirect(url_for('main'))
    
    return render_template('result.html', excel_filename=os.path.basename(excel_path))

@app.route('/download_excel')
@login_required
def download_excel():
    excel_path = session.get('excel_path')
    if not excel_path:
        return jsonify({"success": False, "message": "No Excel file available for download"}), 404
    
    return send_file(excel_path, as_attachment=True)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)