# from flask import Flask

# app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return "<p>Hello, World!</p>"

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from config import Config
from extract_table_from_pdf import extract_table_from_pdf, convert_tables_to_excel
from flask import jsonify

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_id' not in session:
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
    
    return render_template('main.html')

@app.route('/get_lecturer_info', methods=['POST'])
def get_lecturer_info():
    lecturer_id = request.json['lecturer_id']
    # Fetch lecturer info from database
    # For now, we'll use dummy data
    lecturer_info = {
        'lecturer1': {'level': 'Senior Lecturer', 'email': 'lecturer1@example.com', 'hourlyRate': '$50'},
        'lecturer2': {'level': 'Associate Professor', 'email': 'lecturer2@example.com', 'hourlyRate': '$60'}
    }
    return jsonify(lecturer_info.get(lecturer_id, {}))

@app.route('/get_subject_info', methods=['POST'])
def get_subject_info():
    subject_code = request.json['subject_code']
    # Fetch subject info from database
    # For now, we'll use dummy data
    subject_info = {
        'code1': {'title': 'Introduction to Computer Science', 'startDate': '2024-01-15', 'endDate': '2024-05-15'},
        'code2': {'title': 'Advanced Web Development', 'startDate': '2024-02-01', 'endDate': '2024-06-01'}
    }
    return jsonify(subject_info.get(subject_code, {}))

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
    app.run(debug=True)