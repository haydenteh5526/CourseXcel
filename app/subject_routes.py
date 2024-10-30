from flask import jsonify, request, session, current_app
from app import app, db
from app.models import Subject
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def convert_hours(value):
    if pd.isna(value) or value == 0 or value == '0':
        return 0
    try:
        if isinstance(value, str):
            value = value.lower()
            if 'x' in value:
                parts = value.split('x')
                return parts[0].strip()
        return value
    except (ValueError, IndexError):
        return 0

def convert_weeks(value):
    if pd.isna(value) or value == 0:
        return 0
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0

@app.route('/admin/upload-course-structure', methods=['POST'])
def upload_course_structure():
    """
    Handles uploading the course structure Excel file which includes program levels
    and other course-specific details
    """
    try:
        file = request.files['file']
        print("File received:", file.filename)

        # Read Excel file starting from column B
        df = pd.read_excel(file, usecols="B:K")
        
        current_app.logger.info(f"DataFrame columns found: {df.columns.tolist()}")

        required_columns = [
            'Subject Code', 'Subject Description', 
            'Lecture Hours', 'Tutorial Hours', 'Practical Hours', 'Blended Hours',
            'No of Lecture Weeks', 'No of Tutorial Weeks', 
            'No of Practical Weeks', 'No of Blended Weeks'
        ]

        # Validate columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'success': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400

        success_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                subject_code = str(row['Subject Code']).strip()
                if pd.isna(subject_code) or not subject_code:
                    continue

                # Find or create subject
                subject = Subject.query.filter_by(subject_code=subject_code).first()
                if not subject:
                    subject = Subject()
                    subject.subject_code = subject_code

                # Update subject details
                subject.subject_title = str(row['Subject Description']).strip()
                subject.lecture_hours = convert_hours(row['Lecture Hours'])
                subject.tutorial_hours = convert_hours(row['Tutorial Hours'])
                subject.practical_hours = convert_hours(row['Practical Hours'])
                subject.blended_hours = convert_hours(row['Blended Hours'])
                subject.lecture_weeks = convert_weeks(row['No of Lecture Weeks'])
                subject.tutorial_weeks = convert_weeks(row['No of Tutorial Weeks'])
                subject.practical_weeks = convert_weeks(row['No of Practical Weeks'])
                subject.blended_weeks = convert_weeks(row['No of Blended Weeks'])

                db.session.add(subject)
                success_count += 1

            except Exception as e:
                error_msg = f"Error processing row {index}: {str(e)}"
                current_app.logger.error(error_msg)
                errors.append(error_msg)

        db.session.commit()
        
        response_data = {
            'success': True,
            'message': f'Successfully processed {success_count} subjects',
            'records_added': success_count
        }
        if errors:
            response_data['warnings'] = errors
            
        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        error_msg = f"Error processing file: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

def import_subjects_from_excel(file, level):
    """
    Helper function to import subjects from Excel with a specific level
    Used when uploading subjects for a specific program level
    """
    try:
        df = pd.read_excel(file)
        
        for index, row in df.iterrows():
            subject = Subject(
                subject_code=row['Subject Code'],
                subject_title=row['Subject Description'],
                lecture_hours=convert_hours(row['Lecture Hours']),
                tutorial_hours=convert_hours(row['Tutorial Hours']),
                practical_hours=convert_hours(row['Practical Hours']),
                blended_hours=convert_hours(row['Blended Hours']),
                lecture_weeks=convert_weeks(row['No of Lecture Weeks']),
                tutorial_weeks=convert_weeks(row['No of Tutorial Weeks']),
                practical_weeks=convert_weeks(row['No of Practical Weeks']),
                blended_weeks=convert_weeks(row['No of Blended Weeks']),
                level=level
            )
            db.session.add(subject)
        
        db.session.commit()
        return True, "Subjects imported successfully"
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error importing subjects: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

@app.route('/admin/upload_subjects', methods=['POST'])
def upload_subjects():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    course_level = request.form.get('course_level')
    
    if not course_level:
        return jsonify({'success': False, 'message': 'Course level is required'})
    
    try:
        # Read all sheets from the Excel file
        excel_file = pd.ExcelFile(file)
        records_added = 0
        errors = []
        
        # Process each sheet in the Excel file
        for sheet_name in excel_file.sheet_names:
            current_app.logger.info(f"Processing sheet: {sheet_name}")
            
            # Read the current sheet
            df = pd.read_excel(
                excel_file, 
                sheet_name=sheet_name,
                usecols="B:K",  # Columns B through K
                skiprows=1  # Skip header row if needed
            )
            
            # Rename columns to match expected format
            df.columns = [
                'Subject Code', 'Subject Description',
                'Lecture Hours', 'Tutorial Hours', 'Practical Hours', 'Blended Hours',
                'No of Lecture Weeks', 'No of Tutorial Weeks',
                'No of Practical Weeks', 'No of Blended Weeks'
            ]
            
            # Process each row in the current sheet
            for index, row in df.iterrows():
                try:
                    subject_code = str(row['Subject Code']).strip()
                    if pd.isna(subject_code) or not subject_code:
                        continue
                    
                    current_app.logger.info(f"Processing subject: {subject_code}")
                    
                    # Create or update subject
                    subject = Subject.query.filter_by(subject_code=subject_code).first()
                    if not subject:
                        subject = Subject()
                        subject.subject_code = subject_code
                    
                    # Update subject details
                    subject.subject_title = str(row['Subject Description']).strip()
                    subject.course_level = course_level  # Use the selected course level
                    subject.lecture_hours = convert_hours(row['Lecture Hours'])
                    subject.tutorial_hours = convert_hours(row['Tutorial Hours'])
                    subject.practical_hours = convert_hours(row['Practical Hours'])
                    subject.blended_hours = convert_hours(row['Blended Hours'])
                    subject.lecture_weeks = convert_weeks(row['No of Lecture Weeks'])
                    subject.tutorial_weeks = convert_weeks(row['No of Tutorial Weeks'])
                    subject.practical_weeks = convert_weeks(row['No of Practical Weeks'])
                    subject.blended_weeks = convert_weeks(row['No of Blended Weeks'])
                    
                    db.session.add(subject)
                    records_added += 1
                    
                except Exception as e:
                    error_msg = f"Error in sheet {sheet_name}, row {index}: {str(e)}"
                    current_app.logger.error(error_msg)
                    errors.append(error_msg)
        
        db.session.commit()
        
        response_data = {
            'success': True,
            'message': f'Successfully processed {records_added} subjects for {course_level}',
            'records_added': records_added
        }
        if errors:
            response_data['warnings'] = errors
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error processing file: {str(e)}"
        current_app.logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg
        })

@app.route('/get_subjects', methods=['GET'])
def get_subjects():
    try:
        subjects = Subject.query.all()
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
        current_app.logger.error(f"Error getting subjects: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/get_subjects_by_level/<course_level>')
def get_subjects_by_level(course_level):
    """Get subjects filtered by course level for the main form dropdown"""
    try:
        subjects = Subject.query.filter_by(course_level=course_level).all()
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
        return jsonify({'success': False, 'message': error_msg})

@app.route('/get_subject_details/<subject_code>')
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
                'program_code': subject.program_code,
                'lecturer_id': subject.lecturer_id,
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

