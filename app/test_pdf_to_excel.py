import os
import logging
from app.extract_table_from_pdf import extract_ltp_values, insert_values_to_template, process_pdf_to_template
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)

def conversion(file_name):
    # Paths for testing
    sample_pdf_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], file_name)
    template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "files", "Part-Time Lecturer Requisition Form - template.xlsx")
    output_folder = "coursepdfextractor/outputs"
    
    # Specify the output filename
    output_filename = file_name + ".xlsx"

    # Process the PDF and save the filled Excel template
    output_excel_path = process_pdf_to_template(sample_pdf_path, template_path, output_folder, output_filename)

    if output_excel_path:
        logging.info(f"Excel template filled and saved at: {output_excel_path}")
    else:
        logging.warning("Failed to create the filled Excel template.")
