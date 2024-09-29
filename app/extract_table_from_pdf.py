import pdfplumber
import os
import logging
from openpyxl import load_workbook
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_ltp_values(pdf_path: str) -> Tuple[int, int, int]:
    """
    Extract the numeric values for L (Lecture), T (Tutorial), and P (Practical) from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        Tuple[int, int, int]: A tuple containing the numeric values of L, T, and P.
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
                            return l_value, t_value, p_value

    except Exception as e:
        logging.error(f"An error occurred while processing the PDF: {e}")
        raise

    # If no values were found
    logging.warning("No numeric values for L, T, and P found in the PDF.")
    return l_value, t_value, p_value

def insert_values_to_template(l_value: int, t_value: int, p_value: int, hourly_rate: int, template_path: str, output_path: str) -> None:
    """
    Insert the extracted L, T, and P values into the provided Excel template while preserving formatting.
    
    Args:
        l_value (int): Numeric value for L (Lecture).
        t_value (int): Numeric value for T (Tutorial).
        p_value (int): Numeric value for P (Practical).
        hourly_rate (int): Numeric value for the hourly rate.
        template_path (str): Path to the Excel template file.
        output_path (str): Path to save the modified Excel file.
    """
    try:
        # Load the Excel template
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active

        # Get the divisor values from column G (cells G15, G16, and G18)
        g15_value = template_ws['G15'].value
        g16_value = template_ws['G16'].value
        g18_value = template_ws['G18'].value

        # Divide L, T, and P values by their respective divisors
        lecture_hours = l_value / g15_value if g15_value else l_value
        tutorial_hours = t_value / g16_value if g16_value else t_value
        practical_hours = p_value / g18_value if g18_value else p_value

        # Variables for additional fields to be inserted
        school_centre = "SOC"
        name = "John Doe"
        ic_number = "123456-78-9101"
        level = "I"
        subject_title = "Programming Fundamentals"
        subject_code = "DCS1101"
        subject_level = "Diploma"
        teaching_period = "From   1st August 2024   to   31st December 2024"

        # Insert the additional variables into the template
        template_ws['C5'].value = school_centre  # Insert School/Centre to C5
        template_ws['C6'].value = name  # Insert Name to C6
        template_ws['H6'].value = ic_number  # Insert IC Number to H6
        template_ws['C7'].value = (template_ws['C7'].value or "") + f" {level}"  # Append Level to C7
        template_ws['C10'].value = subject_title  # Insert Subject Title to C10
        template_ws['I10'].value = subject_code  # Insert Subject Code to I10
        template_ws['C11'].value = subject_level  # Insert Subject Level to C11
        template_ws['C13'].value = teaching_period  # Insert Teaching Period to C13

        # Insert L, T, and P values into the template
        template_ws['D15'].value = lecture_hours  # Insert Lecture value into D15
        template_ws['D16'].value = tutorial_hours  # Insert Tutorial value into D16
        template_ws['D17'].value = 1  # Hardcode Blended Learning to be 1
        template_ws['D18'].value = practical_hours  # Insert Practical value into D18
        template_ws['D20'].value = hourly_rate  # Insert hourly rate value into D20

        # Save the modified template as a new Excel file
        template_wb.save(output_path)
        logging.info(f"Excel template filled and saved successfully at {output_path}")
    except Exception as e:
        logging.error(f"An error occurred while filling the Excel template: {e}")
        raise

def process_pdf_to_template(pdf_path: str, template_path: str, output_folder: str, output_filename: str = "filled_template.xlsx") -> str:
    """
    Process the PDF to extract numeric L, T, and P values and insert them into an Excel template.
    
    Args:
        pdf_path (str): Path to the PDF file.
        template_path (str): Path to the Excel template file.
        output_folder (str): Folder where the modified Excel file will be saved.
        output_filename (str): Name of the output Excel file (default is "filled_template.xlsx").
    
    Returns:
        str: Path to the saved Excel file.
    """
    # Extract L, T, and P numeric values from the PDF
    l_value, t_value, p_value = extract_ltp_values(pdf_path)
    
    if l_value is not None and t_value is not None and p_value is not None:
        # Define hourly rate
        hourly_rate = 60

        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Define the output file path
        output_excel_path = os.path.join(output_folder, output_filename)
        
        # Insert the extracted values and other details into the Excel template
        insert_values_to_template(l_value, t_value, p_value, hourly_rate, template_path, output_excel_path)
        
        return output_excel_path

    logging.warning("No numeric L, T, and P values were extracted from the PDF.")
    return ""

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
