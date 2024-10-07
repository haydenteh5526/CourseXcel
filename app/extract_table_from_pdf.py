import pdfplumber
import os
import logging
from openpyxl import load_workbook
from typing import List, Dict
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_ltp_values(pdf_path: str) -> Dict[str, int]:
    """
    Extract the numeric values for L (Lecture), T (Tutorial), and P (Practical) from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        Dict[str, int]: A dictionary with keys 'L', 'T', and 'P'.
    """
    logging.info(f"Extracting numeric values of L, T, and P from PDF: {pdf_path}")

    # Check if the file exists
    if not os.path.exists(pdf_path):
        logging.error(f"The file {pdf_path} does not exist.")
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    l_value, t_value, p_value = None, None, None
    try:
        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            logging.info(f"Opened PDF: {pdf_path}")
            # Iterate over all pages to find the numeric values
            for page_number, page in enumerate(pdf.pages, start=1):
                table = page.extract_table()
                if table:
                    # Look for the row containing L, T, and P
                    for row in table:
                        if row and len(row) >= 3 and row[0].strip().upper() == 'L' and row[1].strip().upper() == 'T' and row[2].strip().upper() == 'P':
                            # The next row should contain the numeric values for L, T, and P
                            index = table.index(row)
                            l_value = int(table[index + 1][0])
                            t_value = int(table[index + 1][1])
                            p_value = int(table[index + 1][2])
                            logging.info(f"Extracted values - L: {l_value}, T: {t_value}, P: {p_value}")
                            return {'L': l_value, 'T': t_value, 'P': p_value}

    except Exception as e:
        logging.error(f"An error occurred while processing the PDF: {e}")
        raise

    # If no values were found
    logging.warning("No numeric values for L, T, and P found in the PDF.")
    return {'L': 0, 'T': 0, 'P': 0}  # Default to 0 if not found

def format_date(date_str: str) -> str:
    """
    Format date from YYYY-MM-DD to DD/MM/YYYY.
    
    Args:
        date_str (str): Date in the format YYYY-MM-DD.
    
    Returns:
        str: Date in the format DD/MM/YYYY.
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError:
        return date_str

def insert_values_to_template(school_centre: str, lecturer_name: str, designation: str, ic_number: str, courses: List[Dict], hourly_rate: int, template_path: str, output_path: str) -> None:
    try:
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active

        # Insert lecturer details
        template_ws['C5'].value = school_centre
        template_ws['C6'].value = lecturer_name
        template_ws['C7'].value = designation
        template_ws['H6'].value = ic_number

        # Define the starting positions for each course
        row_mappings = [(10, 11, 13, 15, 16, 17, 18, 20),  # (Subject title, level, period, lecture, tutorial, blended, practical, hourly rate)
                        (24, 25, 27, 29, 30, 31, 32, 34),
                        (38, 39, 41, 43, 44, 45, 46, 48),
                        (51, 52, 54, 56, 57, 58, 59, 61)]

        # Insert course details and extracted L, T, P values
        for index, course in enumerate(courses):
            subject_title_row, subject_level_row, teaching_period_row, lecture_row, tutorial_row, blended_row, practical_row, hourly_row = row_mappings[index]

            # Form data from input
            template_ws[f'C{subject_title_row}'].value = course['subject_title']
            template_ws[f'I{subject_title_row}'].value = course['subject_code']
            template_ws[f'C{subject_level_row}'].value = course['program_level']
            
            # Format the dates to DD/MM/YYYY
            start_date = format_date(course['start_date'])
            end_date = format_date(course['end_date'])
            template_ws[f'C{teaching_period_row}'].value = f"From {start_date} to {end_date}"

            # Insert form weeks data
            template_ws[f'G{lecture_row}'].value = course['lecture_weeks']
            template_ws[f'G{tutorial_row}'].value = course['tutorial_weeks']
            template_ws[f'G{blended_row}'].value = 14  # Hardcoded blended learning value
            template_ws[f'G{practical_row}'].value = course['practical_weeks']

            # Insert hourly rate
            template_ws[f'D{hourly_row}'].value = hourly_rate

            # Calculate and insert L, T, P values into Excel template
            template_ws[f'D{lecture_row}'].value = course['L'] / course['lecture_weeks'] if course['lecture_weeks'] > 0 else 0
            template_ws[f'D{tutorial_row}'].value = course['T'] / course['tutorial_weeks'] if course['tutorial_weeks'] > 0 else 0
            template_ws[f'D{blended_row}'].value = 1  # Hardcoded blended learning value
            template_ws[f'D{practical_row}'].value = course['P'] / course['practical_weeks'] if course['practical_weeks'] > 0 else 0

        # Save the modified template as a new Excel file
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        template_wb.save(output_path)
        logging.info(f"Excel template filled and saved successfully at {output_path}")
    except Exception as e:
        logging.error(f"An error occurred while filling the Excel template: {e}")
        raise

def process_pdf_to_template(school_centre: str, lecturer_name: str, designation: str, ic_number: str, hourly_rate: int, pdf_paths: List[str], template_path: str, output_folder: str, output_filename: str, course_details: List[Dict]) -> str:
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
    insert_values_to_template(school_centre, lecturer_name, designation, ic_number, courses, hourly_rate, template_path, output_excel_path)
    
    return output_excel_path
