import pdfplumber
import os
import pandas as pd
from typing import List, Any

def extract_table_from_pdf(pdf_path: str) -> List[List[Any]]:
    """
    Extract tables from a PDF file.

    Args:
    pdf_path (str): Path to the PDF file.

    Returns:
    List[List[Any]]: A list of tables, where each table is a list of rows.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    tables.append(table)
    except pdfplumber.PDFSyntaxError as e:
        print(f"Error parsing PDF: {str(e)}")
    except pdfplumber.PDFPasswordError as e:
        print(f"PDF is password protected: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred while processing the PDF: {str(e)}")

    return tables

def convert_tables_to_excel(tables: List[List[Any]], output_path: str) -> None:
    """
    Convert extracted tables to an Excel file.

    Args:
    tables (List[List[Any]]): A list of tables extracted from the PDF.
    output_path (str): Path where the Excel file will be saved.
    """
    if not tables:
        print("No tables found to convert.")
        return

    try:
        with pd.ExcelWriter(output_path) as writer:
            for i, table in enumerate(tables):
                # Convert each table into a DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])  # Use first row as headers
                df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
        print(f"Excel file saved successfully at {output_path}")
    except PermissionError:
        print(f"Permission denied: Unable to write to {output_path}")
    except Exception as e:
        print(f"An unexpected error occurred while creating the Excel file: {str(e)}")

def process_pdf_to_excel(pdf_path: str, output_folder: str) -> str:
    """
    Extract tables from a PDF file and convert them to an Excel file.

    Args:
    pdf_path (str): Path to the PDF file.
    output_folder (str): Folder where the Excel file will be saved.

    Returns:
    str: Path to the saved Excel file.
    """
    # Extract tables from the PDF
    tables = extract_table_from_pdf(pdf_path)
    
    # If tables are extracted, convert them to an Excel file
    if tables:
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output file path
        output_path = os.path.join(output_folder, "output.xlsx")
        
        # Convert tables to Excel
        convert_tables_to_excel(tables, output_path)
        
        return output_path
    
    # If no tables were found, return an empty string
    print("No tables were extracted from the PDF.")
    return ""

if __name__ == "__main__":
    pdf_path = os.path.join("samplePDFs", "DCS1101 updated230621.pdf")
    output_folder = "outputs"
    
    # Process the PDF and save the Excel file
    excel_output_path = process_pdf_to_excel(pdf_path, output_folder)
    
    if excel_output_path:
        print(f"Excel file created at: {excel_output_path}")
    else:
        print("No tables were extracted or converted.")
