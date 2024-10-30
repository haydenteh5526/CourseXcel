import os
import logging
from openpyxl import load_workbook
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

def format_date(date_str):
    """Convert date string to DD/MM/YYYY format"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except ValueError as e:
        logging.error(f"Date format error: {e}")
        return date_str

def generate_excel(school_centre, lecturer_name, designation, ic_number, course_details):
    try:
        # Load template
        template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                   "files", 
                                   "Part-Time Lecturer Requisition Form - template.xlsx")
        output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "outputs")
        output_filename = f"{lecturer_name}.xlsx"
        output_path = os.path.join(output_folder, output_filename)

        # Ensure output directory exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Load workbook
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active

        # Insert lecturer details from form
        template_ws['C5'].value = school_centre
        template_ws['C6'].value = lecturer_name
        template_ws['C7'].value = designation
        template_ws['H6'].value = ic_number

        # Define row mappings for each course
        row_mappings = [
            (10, 11, 13, 15, 16, 17, 18, 20),  # First course
            (24, 25, 27, 29, 30, 31, 32, 34),  # Second course
            (38, 39, 41, 43, 44, 45, 46, 48),  # Third course
            (51, 52, 54, 56, 57, 58, 59, 61)   # Fourth course
        ]

        # Default hourly rate
        hourly_rate = 60

        # Insert course details from form
        for index, course in enumerate(course_details):
            if index >= len(row_mappings):
                break  # Don't exceed template capacity
                
            subject_title_row, subject_level_row, teaching_period_row, lecture_row, tutorial_row, blended_row, practical_row, hourly_row = row_mappings[index]

            # Insert course details from form
            template_ws[f'C{subject_title_row}'].value = course['subject_title']
            template_ws[f'I{subject_title_row}'].value = course['subject_code']
            template_ws[f'C{subject_level_row}'].value = course['program_level']
            
            # Format and insert dates from form
            start_date = format_date(course['start_date'])
            end_date = format_date(course['end_date'])
            template_ws[f'C{teaching_period_row}'].value = f"From {start_date} to {end_date}"

            # Insert weeks data from form
            lecture_weeks = int(course['lecture_weeks'])
            tutorial_weeks = int(course['tutorial_weeks'])
            practical_weeks = int(course['practical_weeks'])
            elearning_weeks = int(course.get('elearning_weeks', 14))  # Default to 14 if not provided

            template_ws[f'G{lecture_row}'].value = lecture_weeks
            template_ws[f'G{tutorial_row}'].value = tutorial_weeks
            template_ws[f'G{blended_row}'].value = elearning_weeks
            template_ws[f'G{practical_row}'].value = practical_weeks

            # Insert hourly rate from form data
            template_ws[f'D{hourly_row}'].value = course['hourly_rate']  # Update this line

            # Calculate and insert hours per week from form data
            template_ws[f'D{lecture_row}'].value = int(course['lecture_hours']) if 'lecture_hours' in course else 0
            template_ws[f'D{tutorial_row}'].value = int(course['tutorial_hours']) if 'tutorial_hours' in course else 0
            template_ws[f'D{blended_row}'].value = int(course['elearning_hours']) if 'elearning_hours' in course else 1
            template_ws[f'D{practical_row}'].value = int(course['practical_hours']) if 'practical_hours' in course else 0

        # Save the file
        template_wb.save(output_path)
        logging.info(f"Excel file generated successfully at: {output_path}")
        return output_filename

    except Exception as e:
        logging.error(f"Error generating Excel file: {e}")
        raise
