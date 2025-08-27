import pandas as pd
import logging
from app import app, db
from app.database import handle_db_connection
from app.models import Department, Lecturer, Head
from flask import jsonify, request, current_app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
logger = logging.getLogger(__name__)

@app.route('/upload_lecturers', methods=['POST'])
@handle_db_connection
def upload_lecturers():
    if 'lecturer_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['lecturer_file']
    records_added = 0
    errors = []
    warnings = []

    if not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        return jsonify({'success': False, 'message': 'Invalid file format. Please upload an Excel (.xls or .xlsx) file.'})
    
    try:
        excel_file = pd.ExcelFile(file)

        if not excel_file.sheet_names:
            return jsonify({'success': False, 'message': 'The uploaded Excel file contains no sheets.'})
        
        for sheet_name in excel_file.sheet_names:
            current_app.logger.info(f"Processing sheet: {sheet_name}")
            department_code = sheet_name.strip().upper()

            department = Department.query.filter_by(department_code=department_code).first()
            if not department:
                raise ValueError(f"Department with code '{department_code}' not found.")
            
            try:
                df = pd.read_excel(
                    excel_file, 
                    sheet_name=sheet_name,
                    usecols="B:E",
                    skiprows=1
                )

                if df.empty:
                    raise ValueError(f"Sheet '{sheet_name}' is empty or contains no readable data.")
                
                expected_columns = ['Name', 'Email', 'Level', 'IC No']
                actual_columns = list(df.columns)

                if actual_columns != expected_columns:
                    raise ValueError(
                        f"Incorrect or unexpected column headers in sheet '{sheet_name}'.\n"
                        f"Expected: {expected_columns}\nFound: {actual_columns}"
                    )

                df.columns = expected_columns
                
                for index, row in df.iterrows():
                    try:
                        # Validate Name: Must not be empty
                        name = str(row['Name']).strip()
                        if not name:
                            errors.append(f"Row {index + 2}: Name cannot be empty.")
                            continue

                        # Validate Email: Must end with '@newinti.edu.my'
                        email = str(row['Email']).strip()
                        if not email.endswith('@newinti.edu.my'):
                            errors.append(f"Row {index + 2}: Email must end with '@newinti.edu.my'.")
                            continue

                        # Validate Level: Must be 'I', 'II', or 'III'
                        level = str(row['Level']).strip()
                        if level not in ['I', 'II', 'III']:
                            errors.append(f"Row {index + 2}: Level must be 'I', 'II', or 'III'.")
                            continue

                        # Validate IC No: Must be 12 digits, no letters or symbols
                        ic_no = str(row['IC No']).strip()
                        if len(ic_no) != 12 or not ic_no.isdigit():
                            errors.append(f"Row {index + 2}: IC No must be exactly 12 digits and contain no letters or symbols.")
                            continue
                        
                        # Check if the lecturer already exists
                        lecturer = Lecturer.query.filter_by(email=email).first()
                        
                        # If lecturer exists, update its fields
                        if lecturer:
                            lecturer.name = name
                            lecturer.level = level
                            lecturer.department_id = department.department_id
                            lecturer.set_ic_number(ic_no)
                        else:
                            # Create new lecturer if it doesn't exist
                            lecturer = Lecturer(
                                name=name,
                                email=email,
                                password=bcrypt.generate_password_hash('default_password').decode('utf-8'),
                                level=level,
                                department_id=department.department_id,
                            )
                            lecturer.set_ic_number(ic_no)
                            db.session.add(lecturer)
                            records_added += 1
                                           
                        db.session.commit()
                        
                    except Exception as e:
                        error_msg = f"Error in sheet {sheet_name}, row {index + 2}: {str(e)}"
                        errors.append(error_msg)
                        current_app.logger.error(error_msg)
                        db.session.rollback()
                        continue
                
            except Exception as e:
                error_msg = f"Error processing sheet {sheet_name}: {str(e)}"
                errors.append(error_msg)
                current_app.logger.error(error_msg)
                continue
        
        if records_added == 0 and errors:
            return jsonify({
                'success': False,
                'message': 'Upload failed. No lecturers processed due to errors. Please check the file format, column structure, and sheet contents before uploading.',
                'errors': errors,
                'warnings': warnings if warnings else []
            })

        response_data = {
            'success': True,
            'message': f'Successfully processed {records_added} lecturer(s)'
        }
        
        if warnings:
            response_data['warnings'] = warnings
        if errors:
            response_data['errors'] = errors
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg
        })

