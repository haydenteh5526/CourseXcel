from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import os
from config import Config
from models import db, User, Lecturer, Subject
from extract_table_from_pdf import extract_table_from_pdf, convert_tables_to_excel
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Ensure required directories exist
os.makedirs('samplePDFs', exist_ok=True)
os.makedirs('static/outputs', exist_ok=True)

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
                flash('Logged in successfully!', 'success')
                return redirect(url_for('main'))
            else:
                flash('Invalid email or password', 'error')
        except SQLAlchemyError as e:
            flash('An error occurred. Please try again.', 'error')
            app.logger.error(f"Database error during login: {str(e)}")
    
    return render_template('login.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        lecturers = Lecturer.query.all()
        subjects = Subject.query.all()
    except SQLAlchemyError as e:
        flash('An error occurred while fetching data.', 'error')
        app.logger.error(f"Database error in main route: {str(e)}")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'pdfFile' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['pdfFile']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join('samplePDFs', file.filename)
            file.save(pdf_path)
            tables = extract_table_from_pdf(pdf_path)
            if tables:
                excel_path = os.path.join('static', 'outputs', f"{os.path.splitext(file.filename)[0]}.xlsx")
                convert_tables_to_excel(tables, excel_path)
                session['excel_path'] = excel_path
                flash('PDF converted successfully!', 'success')
                return redirect(url_for('result'))
            else:
                flash('No tables found in the PDF', 'error')
        else:
            flash('Invalid file type', 'error')
    
    return render_template('main.html', lecturers=lecturers, subjects=subjects)

@app.route('/get_lecturer_info', methods=['POST'])
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
    return jsonify({})

@app.route('/get_subject_info', methods=['POST'])
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
    return jsonify({})

@app.route('/result')
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    excel_path = session.get('excel_path')
    if not excel_path:
        return redirect(url_for('main'))
    
    return render_template('result.html', excel_filename=os.path.basename(excel_path))

@app.route('/download_excel')
def download_excel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    excel_path = session.get('excel_path')
    if not excel_path:
        flash('No Excel file available for download', 'error')
        return redirect(url_for('main'))
    
    return send_file(excel_path, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('excel_path', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)