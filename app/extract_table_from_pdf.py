import os
import logging
from openpyxl import load_workbook
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_ltp_values(pdf_path: str) -> Dict[str, int]:
    """
    Extract the L (Lecture), T (Tutorial), and P (Practical) values from the PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        Dict[str, int]: A dictionary with keys 'L', 'T', and 'P'.
    """
    logging.info(f"Extracting numeric values of L, T, and P from PDF: {pdf_path}")
    
    # Replace with actual PDF parsing logic.
    extracted_values = {
        'L': 28,  # Replace with extracted value
        'T': 0,   # Replace with extracted value
        'P': 26   # Replace with extracted value
    }
    
    return extracted_values

def insert_values_to_template(lecturer_name: str, designation: str, ic_number: str, courses: List[Dict], hourly_rate: int, template_path: str, output_path: str) -> None:
    """
    Insert the form and extracted data into the Excel template.
    
    Args:
        lecturer_name (str): The name of the lecturer.
        designation (str): The lecturer's designation.
        ic_number (str): The lecturer's IC number.
        courses (List[Dict]): A list of course details including L, T, P values.
        hourly_rate (int): The hourly rate of the lecturer.
        template_path (str): The path to the Excel template file.
        output_path (str): The path where the modified Excel file will be saved.
    """
    try:
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active

        # Insert lecturer details
        template_ws['C6'].value = lecturer_name
        template_ws['C7'].value = designation
        template_ws['H6'].value = ic_number
        template_ws['D20'].value = hourly_rate

        # Define the starting positions for each course
        row_mappings = [(10, 11, 13), (24, 25, 27), (38, 39, 41), (51, 52, 54)]

        # Insert course details and extracted L, T, P values
        for index, course in enumerate(courses):
            subject_title_row, subject_level_row, teaching_period_row = row_mappings[index]

            # Form data from input
            template_ws[f'C{subject_title_row}'].value = course['subject_title']
            template_ws[f'I{subject_title_row}'].value = course['subject_code']
            template_ws[f'C{subject_level_row}'].value = course['program_level']
            template_ws[f'C{teaching_period_row}'].value = f"From {course['start_date']} to {course['end_date']}"

            # L, T, P values from extracted PDF data
            if course['weeks'] > 0:
                template_ws[f'D{subject_title_row + 5}'].value = course['L'] / course['weeks']  # D15, D29, D43, D56
                template_ws[f'D{subject_title_row + 6}'].value = course['T'] / course['weeks']  # D16, D30, D44, D57
                template_ws[f'D{subject_title_row + 8}'].value = course['P'] / course['weeks']  # D18, D32, D46, D59
            
            template_ws[f'D{subject_title_row + 7}'].value = 1  # Hardcoded Blended Learning (D17, D31, D45, D58)

        # Save the modified template as a new Excel file
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        template_wb.save(output_path)
        logging.info(f"Excel template filled and saved successfully at {output_path}")
    except Exception as e:
        logging.error(f"An error occurred while filling the Excel template: {e}")
        raise

def process_pdf_to_template(lecturer_name: str, designation: str, ic_number: str, hourly_rate: int, pdf_paths: List[str], template_path: str, output_folder: str, output_filename: str, course_details: List[Dict]) -> str:
    """
    Process PDFs to extract L, T, and P values and insert them into the Excel template.
    
    Args:
        lecturer_name (str): Name of the lecturer.
        designation (str): Designation level.
        ic_number (str): The IC number of the lecturer.
        hourly_rate (int): Hourly rate.
        pdf_paths (List[str]): Paths to the PDF files.
        template_path (str): Path to the Excel template.
        output_folder (str): Folder to save the output file.
        output_filename (str): Name of the output Excel file.
        course_details (List[Dict]): Details of each course (program level, subject title, code, etc.)
    
    Returns:
        str: The path to the saved Excel file.
    """
    courses = []

    # Extract L, T, P values for each PDF and combine with course details
    for pdf_path, course_info in zip(pdf_paths, course_details):
        ltp_values = extract_ltp_values(pdf_path)

        # Combine form data with extracted values
        course_info['L'] = ltp_values['L']
        course_info['T'] = ltp_values['T']
        course_info['P'] = ltp_values['P']
        courses.append(course_info)

    output_excel_path = os.path.join(output_folder, output_filename)

    # Insert form data and L, T, P values into the Excel template
    insert_values_to_template(lecturer_name, designation, ic_number, courses, hourly_rate, template_path, output_excel_path)
    
    return output_excel_path
