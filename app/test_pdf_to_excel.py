import os
import logging
from app.extract_table_from_pdf import process_pdf_to_template
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)

def conversion(pdf_paths, school_centre, lecturer_name, designation, ic_number, course_details):
    # Assuming pdf_paths is a list of PDF file paths
    template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "files", "Part-Time Lecturer Requisition Form - template.xlsx")
    output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "outputs")  # Ensure this path is correct
    output_filename = f"{lecturer_name}.xlsx"

    # Assume hourly_rate is calculated or hardcoded
    hourly_rate = 60

    # Ensure course_details has the required structure
    formatted_course_details = []
    for course in course_details:
        formatted_course = {
            'program_level': course.get('program_level'),
            'subject_code': course.get('subject_code'),
            'subject_title': course.get('subject_title'),
            'weeks': max(int(course.get('lecture_weeks', 0)), int(course.get('tutorial_weeks', 0)), int(course.get('practical_weeks', 0))),
            'start_date': course.get('start_date'),
            'end_date': course.get('end_date'),
            'lecture_weeks': int(course.get('lecture_weeks', 0)),
            'tutorial_weeks': int(course.get('tutorial_weeks', 0)),
            'practical_weeks': int(course.get('practical_weeks', 0))
        }
        formatted_course_details.append(formatted_course)

    # Process the PDF(s) and save the filled Excel template
    output_excel_path = process_pdf_to_template(
        school_centre=school_centre,
        lecturer_name=lecturer_name,
        designation=designation,
        ic_number=ic_number,
        hourly_rate=hourly_rate,
        pdf_paths=pdf_paths,  # Correct argument name
        template_path=template_path,
        output_folder=output_folder,
        output_filename=output_filename,
        course_details=formatted_course_details  # Pass formatted course details
    )

    logging.info(f"Excel file created successfully at: {output_excel_path}")
    return os.path.basename(output_excel_path)
