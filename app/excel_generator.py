import os, logging, pytz
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from copy import copy
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# Convert a date object to DD/MM/YYYY format
def format_date(date_obj):
    try:
        return date_obj.strftime('%d/%m/%Y') if date_obj else ''
    except Exception as e:
        logging.error(f"Date formatting error: {e}")
        return ''

def get_local_date_str(timezone_str='Asia/Kuala_Lumpur'):
    tz = pytz.timezone(timezone_str)
    now = datetime.now(tz)
    return now.strftime('%d/%m/%Y')

def generate_requisition_excel(department_code, name, designation, ic_number, course_details, po_name, head_name, dean_name, ad_name, hr_name):
    try:
        # Load template and define paths
        template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                   "files", 
                                   "Part-Time Lecturer Requisition Form - template.xlsx")
        output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "temp")
        output_filename = f"Part-Time Lecturer Requisition Form - {name}.xlsx"
        output_path = os.path.join(output_folder, output_filename)

        # Ensure the output directory exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Load the workbook and active sheet
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active

        # Insert lecturer and department details
        template_ws['C5'].value = department_code
        template_ws['C6'].value = name
        template_ws['C7'].value = designation
        template_ws['H6'].value = ic_number

        # Store the template of the first course record (A9:L22)
        first_record_template = []
        for row in range(9, 23):
            row_data = []
            for col in range(1, 13):  # Columns A to L
                cell = template_ws.cell(row=row, column=col)
                row_data.append({
                    'value': cell.value,
                    'style': copy(cell._style),
                    'formula': cell.value if isinstance(cell.value, str) and cell.value.startswith('=') else None
                })
            first_record_template.append(row_data)

        # Track total cost cells to later calculate grand total
        total_cost_cells = ['I20']  # First record's total cost cell

        # Process each course in course_details
        for index, course in enumerate(course_details):
            if index == 0:
                # Use existing template space for the first course
                insert_record(template_ws, course, 9)
            else:
                # Determine row to insert new course
                insert_point = 23 + (14 * (index - 1))
                
                # Insert 14 new rows for the new course section
                template_ws.insert_rows(insert_point, 14)
                
                # Copy layout and styles from the first template block
                copy_record_structure(template_ws, first_record_template, insert_point)
                
                # Fill in course data
                insert_record(template_ws, course, insert_point)
                
                # Update formulas for cost in new section
                update_record_formulas(template_ws, insert_point)
                
                # Add this course's cost cell to the list
                total_cost_cells.append(f'I{insert_point + 11}')

        # Write total cost formula summing all tracked cells
        final_total_row = 23 + (14 * (len(course_details) - 1))
        template_ws[f'I{final_total_row}'].value = f'=SUM({",".join(total_cost_cells)})'

        # Maps for determining where to insert final signature block
        row_map = {1: 29, 2: 43, 3: 57, 4: 71}
        merge_row_map = {1: 27, 2: 41, 3: 55, 4: 69}
        num_courses = len(course_details)
        start_row = row_map.get(num_courses)
        merge_row = merge_row_map.get(num_courses)

        # Insert and style signature blocks if applicable
        if start_row and merge_row:
            # Merge and center cells for signature layout
            template_ws.merge_cells(f'B{merge_row}:B{merge_row + 1}')
            template_ws.merge_cells(f'E{merge_row}:E{merge_row + 1}')
            template_ws.merge_cells(f'G{merge_row}:G{merge_row + 1}')
            template_ws.merge_cells(f'I{merge_row}:I{merge_row + 1}')
            template_ws.merge_cells(f'K{merge_row}:K{merge_row + 1}')

            # Center align the merged cells
            for col in ['B', 'E', 'G', 'I', 'K']:
                cell = template_ws[f'{col}{merge_row}']
                cell.alignment = Alignment(horizontal='center', vertical='center')

            # Populate signature block with names and date
            template_ws[f'B{start_row}'].value = f"Name: {po_name}"
            template_ws[f'B{start_row + 1}'].value = f"Date: {get_local_date_str()}"
            template_ws[f'E{start_row}'].value = f"Name: {head_name}"
            template_ws[f'G{start_row}'].value = f"Name: {dean_name}"
            template_ws[f'I{start_row}'].value = f"Name: {ad_name}"
            template_ws[f'K{start_row}'].value = f"Name: {hr_name}"

        # Protect the worksheet to make it read-only
        template_ws.protection.sheet = True
        
        # Save the final output Excel file
        template_wb.save(output_path)
        return output_path, merge_row

    except Exception as e:
        logging.error(f"Error generating Excel file: {e}")
        raise

