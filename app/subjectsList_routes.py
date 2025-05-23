from flask import jsonify, request, current_app
from app import app, db
from app.models import Subject, subject_levels
import pandas as pd
import logging
from app.database import handle_db_connection

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
    records_added = 0
    errors = []
    warnings = []
    
    try:
        excel_file = pd.ExcelFile(file)
        
        for sheet_name in excel_file.sheet_names:
            current_app.logger.info(f"Processing sheet: {sheet_name}")
            subject_level = determine_subject_level(sheet_name)
            current_app.logger.info(f"Determined subject level: {subject_level}")
            
            try:
                df = pd.read_excel(
                    excel_file, 
                    sheet_name=sheet_name,
                    usecols="B:K",
                    skiprows=1
                )
                
                df.columns = [
                    'Subject Code', 'Subject Description',
                    'Lecture Hours', 'Tutorial Hours', 'Practical Hours', 'Blended Hours',
                    'No of Lecture Weeks', 'No of Tutorial Weeks',
                    'No of Practical Weeks', 'No of Blended Weeks'
                ]
                
                for index, row in df.iterrows():
                    try:
                        subject_code = str(row['Subject Code']).strip()
                        if pd.isna(subject_code) or not subject_code:
                            continue
                        
                        # Get or create subject
                        subject = Subject.query.get(subject_code)
                        
                        # If subject exists, update its fields
                        if subject:
                            subject.subject_title = str(row['Subject Description']).strip()
                            subject.lecture_hours = convert_hours(row['Lecture Hours'])
                            subject.tutorial_hours = convert_hours(row['Tutorial Hours'])
                            subject.practical_hours = convert_hours(row['Practical Hours'])
                            subject.blended_hours = convert_hours(row['Blended Hours'])
                            subject.lecture_weeks = convert_weeks(row['No of Lecture Weeks'])
                            subject.tutorial_weeks = convert_weeks(row['No of Tutorial Weeks'])
                            subject.practical_weeks = convert_weeks(row['No of Practical Weeks'])
                            subject.blended_weeks = convert_weeks(row['No of Blended Weeks'])
                            records_added += 1
                        else:
                            # Create new subject if it doesn't exist
                            subject = Subject(
                                subject_code=subject_code,
                                subject_title=str(row['Subject Description']).strip(),
                                lecture_hours=convert_hours(row['Lecture Hours']),
                                tutorial_hours=convert_hours(row['Tutorial Hours']),
                                practical_hours=convert_hours(row['Practical Hours']),
                                blended_hours=convert_hours(row['Blended Hours']),
                                lecture_weeks=convert_weeks(row['No of Lecture Weeks']),
                                tutorial_weeks=convert_weeks(row['No of Tutorial Weeks']),
                                practical_weeks=convert_weeks(row['No of Practical Weeks']),
                                blended_weeks=convert_weeks(row['No of Blended Weeks'])
                            )
                            db.session.add(subject)
                            records_added += 1
                        
                        # Handle subject levels - always add the level
                        level_exists = db.session.query(subject_levels).filter_by(
                            subject_code=subject_code,
                            level=subject_level
                        ).first() is not None
                        
                        if not level_exists:
                            db.session.execute(
                                subject_levels.insert().values(
                                    subject_code=subject_code,
                                    level=subject_level
                                )
                            )
                        
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
            'message': f'Successfully processed {records_added} subject(s)'
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

@app.route('/get_subjects_by_level/<subject_level>')
@handle_db_connection
def get_subjects_by_level(subject_level):
    """Get subjects filtered by course level using the subject_levels association table"""
    try:
        # Join Subject with subject_levels table and filter by level
        subjects = db.session.query(Subject).\
            join(subject_levels, Subject.subject_code == subject_levels.c.subject_code).\
            filter(subject_levels.c.level == subject_level).\
            all()

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

