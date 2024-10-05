import os
import logging
from openpyxl import Workbook
from openpyxl import load_workbook
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_ltp_values(pdf_path: str) -> Dict[str, int]:
    logging.info(f"Extracting numeric values of L, T, and P from PDF: {pdf_path}")
    
    # Replace with actual implementation
    extracted_values = {
        'L': 28,
        'T': 0,
        'P': 26
    }
    
    return extracted_values

def insert_values_to_template(lecturer_name: str, designation: str, courses: List[Dict], hourly_rate: int, template_path: str, output_path: str) -> None:
    try:
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active

        # Insert lecturer details
        template_ws['C5'].value = lecturer_name
        template_ws['B6'].value = f"Name: {lecturer_name}"
        template_ws['G6'].value = "IC Number"  # Placeholder
        template_ws['B7'].value = f"Level: {designation}"
        template_ws['D20'].value = hourly_rate

        # Insert course details
        for index, course in enumerate(courses):
            row_offset = index * 10  # Modify as per template structure

            template_ws[f'C{10 + row_offset}'].value = course['subject_title']
            template_ws[f'I{10 + row_offset}'].value = course['subject_code']
            template_ws[f'C{11 + row_offset}'].value = course['program_level']
            template_ws[f'B{13 + row_offset}'].value = f"From {course['start_date']} to {course['end_date']}"

            if course['weeks'] > 0:
                template_ws[f'D{15 + row_offset}'].value = course['L'] / course['weeks']
                template_ws[f'D{16 + row_offset}'].value = course['T'] / course['weeks']
                template_ws[f'D{18 + row_offset}'].value = course['P'] / course['weeks']
            
            template_ws[f'D{17 + row_offset}'].value = 1  # Hardcoded Blended Learning

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        template_wb.save(output_path)
        logging.info(f"Excel template filled and saved successfully at {output_path}")
    except Exception as e:
        logging.error(f"An error occurred while filling the Excel template: {e}")
        raise

def process_pdf_to_template(lecturer_name, designation, hourly_rate, pdf_paths, template_path):
    # Load your template workbook
    template_wb = load_workbook(template_path)
    template_ws = template_wb.active

    # Populate template with necessary data (implement your logic here)

    # Instead of saving to disk, return the workbook object
    return template_wb

if __name__ == '__main__':
    sample_pdf_paths = [
        os.path.join("uploads", "DCS1101_sample.pdf"),
    ]
    template_path = os.path.join("files", "Part-Time Lecturer Requisition Form - template.xlsx")
    output_folder = "outputs"
    output_filename = "DCS1101_filled_template.xlsx"

    lecturer_name = "John Doe"
    designation = "II"
    hourly_rate = 60

    output_excel_path = process_pdf_to_template(lecturer_name, designation, hourly_rate, sample_pdf_paths, template_path, output_folder, output_filename)

    if output_excel_path:
        logging.info(f"Excel template filled and saved at: {output_excel_path}")
    else:
        logging.warning("Failed to create the filled Excel template.")