# Copy the record structure from the template to a new location in the worksheet
def copy_record_structure(ws, template_data, start_row):
    try:
        # Loop through each row in the stored template data
        for row_idx, row_data in enumerate(template_data):
            target_row = start_row + row_idx   # Determine target row number
            
            # Loop through each column (cell) in the current row
            for col_idx, cell_data in enumerate(row_data, start=1):
                target_cell = ws.cell(row=target_row, column=col_idx)
                
                # Copy value only if it's not a formula (formulas will be set separately)
                if cell_data['value'] and not cell_data['formula']:
                    target_cell.value = cell_data['value']
                
                # Apply the original cell style
                target_cell._style = copy(cell_data['style'])
                
        logging.info(f"Successfully copied record structure to row {start_row}")
        
    except Exception as e:
        logging.error(f"Error copying record structure: {e}")
        raise

# Insert course details into the Excel worksheet
def insert_record(ws, course, start_row):
    try:
        # Calculate row positions relative to start_row
        subject_title_row = start_row + 1  # Row 10 for first record
        subject_level_row = start_row + 2  # Row 11 for first record
        teaching_period_row = start_row + 4  # Row 13 for first record
        
        # Category rows (Lecture, Tutorial, Practical, Blended)
        category_start = start_row + 6  # Row 15 for first record
        
        # Insert basic course information
        ws[f'C{subject_title_row}'].value = course['subject_title']
        ws[f'I{subject_title_row}'].value = course['subject_code']
        ws[f'C{subject_level_row}'].value = course['subject_level']
        
        # Insert teaching period dates
        start_date = format_date(course['start_date'])
        end_date = format_date(course['end_date'])
        ws[f'C{teaching_period_row}'].value = f"From {start_date} to {end_date}"
        
        # Insert teaching hours
        ws[f'D{category_start}'].value = course['lecture_hours']
        ws[f'D{category_start + 1}'].value = course['tutorial_hours']
        ws[f'D{category_start + 2}'].value = course['blended_hours']
        ws[f'D{category_start + 3}'].value = course['practical_hours']
        
        # Insert teaching weeks
        ws[f'G{category_start}'].value = course['lecture_weeks']
        ws[f'G{category_start + 1}'].value = course['tutorial_weeks']
        ws[f'G{category_start + 2}'].value = course['blended_weeks']
        ws[f'G{category_start + 3}'].value = course['practical_weeks']
        
        # Insert hourly rate
        ws[f'D{start_row + 11}'].value = course['hourly_rate']  # Row 20 for first record
        
        logging.info(f"Successfully inserted course data starting at row {start_row}")
        
    except Exception as e:
        logging.error(f"Error inserting record: {e}")
        raise

# Update Excel formulas for a record block
def update_record_formulas(ws, start_row):
    try:
        # Calculate formula positions
        category_start = start_row + 6  # Row 15 for first record (categories start)
        total_row = start_row + 11      # Row 20 for first record (totals row)
        
        # Update category total formulas (hours × weeks)
        # Example: For first record, updates I15 to I18
        for i in range(4):  # 4 categories: Lecture, Tutorial, Practical, Blended
            row = category_start + i
            # Formula: hours × weeks (e.g., =D15*G15)
            ws[f'I{row}'].value = f'=D{row}*G{row}'
        
        # Update total hours formula
        # Example: For first record, G20 = SUM(I15:I18)
        ws[f'G{total_row}'].value = f'=SUM(I{category_start}:I{category_start+3})'
        
        # Update total cost formula
        # Example: For first record, J20 = D20*G20
        ws[f'I{total_row}'].value = f'=D{total_row}*G{total_row}'
        
        logging.info(f"Successfully updated formulas starting at row {start_row}")
        
    except Exception as e:
        logging.error(f"Error updating record formulas: {e}")
        raise


