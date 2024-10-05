import os
import logging
from app.extract_table_from_pdf import process_pdf_to_template
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)

def conversion(file_name, lecturer_name, designation):
    # Paths for processing
    sample_pdf_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], file_name)
    template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "files", "Part-Time Lecturer Requisition Form - template.xlsx")
    output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "outputs")
    output_filename = f"{file_name}.xlsx"

    # Assume hourly_rate is calculated or hardcoded
    hourly_rate = 60

    # Process the PDF and save the filled Excel template
    output_excel_path = process_pdf_to_template(lecturer_name, designation, hourly_rate, [sample_pdf_path], template_path, output_folder, output_filename)

    return output_filename
