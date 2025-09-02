import pandas as pd
import logging
from app import app, db
from app.database import handle_db_connection
from app.models import Department, Head, Lecturer
from flask import current_app, jsonify, request
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
logger = logging.getLogger(__name__)

@app.route('/upload_lecturers', methods=['POST'])
@handle_db_connection
def upload_lecturers():
    if 'lecturer_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['lecturer_file']

    if not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        return jsonify({
            'success': False,
            'message': 'Invalid file format. Please upload an Excel (.xls or .xlsx) file.'
        })
    
    try:
        excel_file = pd.ExcelFile(file)

        if not excel_file.sheet_names:
            return jsonify({'success': False, 'message': 'The uploaded Excel file contains no sheets.'})

        errors = []
        warnings = []
        sheets_processed = 0
        lecturers_to_add = []
        lecturers_to_update = []

        # Iterate sheets
        for sheet_name in excel_file.sheet_names:
            current_app.logger.info(f"Processing sheet: {sheet_name}")
            department_code = sheet_name.strip().upper()
            department = Department.query.filter_by(department_code=department_code).first()
            if not department:
                errors.append(f"Department with code '{department_code}' not found.")
                continue

            df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="B:E", skiprows=1)
            if df.empty:
                continue
            sheets_processed += 1

            expected_columns = ['Name', 'Email', 'Level', 'IC No']
            if list(df.columns) != expected_columns:
                errors.append(f"Incorrect headers in sheet '{sheet_name}'. Expected: {expected_columns}, Found: {list(df.columns)}")
                continue

            df.columns = expected_columns

            for index, row in df.iterrows():
                name = str(row['Name']).strip()
                email = str(row['Email']).strip()
                level = str(row['Level']).strip()
                ic_no = str(row['IC No']).strip()

                # Row-level validations
                if not name:
                    errors.append(f"Row {index + 2} in sheet '{sheet_name}': Name cannot be empty.")
                    continue
                if not email.endswith('@newinti.edu.my'):
                    errors.append(f"Row {index + 2} in sheet '{sheet_name}': Email must end with '@newinti.edu.my'.")
                    continue
                if level not in ['I', 'II', 'III']:
                    errors.append(f"Row {index + 2} in sheet '{sheet_name}': Level must be 'I', 'II', or 'III'.")
                    continue
                if len(ic_no) != 12 or not ic_no.isdigit():
                    errors.append(f"Row {index + 2} in sheet '{sheet_name}': IC No must be exactly 12 digits and contain no letters or symbols.")
                    continue

                # Check existing lecturer
                existing_lecturer = Lecturer.query.filter_by(email=email).first()
                if existing_lecturer:
                    lecturers_to_update.append({
                        'instance': existing_lecturer,
                        'data': {
                            'name': name,
                            'level': level,
                            'department_id': department.department_id,
                            'ic_no': ic_no
                        }
                    })
                else:
                    lecturers_to_add.append({
                        'name': name,
                        'email': email,
                        'password': bcrypt.generate_password_hash('default_password').decode('utf-8'),
                        'level': level,
                        'department_id': department.department_id,
                        'ic_no': ic_no
                    })

        # If no sheets had data
        if sheets_processed == 0:
            return jsonify({'success': False, 'message': 'All sheets are empty or contain no readable data.'})

        # If any errors, return without committing
        if errors:
            db.session.rollback()
            return jsonify({
                'success': False,
                'errors': errors,
                'message': 'Upload failed due to errors. No lecturers were added or updated.'
                
            })

        # Perform atomic commit
        try:
            for lec_data in lecturers_to_add:
                lecturer = Lecturer(
                    name=lec_data['name'],
                    email=lec_data['email'],
                    password=lec_data['password'],
                    level=lec_data['level'],
                    department_id=lec_data['department_id']
                )
                lecturer.set_ic_no(lec_data['ic_no'])
                db.session.add(lecturer)

            for update in lecturers_to_update:
                instance = update['instance']
                data = update['data']
                instance.name = data['name']
                instance.level = data['level']
                instance.department_id = data['department_id']
                instance.set_ic_no(data['ic_no'])

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to commit lecturers: {str(e)}")
            return jsonify({'success': False, 'message': f"Database commit failed: {str(e)}"})

        total_processed = len(lecturers_to_add) + len(lecturers_to_update)
        response_data = {
            'success': True,
            'message': f"Successfully processed {total_processed} lecturer(s)."
        }
        if warnings:
            response_data['warnings'] = warnings

        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({'success': False, 'message': f"Error processing file: {str(e)}"})

