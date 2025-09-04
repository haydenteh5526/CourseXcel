import pandas as pd
import logging
from app import app, db
from app.database import handle_db_connection
from app.models import Head, Subject
from flask import current_app, jsonify, request

logger = logging.getLogger(__name__)

def convert_hours(value):
    """Convert hour values from various formats to integer"""
    if pd.isna(value) or value == 0 or value == '0':
        return 0
    try:
        if isinstance(value, str):
            value = value.lower().strip()
            if 'x' in value:
                # Handle format like "2x1"
                hours, _ = value.split('x')
                return int(float(hours.strip()))
            return int(float(value))
        return int(float(value))
    except (ValueError, IndexError):
        return 0

def convert_weeks(value):
    """Convert week values from various formats to integer"""
    if pd.isna(value) or value == 0:
        return 0
    try:
        if isinstance(value, str):
            value = value.lower().strip()
            if 'x' in value:
                # Handle format like "2x1"
                _, weeks = value.split('x')
                return int(float(weeks.strip()))
        return int(float(value))
    except (ValueError, TypeError):
        return 0

def determine_subject_level(sheet_name):
    """Determine subject level based on sheet name prefix"""
    sheet_name = sheet_name.strip().upper()
    
    if sheet_name.startswith('CF'):
        return 'Foundation'
    elif sheet_name.startswith('C'):
        return 'Certificate'
    elif sheet_name.startswith('D'):
        return 'Diploma'
    elif sheet_name.startswith('B'):
        return 'Degree'
    else:
        return 'Others'

@app.route('/upload_subjects', methods=['POST'])
@handle_db_connection
def upload_subjects():
    if 'cs_file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['cs_file']

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
        subjects_to_add = []
        # subjects_to_update = []

        # Iterate sheets
        for sheet_name in excel_file.sheet_names:
            current_app.logger.info(f"Processing sheet: {sheet_name}")
            subject_level = determine_subject_level(sheet_name)
            current_app.logger.info(f"Determined subject level: {subject_level}")
            
            df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="B:L", skiprows=1)
            if df.empty:
                continue  # Skip empty sheets
            sheets_processed += 1

            expected_columns = [
                'Subject Code', 'Subject Title',
                'Lecture Hours', 'Tutorial Hours', 'Practical Hours', 'Blended Hours',
                'No of Lecture Weeks', 'No of Tutorial Weeks',
                'No of Practical Weeks', 'No of Blended Weeks', 'Head'
            ]
            if list(df.columns) != expected_columns:
                errors.append(f"Incorrect headers in sheet '{sheet_name}'. Expected: {expected_columns}, Found: {list(df.columns)}")
                continue

            df.columns = expected_columns

            for index, row in df.iterrows():
                subject_code = str(row['Subject Code']).strip()
                if pd.isna(subject_code) or not subject_code:
                    continue  # skip empty subject code

                head_name = str(row['Head']).strip()
                head = Head.query.filter_by(name=head_name).first()
                if not head and head_name:
                    errors.append(f"Row {index + 2} in sheet '{sheet_name}': Head '{head_name}' not found in database. Please upload head list or add the head entry before uploading the course structure.")
                    continue

                """ existing_subject = Subject.query.filter_by(subject_code=subject_code).first()
                if existing_subject:
                    # Prepare for update
                    subjects_to_update.append({
                        'instance': existing_subject,
                        'data': {
                            'subject_title': str(row['Subject Title']).strip(),
                            'subject_level': subject_level,
                            'lecture_hours': convert_hours(row['Lecture Hours']),
                            'tutorial_hours': convert_hours(row['Tutorial Hours']),
                            'practical_hours': convert_hours(row['Practical Hours']),
                            'blended_hours': convert_hours(row['Blended Hours']),
                            'lecture_weeks': convert_weeks(row['No of Lecture Weeks']),
                            'tutorial_weeks': convert_weeks(row['No of Tutorial Weeks']),
                            'practical_weeks': convert_weeks(row['No of Practical Weeks']),
                            'blended_weeks': convert_weeks(row['No of Blended Weeks']),
                            'head_id': head.head_id if head else None
                        }
                    }) """
                #else:
                    # Prepare new subject
                subjects_to_add.append(Subject(
                    subject_code=subject_code,
                    subject_title=str(row['Subject Title']).strip(),
                    subject_level=subject_level,
                    lecture_hours=convert_hours(row['Lecture Hours']),
                    tutorial_hours=convert_hours(row['Tutorial Hours']),
                    practical_hours=convert_hours(row['Practical Hours']),
                    blended_hours=convert_hours(row['Blended Hours']),
                    lecture_weeks=convert_weeks(row['No of Lecture Weeks']),
                    tutorial_weeks=convert_weeks(row['No of Tutorial Weeks']),
                    practical_weeks=convert_weeks(row['No of Practical Weeks']),
                    blended_weeks=convert_weeks(row['No of Blended Weeks']),
                    head_id=head.head_id if head else None
                ))

        # Check if any errors occurred
        if sheets_processed == 0:
            return jsonify({'success': False, 'message': 'All sheets are empty or contain no readable data.'})

        if errors:
            db.session.rollback()
            return jsonify({
                'success': False,
                'errors': errors,
                'message': 'Upload failed due to errors. No subjects were added or updated.'
            })

        # No errors → perform database updates atomically
        try:
            for sub in subjects_to_add:
                db.session.add(sub)
            """ for update in subjects_to_update:
                instance = update['instance']
                data = update['data']
                for key, value in data.items():
                    setattr(instance, key, value) """
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to commit subjects: {str(e)}")
            return jsonify({
                'success': False,
                'message': f"Database commit failed: {str(e)}"
            })

        total_processed = len(subjects_to_add) # + len(subjects_to_update)
        response_data = {
            'success': True,
            'message': f"Successfully processed {total_processed} subject(s)."
        }
        if warnings:
            response_data['warnings'] = warnings

        return jsonify(response_data)

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error processing file: {str(e)}"
        })