@app.route('/upload_heads', methods=['POST'])
@handle_db_connection
def upload_heads():
    if 'head_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['head_file']
    records_added = 0
    errors = []
    warnings = []

    if not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        return jsonify({'success': False, 'message': 'Invalid file format. Please upload an Excel (.xls or .xlsx) file.'})
    
    try:
        excel_file = pd.ExcelFile(file)

        if not excel_file.sheet_names:
            return jsonify({'success': False, 'message': 'The uploaded Excel file contains no sheets.'})
        
        for sheet_name in excel_file.sheet_names:
            current_app.logger.info(f"Processing sheet: {sheet_name}")
            department_code = sheet_name.strip().upper()

            department = Department.query.filter_by(department_code=department_code).first()
            if not department:
                raise ValueError(f"Department with code '{department_code}' not found.")
            
            try:
                df = pd.read_excel(
                    excel_file, 
                    sheet_name=sheet_name,
                    usecols="B:D",
                    skiprows=1
                )

                if df.empty:
                    raise ValueError(f"Sheet '{sheet_name}' is empty or contains no readable data.")
                
                expected_columns = ['Name', 'Email', 'Level']
                actual_columns = list(df.columns)

                if actual_columns != expected_columns:
                    raise ValueError(
                        f"Incorrect or unexpected column headers in sheet '{sheet_name}'.\n"
                        f"Expected: {expected_columns}\nFound: {actual_columns}"
                    )

                df.columns = expected_columns
     
                for index, row in df.iterrows():
                    try:
                        # Validate Name: Ensure it's not empty
                        name = str(row['Name']).strip()
                        if not name:
                            errors.append(f"Row {index + 2}: Name cannot be empty.")
                            continue

                        # Validate Email: Ensure it's a valid email
                        email = str(row['Email']).strip()
                        if not email.endswith('@newinti.edu.my'):
                            errors.append(f"Row {index + 2}: Email must end with '@newinti.edu.my'.")
                            continue

                        # Validate Level: Ensure it does not contain numbers
                        level = str(row['Level']).strip()
                        if any(char.isdigit() for char in level):
                            errors.append(f"Row {index + 2}: Level cannot contain numbers.")
                            continue

                        # Check if the head already exists
                        head = Head.query.filter_by(email=email).first()
                        
                        # If head exists, update its fields
                        if head:
                            head.name = name
                            head.level = level
                            head.department_id = department.department_id
                        else:
                            # Create new head if it doesn't exist
                            head = Head(
                                name=name,
                                email=email,
                                level=level,
                                department_id=department.department_id,
                            )
                            db.session.add(head)
                            records_added += 1
                                           
                        db.session.commit()
                        
                    except Exception as e:
                        error_msg = f"Error in sheet {sheet_name}, row {index + 2}: {str(e)}"
                        errors.append(error_msg)
                        current_app.logger.error(error_msg)
                        db.session.rollback()
                        continue
                
            except Exception as e:
                error_msg = f"Error processing sheet {sheet_name}: {str(e)}"
                errors.append(error_msg)
                current_app.logger.error(error_msg)
                continue
        
        if records_added == 0 and errors:
            return jsonify({
                'success': False,
                'message': 'Upload failed. No heads processed due to errors. Please check the file format, column structure, and sheet contents before uploading.',
                'errors': errors,
                'warnings': warnings if warnings else []
            })

        response_data = {
            'success': True,
            'message': f'Successfully processed {records_added} head(s)'
        }
        
        if warnings:
            response_data['warnings'] = warnings
        if errors:
            response_data['errors'] = errors
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg
        })
