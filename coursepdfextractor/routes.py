from flask import render_template, request, redirect, url_for, flash
from coursepdfextractor import app
from coursepdfextractor.models import User, Lecturer, Subject
import os
from werkzeug.utils import secure_filename


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'pdfFile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdfFile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect(url_for('result'))
    return render_template('result.html')

