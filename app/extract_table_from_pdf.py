import pdfplumber
import pandas as pd
import os
import logging
from typing import List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_table_from_pdf(pdf_path: str) -> List[List[Any]]:
    """
    Extract tables from a PDF file.
    
    Args:
    pdf_path (str): Path to the PDF file.
    
    Returns:
    List[List[Any]]: A list of rows extracted from the table(s) in the PDF.
    """
    logging.info(f"Extracting tables from PDF: {pdf_path}")

    # Check if the file exists
    if not os.path.exists(pdf_path):
        logging.error(f"The file {pdf_path} does not exist.")
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    tables = []
    try:
        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            logging.info(f"Opened PDF: {pdf_path}")
            # Iterate over all pages to extract tables
            for page_number, page in enumerate(pdf.pages, start=1):
                table = page.extract_table()
                if table:
                    logging.info(f"Table found on page {page_number}")
                    tables.extend(table)
                else:
                    logging.info(f"No table found on page {page_number}")
    except Exception as e:
        logging.error(f"An error occurred while processing the PDF: {e}")
        raise

    if tables:
        logging.info(f"Extracted {len(tables)} rows from the PDF.")
    else:
        logging.warning("No tables were found in the entire PDF.")

    return tables

def convert_tables_to_excel(tables: List[List[Any]], output_path: str) -> None:
    """
    Convert extracted tables to an Excel file.
    
    Args:
    tables (List[List[Any]]): A list of rows from the table(s) extracted from the PDF.
    output_path (str): Path to save the Excel file.
    """
    if not tables:
        logging.warning("No tables found to convert. Exiting without creating Excel file.")
        return

    try:
        # Convert tables to a DataFrame
        df = pd.DataFrame(tables[1:], columns=tables[0])  # Assume first row as header
        # Save DataFrame to Excel
        df.to_excel(output_path, index=False)
        logging.info(f"Excel file saved successfully at {output_path}")
    except Exception as e:
        logging.error(f"An error occurred while creating the Excel file: {e}")
        raise

def process_pdf_to_excel(pdf_path: str, output_folder: str) -> str:
    """
    Process the PDF to extract tables and convert them to an Excel file.
    
    Args:
    pdf_path (str): Path to the PDF file.
    output_folder (str): Folder where the Excel file will be saved.
    
    Returns:
    str: Path to the saved Excel file.
    """
    # Extract tables from the PDF
    tables = extract_table_from_pdf(pdf_path)
    
    if tables:
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Define the output file path
        output_excel_path = os.path.join(output_folder, "output.xlsx")
        
        # Convert tables to Excel
        convert_tables_to_excel(tables, output_excel_path)
        
        return output_excel_path

    logging.warning("No tables were extracted from the PDF.")
    return ""

if __name__ == '__main__':
    # Sample paths for testing
    sample_pdf_path = os.path.join("uploads", "sample.pdf")  # Make sure this file exists
    output_folder = "outputs"

    # Process the PDF and save the Excel file
    output_excel_path = process_pdf_to_excel(sample_pdf_path, output_folder)

    if output_excel_path:
        logging.info(f"Excel file created at: {output_excel_path}")
    else:
        logging.warning("No Excel file was created.")