@app.route('/get_subjects_by_level/<level>')
@handle_db_connection
def get_subjects_by_level(level):
    """Get subjects filtered by course level using the subject_levels association table"""
    try:
        subjects = (
                    db.session.query(Subject)
                    .filter(Subject.subject_level == level)
                    .order_by(Subject.subject_code.asc())
                    .all()
                )
        return jsonify({
            'success': True,
            'subjects': [{
                'subject_code': s.subject_code,
                'subject_title': s.subject_title,
                'lecture_hours': s.lecture_hours,
                'tutorial_hours': s.tutorial_hours,
                'practical_hours': s.practical_hours,
                'blended_hours': s.blended_hours,
                'lecture_weeks': s.lecture_weeks,
                'tutorial_weeks': s.tutorial_weeks,
                'practical_weeks': s.practical_weeks,
                'blended_weeks': s.blended_weeks
            } for s in subjects]
        })
    except Exception as e:
        error_msg = f"Error getting subjects by level: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({
            'success': False, 
            'message': error_msg,
            'subjects': []
        })

@app.route('/get_subject_details/<subject_code>')
@handle_db_connection
def get_subject_details(subject_code):
    try:
        subject = Subject.query.filter_by(subject_code=subject_code).first()
        if not subject:
            return jsonify({
                'success': False,
                'message': 'Subject not found'
            })

        return jsonify({
            'success': True,
            'subject': {
                'subject_code': subject.subject_code,
                'subject_title': subject.subject_title,
                'lecture_hours': subject.lecture_hours,
                'tutorial_hours': subject.tutorial_hours,
                'practical_hours': subject.practical_hours,
                'blended_hours': subject.blended_hours,
                'lecture_weeks': subject.lecture_weeks,
                'tutorial_weeks': subject.tutorial_weeks,
                'practical_weeks': subject.practical_weeks,
                'blended_weeks': subject.blended_weeks
            }
        })
    except Exception as e:
        logger.error(f"Error getting subject details: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })
