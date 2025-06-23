from flask import jsonify, request, current_app
from app import app, db
from app.models import Lecturer, Head
import pandas as pd
import logging
from app.database import handle_db_connection
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
                        email = str(row['Email']).strip()
                        if pd.isna(email) or not email:
                            continue
                        
                        lecturer = Lecturer.query.filter_by(email=email).first()
                        
                        # If lecturer exists, update its fields
                        if lecturer:
                            lecturer.name = str(row['Name'])
                            lecturer.level = str(row['Level'])
                            lecturer.department_code = department_code
                            lecturer.ic_no = str(row['IC No'])
                        else:
                            # Create new lecturer if it doesn't exist
                            lecturer = Lecturer(
                                name=str(row['Name']),
                                email=email,
                                password = bcrypt.generate_password_hash('default_password').decode('utf-8'),
                                level=str(row['Level']),
                                department_code=department_code,
                                ic_no=str(row['IC No'])
                            )
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
                        email = str(row['Email']).strip()
                        if pd.isna(email) or not email:
                            continue
                        
                        head = Head.query.filter_by(email=email).first()
                        
                        # If head exists, update its fields
                        if head:
                            head.name = str(row['Name'])
                            head.level = str(row['Level']).strip()
                            head.department_code = department_code
                        else:
                            # Create new lecturer if it doesn't exist
                            head = Head(
                                name=str(row['Name']),
                                email=email,
                                level=str(row['Level']),
                                department_code=department_code,
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