def generate_claim_excel(name, department_code, subject_level, subject_code, hourly_rate, claim_details, remaining_lecture, remaining_tutorial, remaining_practical, remaining_blended, dean_name, hr_name):
    try:
        # Load template
        template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                   "files", 
                                   "Part-Time Lecturer Claim Form - template.xlsx")
        output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "temp")
        output_filename = f"Part-Time Lecturer Claim Form - {name}.xlsx"
        output_path = os.path.join(output_folder, output_filename)

        # Ensure output directory exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Load workbook
        template_wb = load_workbook(template_path)
        template_ws = template_wb.active

        # Insert lecturer details
        template_ws['B5'].value = name
        template_ws['B6'].value = name
        template_ws['B7'].value = department_code
        template_ws['B8'].value = subject_level
        template_ws['B9'].value = subject_code
        template_ws['B10'].value = hourly_rate

        # Insert claim details starting from row 14
        start_row = 14
        max_rows = 15

        for index, claim in enumerate(claim_details[:max_rows]):
            row = start_row + index
            template_ws[f"A{row}"].value = claim['date']
            template_ws[f"B{row}"].value = claim['lecture_hours']
            template_ws[f"C{row}"].value = claim['tutorial_hours']
            template_ws[f"D{row}"].value = claim['practical_hours']
            template_ws[f"E{row}"].value = claim['blended_hours']
            template_ws[f"F{row}"].value = claim['remarks']

        # Insert total claimed hours formulas
        template_ws["B29"] = "=SUM(B14:B28)"
        template_ws["C29"] = "=SUM(C14:C28)"
        template_ws["D29"] = "=SUM(D14:D28)"
        template_ws["E29"] = "=SUM(E14:E28)"

        # Insert rounded total payment formulas based on hourly rate
        template_ws["B34"] = "=ROUND(B10*B29, 2)"
        template_ws["B35"] = "=ROUND(B10*C29, 2)"
        template_ws["B36"] = "=ROUND(B10*D29, 2)"
        template_ws["B37"] = "=ROUND(B10*E29, 2)"

        # Insert grand total payment (sum of all above payments)
        template_ws["B38"] = "=SUM(B34:B37)"

        # Insert remaining hours
        template_ws["E34"] = remaining_lecture
        template_ws["E35"] = remaining_tutorial
        template_ws["E36"] = remaining_practical
        template_ws["E37"] = remaining_blended

        # Insert total remaining hours
        template_ws["E38"] = "=SUM(E34:E37)"

        # Insert remaining amount
        template_ws["F34"] = round(remaining_lecture * hourly_rate, 2)
        template_ws["F35"] = round(remaining_tutorial * hourly_rate, 2)
        template_ws["F36"] = round(remaining_practical * hourly_rate, 2)
        template_ws["F37"] = round(remaining_blended * hourly_rate, 2)

        # Insert total remaining amount
        template_ws["F38"] = "=SUM(F34:F37)"

        # Handle signature cells
        sign_col = 43
        name_col = 45

        # Merge the rows
        template_ws.merge_cells(f'A{sign_col}:A{sign_col + 1}')
        template_ws.merge_cells(f'C{sign_col}:C{sign_col + 1}')
        template_ws.merge_cells(f'F{sign_col}:F{sign_col + 1}')

        # Center align the merged cells
        for col in ['A', 'C', 'F']:
            cell = template_ws[f'{col}{sign_col}']  # Get the first cell of the merged range
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Fill values in correct cells
        template_ws[f'A{name_col}'].value = f"Name: {name}"
        template_ws[f'A{name_col + 2}'].value = f"Date: {get_local_date_str()}"
        template_ws[f'C{name_col}'].value = f"Name: {dean_name}"
        template_ws[f'F{name_col}'].value = f"Name: {hr_name}"

        # Protect the worksheet and make it read-only
        template_ws.protection.sheet = True
        
        # Save the file
        template_wb.save(output_path)
        return output_path, sign_col

    except Exception as e:
        logging.error(f"Error generating Excel file: {e}")
        raise