@app.route('/upload_heads', methods=['POST'])
@handle_db_connection
def upload_heads():
    if 'head_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['head_file']

    if not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        return jsonify({
            'success': False,
            'message': 'Invalid file format. Please upload an Excel (.xls or .xlsx) file.'
        })
    
    try:
        excel_file = pd.ExcelFile(file)

        if not excel_file.sheet_names:
            return jsonify({'success': False, 'message': 'The uploaded Excel file contains no sheets.'})

        errors = []
        warnings = []
        sheets_processed = 0
        heads_to_add = []
        heads_to_update = []

        for sheet_name in excel_file.sheet_names:
            current_app.logger.info(f"Processing sheet: {sheet_name}")
            department_code = sheet_name.strip().upper()
            department = Department.query.filter_by(department_code=department_code).first()
            if not department:
                errors.append(f"Department with code '{department_code}' not found.")
                continue

            df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="B:D", skiprows=1)
            if df.empty:
                continue
            sheets_processed += 1

            expected_columns = ['Name', 'Email', 'Level']
            if list(df.columns) != expected_columns:
                errors.append(f"Incorrect headers in sheet '{sheet_name}'. Expected: {expected_columns}, Found: {list(df.columns)}")
                continue

            df.columns = expected_columns

            for index, row in df.iterrows():
                name = str(row['Name']).strip()
                email = str(row['Email']).strip()
                level = str(row['Level']).strip()

                # Row-level validations
                if not name:
                    errors.append(f"Row {index + 2} in sheet '{sheet_name}': Name cannot be empty.")
                    continue
                if not email.endswith('@newinti.edu.my'):
                    errors.append(f"Row {index + 2} in sheet '{sheet_name}': Email must end with '@newinti.edu.my'.")
                    continue
                if level not in ['Certificate', 'Foundation', 'Diploma', 'Degree', 'Others']:
                    errors.append(f"Row {index + 2} in sheet '{sheet_name}': Level must be 'Certificate', 'Foundation', 'Diploma', 'Degree', or 'Others'.")
                    continue

                # Check existing head
                existing_head = Head.query.filter_by(email=email).first()
                if existing_head:
                    heads_to_update.append({
                        'instance': existing_head,
                        'data': {
                            'name': name,
                            'level': level,
                            'department_id': department.department_id
                        }
                    })
                else:
                    heads_to_add.append({
                        'name': name,
                        'email': email,
                        'level': level,
                        'department_id': department.department_id
                    })

        if sheets_processed == 0:
            return jsonify({'success': False, 'message': 'All sheets are empty or contain no readable data.'})

        if errors:
            db.session.rollback()
            return jsonify({
                'success': False,
                'errors': errors,
                'message': 'Upload failed due to errors. No heads were added or updated.'
            })

        # Commit all additions and updates at once
        try:
            for head_data in heads_to_add:
                head = Head(
                    name=head_data['name'],
                    email=head_data['email'],
                    level=head_data['level'],
                    department_id=head_data['department_id']
                )
                db.session.add(head)

            for update in heads_to_update:
                instance = update['instance']
                data = update['data']
                instance.name = data['name']
                instance.level = data['level']
                instance.department_id = data['department_id']

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to commit heads: {str(e)}")
            return jsonify({'success': False, 'message': f"Database commit failed: {str(e)}"})

        total_processed = len(heads_to_add) + len(heads_to_update)
        response_data = {
            'success': True,
            'message': f"Successfully processed {total_processed} head(s)."
        }
        if warnings:
            response_data['warnings'] = warnings

        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({'success': False, 'message': f"Error processing file: {str(e)}"})
