from flask import jsonify, request, current_app
from app import app, db
from app.models import Lecturer
import pandas as pd
import logging
from app.database import handle_db_connection
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

logger = logging.getLogger(__name__)

@app.route('/upload_lecturers', methods=['POST'])
@handle_db_connection
def upload_lecturers():
    print("upload_lecturers route hit")  # ← Add this
    if 'lecturer_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['lecturer_file']
    records_added = 0
    errors = []
    warnings = []
    
    try:
        excel_file = pd.ExcelFile(file)
        
        for sheet_name in excel_file.sheet_names:
            current_app.logger.info(f"Processing sheet: {sheet_name}")
            department_code = sheet_name.strip().upper()
            
            try:
                df = pd.read_excel(
                    excel_file, 
                    sheet_name=sheet_name,
                    usecols="B:G",
                    skiprows=1
                )
                
                df.columns = ['Name', 'Email', 'Level', 'IC No']
                
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
                            records_added += 1
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
