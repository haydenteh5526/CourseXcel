import pandas as pd
import logging
from app import app, db
from app.database import handle_db_connection
from app.models import Head, Subject
from flask import jsonify, request

logger = logging.getLogger(__name__)

# ============================================================
# Utility Functions
# ============================================================
def convert_hours_weeks(value):
    """Convert hour values from various formats to integer"""
    if pd.isna(value) or value == 0 or value == '0':
        return 0
    try:
        if isinstance(value, str):
            value = value.lower().strip()
            if 'x' in value: # Handle '2x1' style entries
                hours, _ = value.split('x')
                return int(float(hours.strip()))
            return int(float(value))
        return int(float(value))
    except (ValueError, IndexError):
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

# ============================================================
# Upload Subjects
# ============================================================
@app.route('/upload_subjects', methods=['POST'])
@handle_db_connection
def upload_subjects():
    if 'cs_file' not in request.files:
        logger.warning("No file (cs_file) found in request.")
        return jsonify({'success': False, 'message': 'No file uploaded'})

    file = request.files['cs_file']

    if not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        logger.warning("Invalid file format detected for course structure upload.")
        return jsonify({
            'success': False,
            'message': 'Invalid file format. Please upload an Excel (.xls or .xlsx) file.'
        })
    
    try:
        excel_file = pd.ExcelFile(file)
        logger.info(f"File '{file.filename}' successfully read into memory.")

        if not excel_file.sheet_names:
            logger.warning("Uploaded Excel file contains no sheets.")
            return jsonify({'success': False, 'message': 'The uploaded Excel file contains no sheets.'})

        errors = []
        sheets_processed = 0
        subjects_to_add, subjects_to_update = [], []

        # Process each sheet
        for sheet_name in excel_file.sheet_names:
            logger.info(f"Processing sheet: {sheet_name}")
            subject_level = determine_subject_level(sheet_name)
            logger.info(f"Determined subject level: {subject_level}")

            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="B:L", skiprows=1)
            except Exception as e:
                msg = f"Sheet '{sheet_name}' does not have the required columns B to L."
                errors.append(msg)
                logger.warning(msg)
                continue

            if df.empty:
                logger.info(f"Sheet '{sheet_name}' is empty, skipping.")
                continue
            
            expected_columns = [
                'Subject Code', 'Subject Title',
                'Lecture Hours', 'Tutorial Hours', 'Practical Hours', 'Blended Hours',
                'No of Lecture Weeks', 'No of Tutorial Weeks',
                'No of Practical Weeks', 'No of Blended Weeks', 'Head'
            ]

            if list(df.columns) != expected_columns:
                msg = f"Incorrect headers in '{sheet_name}'. Expected: {expected_columns}, Found: {list(df.columns)}"
                logger.warning(f"{msg}")
                errors.append(msg)
                continue

            df.columns = expected_columns
            sheets_processed += 1

            for index, row in df.iterrows():
                subject_code = str(row['Subject Code']).strip()
                if pd.isna(subject_code) or not subject_code:
                    continue  # skip empty subject code

                head_name = str(row['Head']).strip()
                head = Head.query.filter_by(name=head_name).first()
                if not head and head_name:
                    msg = f"Row {index + 2} in '{sheet_name}': Head '{head_name}' not found in system."
                    errors.append(msg)
                    logger.warning(f"{msg}")
                    continue

                existing_subject = Subject.query.filter_by(subject_code=subject_code).first()
                if existing_subject:
                    subjects_to_update.append({
                        'instance': existing_subject,
                        'data': {
                            'subject_title': str(row['Subject Title']).strip().title(),
                            'subject_level': subject_level,
                            'lecture_hours': convert_hours_weeks(row['Lecture Hours']),
                            'tutorial_hours': convert_hours_weeks(row['Tutorial Hours']),
                            'practical_hours': convert_hours_weeks(row['Practical Hours']),
                            'blended_hours': convert_hours_weeks(row['Blended Hours']),
                            'lecture_weeks': convert_hours_weeks(row['No of Lecture Weeks']),
                            'tutorial_weeks': convert_hours_weeks(row['No of Tutorial Weeks']),
                            'practical_weeks': convert_hours_weeks(row['No of Practical Weeks']),
                            'blended_weeks': convert_hours_weeks(row['No of Blended Weeks']),
                            'head_id': head.head_id if head else None
                        }
                    })
                else:
                    subjects_to_add.append(Subject(
                        subject_code=subject_code,
                        subject_title=str(row['Subject Title']).strip().title(),
                        subject_level=subject_level,
                        lecture_hours=convert_hours_weeks(row['Lecture Hours']),
                        tutorial_hours=convert_hours_weeks(row['Tutorial Hours']),
                        practical_hours=convert_hours_weeks(row['Practical Hours']),
                        blended_hours=convert_hours_weeks(row['Blended Hours']),
                        lecture_weeks=convert_hours_weeks(row['No of Lecture Weeks']),
                        tutorial_weeks=convert_hours_weeks(row['No of Tutorial Weeks']),
                        practical_weeks=convert_hours_weeks(row['No of Practical Weeks']),
                        blended_weeks=convert_hours_weeks(row['No of Blended Weeks']),
                        head_id=head.head_id if head else None
                    ))

        # Validation summary
        if sheets_processed == 0 and not errors:
            logger.warning("All sheets empty or unreadable.")
            return jsonify({'success': False, 'message': 'All sheets are empty or contain no readable data.'})

        if errors:
            db.session.rollback()
            logger.error(f"{len(errors)} error(s) encountered. Aborting upload.")
            return jsonify({
                'success': False,
                'errors': errors,
                'message': 'Upload failed due to errors. No subjects were added or updated.'
            })
        
        # Database commit
        try:
            for sub in subjects_to_add:
                db.session.add(sub)
            for update in subjects_to_update:
                inst, data = update['instance'], update['data']
                for key, val in data.items():
                    setattr(inst, key, val)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database commit failed: {e}")
            return jsonify({'success': False, 'message': f"Database commit failed: {e}"})

        total_processed = len(subjects_to_add) + len(subjects_to_update)
        logger.info(f"Successfully processed {total_processed} subject(s).")
        return jsonify({'success': True, 'message': f"Successfully processed {total_processed} subject(s)."})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing file: {e}")
        return jsonify({'success': False, 'message': f"Error processing file: {e}"})

# ============================================================
# Get Subjects by Level
# ============================================================
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
        logger.error(f"Error getting subjects by level: {e}")
        return jsonify({'success': False, 'message': f"Error getting subjects by level: {e}", 'subjects': []})

# ============================================================
# Get Subject Details
# ============================================================
@app.route('/get_subject_details/<subject_code>')
@handle_db_connection
def get_subject_details(subject_code):
    try:
        subject = Subject.query.filter_by(subject_code=subject_code).first()
        if not subject:
            logger.warning(f"Subject not found: {subject_code}")
            return jsonify({'success': False, 'message': 'Subject not found'})

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
        logger.error(f"Error getting subject details: {e}")
        return jsonify({'success': False, 'message': f"Error getting subject details: {e}"})
