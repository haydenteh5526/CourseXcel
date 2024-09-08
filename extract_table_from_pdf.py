# import pdfplumber
# with pdfplumber.open("samplePDFs\DCS1101 updated230621.pdf") as f:
#     print(f.pages[0].extract_table())

import pdfplumber
import os
import pandas as pd
from typing import List, Dict, Any

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
    except Exception as e:
        print(f"An error occurred while processing the PDF: {str(e)}")
        return []
    
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
                df = pd.DataFrame(table[1:], columns=table[0])
                df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
        print(f"Excel file saved successfully at {output_path}")
    except Exception as e:
        print(f"An error occurred while creating the Excel file: {str(e)}")

if __name__ == "__main__":
    pdf_path = os.path.join("samplePDFs", "DCS1101 updated230621.pdf")
    excel_output_path = "output.xlsx"
    
    tables = extract_table_from_pdf(pdf_path)
    if tables:
        convert_tables_to_excel(tables, excel_output_path)
    else:
        print("No tables were extracted from the PDF.")