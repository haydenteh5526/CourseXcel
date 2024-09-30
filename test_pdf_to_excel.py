import os
import logging
from coursepdfextractor.extract_table_from_pdf import extract_ltp_values, insert_values_to_template, process_pdf_to_template

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # Paths for testing
    sample_pdf_path = os.path.join("uploads", "DCS1101 updated230621.pdf")  # Ensure this file exists in 'uploads'
    template_path = os.path.join("uploads", "Part-Time Lecturer Requisition Form - template.xlsx")  # Path to your Excel template
    output_folder = "outputs"
    
    # Specify the output filename
    output_filename = "DCS1101_filled_template.xlsx"

    # Process the PDF and save the filled Excel template
    output_excel_path = process_pdf_to_template(sample_pdf_path, template_path, output_folder, output_filename)

    if output_excel_path:
        logging.info(f"Excel template filled and saved at: {output_excel_path}")
    else:
        logging.warning("Failed to create the filled Excel template.")