@app.route('/save_subject', methods=['POST'])
@handle_db_connection
def save_subject():
    try:
        current_app.logger.info("Starting save_subject function")
        data = request.get_json()
        current_app.logger.debug(f"Received data: {data}")
        
        if not data:
            current_app.logger.error("No data received in request")
            return jsonify({
                'success': False,
                'message': 'No data received'
            })
            
        subject_code = data.get('subject_code')
        subject_levels_data = data.get('subject_levels', [])  # Store levels separately
        
        # First, handle the subject record
        try:
            # Create or update subject
            subject = Subject.query.get(subject_code)
            if subject:
                current_app.logger.info(f"Updating existing subject: {subject_code}")
                subject.subject_title = data.get('subject_title')
                subject.lecture_hours = convert_hours(data.get('lecture_hours', 0))
                subject.tutorial_hours = convert_hours(data.get('tutorial_hours', 0))
                subject.practical_hours = convert_hours(data.get('practical_hours', 0))
                subject.blended_hours = convert_hours(data.get('blended_hours', 0))
                subject.lecture_weeks = convert_weeks(data.get('lecture_weeks', 0))
                subject.tutorial_weeks = convert_weeks(data.get('tutorial_weeks', 0))
                subject.practical_weeks = convert_weeks(data.get('practical_weeks', 0))
                subject.blended_weeks = convert_weeks(data.get('blended_weeks', 0))
            else:
                current_app.logger.info(f"Creating new subject: {subject_code}")
                subject = Subject(
                    subject_code=subject_code,
                    subject_title=data.get('subject_title'),
                    lecture_hours=convert_hours(data.get('lecture_hours', 0)),
                    tutorial_hours=convert_hours(data.get('tutorial_hours', 0)),
                    practical_hours=convert_hours(data.get('practical_hours', 0)),
                    blended_hours=convert_hours(data.get('blended_hours', 0)),
                    lecture_weeks=convert_weeks(data.get('lecture_weeks', 0)),
                    tutorial_weeks=convert_weeks(data.get('tutorial_weeks', 0)),
                    practical_weeks=convert_weeks(data.get('practical_weeks', 0)),
                    blended_weeks=convert_weeks(data.get('blended_weeks', 0))
                )
                db.session.add(subject)
            
            # Commit the subject first to ensure it exists in the database
            db.session.commit()
            current_app.logger.info("Subject committed successfully")

            # Now handle the subject levels
            if subject_levels_data:
                current_app.logger.info("Processing subject levels")
                # Clear existing levels
                db.session.execute(
                    subject_levels.delete().where(
                        subject_levels.c.subject_code == subject_code
                    )
                )
                
                # Add new levels
                for level in subject_levels_data:
                    current_app.logger.debug(f"Adding level: {level}")
                    db.session.execute(
                        subject_levels.insert().values(
                            subject_code=subject_code,
                            level=level
                        )
                    )
                
                # Commit the levels
                db.session.commit()
                current_app.logger.info("Subject levels committed successfully")

            return jsonify({
                'success': True,
                'message': 'Subject saved successfully'
            })

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            raise

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving subject: {str(e)}")
        current_app.logger.exception("Full traceback:")
        return jsonify({
            'success': False,
            'message': f'Error saving subject: {str(e)}'
        })

@app.route('/update_subject', methods=['POST'])
@handle_db_connection
def update_subject():
    try:
        data = request.get_json()
        subject_code = data.get('subject_code')
        
        # Verify subject exists
        subject = Subject.query.get(subject_code)
        if not subject:
            return jsonify({
                'success': False,
                'message': 'Subject not found'
            })

        # Update subject fields
        subject.subject_title = data.get('subject_title')
        subject.lecture_hours = convert_hours(data.get('lecture_hours', 0))
        subject.tutorial_hours = convert_hours(data.get('tutorial_hours', 0))
        subject.practical_hours = convert_hours(data.get('practical_hours', 0))
        subject.blended_hours = convert_hours(data.get('blended_hours', 0))
        subject.lecture_weeks = convert_weeks(data.get('lecture_weeks', 0))
        subject.tutorial_weeks = convert_weeks(data.get('tutorial_weeks', 0))
        subject.practical_weeks = convert_weeks(data.get('practical_weeks', 0))
        subject.blended_weeks = convert_weeks(data.get('blended_weeks', 0))

        # Update subject levels if provided
        if 'subject_levels' in data:
            # Clear existing levels
            db.session.execute(
                subject_levels.delete().where(
                    subject_levels.c.subject_code == subject_code
                )
            )
            
            # Add new levels
            for level in data['subject_levels']:
                db.session.execute(
                    subject_levels.insert().values(
                        subject_code=subject_code,
                        level=level
                    )
                )

        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Subject updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating subject: {str(e)}'
        })
