import base64, io, logging, os, pytz, re, requests
from app import app, db, mail
from app.database import handle_db_connection
from app.models import Department, Head
from flask import jsonify, render_template_string
from datetime import datetime, timezone
from flask_mail import Message
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as ExcelImage
from PIL import Image

# ============================================================
#  Utility Functions
# ============================================================
def get_current_utc():
    """Return current UTC time as a datetime object (for DB)."""
    return datetime.now(timezone.utc)

def format_utc(dt):
    """Convert a datetime object to Malaysia timezone and format as string."""
    if not dt:
        return None
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    return dt.astimezone(malaysia_tz).strftime('%a, %d %b %y, %I:%M:%S %p')

def get_drive_service():
    SERVICE_ACCOUNT_FILE = '/home/TomazHayden/coursexcel-459515-3d151d92b61f.json'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

# ============================================================
#  Google Drive Operations
# ============================================================
def download_from_drive(file_id):
    app.logger.info(f"[BACKEND] Downloading file from Drive: {file_id}")
    drive_service = get_drive_service()

    request = drive_service.files().export_media(
        fileId=file_id,
        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    output_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "temp")
    os.makedirs(output_folder, exist_ok=True)
    local_path = os.path.join(output_folder, f"{file_id}.xlsx")

    fh = io.FileIO(local_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        app.logger.debug(f"[BACKEND] Download progress: {int(status.progress() * 100)}%")

    fh.close()
    app.logger.info(f"[BACKEND] File downloaded successfully: {local_path}")
    return local_path

def upload_to_drive(file_path, file_name):
    app.logger.info(f"[BACKEND] Uploading file to Drive: {file_name}")
    try:
        drive_service = get_drive_service()

        file_metadata = {
            'name': file_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet'  # Convert to Google Sheets
        }

        media = MediaFileUpload(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            resumable=True
        )

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        # Make file publicly accessible
        drive_service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'},
        ).execute()

        file_id = file.get('id')
        file_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit"
        app.logger.info(f"[BACKEND] File uploaded successfully. ID: {file_id}")

        return file_url, file_id

    except Exception as e:
        app.logger.error(f"[BACKEND] Failed to upload to Google Drive: {e}")
        raise

# ============================================================
#  Signature Processing
# ============================================================
def save_signature_image(signature_data, approval_id, temp_folder):
    try:
        header, encoded = signature_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(binary_data))
        temp_image_path = os.path.join(temp_folder, f"signature_{approval_id}.png")
        image.save(temp_image_path)
        app.logger.debug(f"[BACKEND] Signature image saved: {temp_image_path}")
        return temp_image_path
    except Exception as e:
        app.logger.error(f"[BACKEND] Signature decoding error: {e}")
        return None

def insert_signature_and_date(local_excel_path, signature_path, cell_prefix, row, updated_path):
    app.logger.info(f"[BACKEND] Inserting signature and date at row {row}")
    wb = load_workbook(local_excel_path)
    ws = wb.active

    # Insert signature
    sign_cell = f"{cell_prefix}{row}"
    signature_img = ExcelImage(signature_path)
    signature_img.width = 100
    signature_img.height = 30
    ws.add_image(signature_img, sign_cell)

    # Insert date
    date_cell = f"{cell_prefix}{row + 3}"
    malaysia_time = datetime.now(pytz.timezone('Asia/Kuala_Lumpur'))
    ws[date_cell] = f"Date: {malaysia_time.strftime('%d/%m/%Y')}"

    wb.save(updated_path)
    app.logger.info(f"[BACKEND] Signature and date inserted, file saved: {updated_path}")

def process_signature_and_upload(approval, signature_data, col_letter):
    app.logger.info(f"[BACKEND] Processing signature for approval ID: {approval.approval_id}")
    temp_folder = os.path.join("temp")
    os.makedirs(temp_folder, exist_ok=True)

    temp_image_path = save_signature_image(signature_data, approval.approval_id, temp_folder)
    if not temp_image_path:
        raise ValueError("Invalid signature image data")

    local_excel_path = download_from_drive(approval.file_id)
    updated_excel_path = os.path.join(temp_folder, approval.file_name)

    try:
        insert_signature_and_date(local_excel_path, temp_image_path, col_letter, approval.sign_col, updated_excel_path)
        new_file_url, new_file_id = upload_to_drive(updated_excel_path, approval.file_name)

        # Delete old file if needed
        drive_service = get_drive_service()
        if approval.file_id and approval.file_id != new_file_id:
            try:
                drive_service.files().delete(fileId=approval.file_id).execute()
                app.logger.info(f"[BACKEND] Deleted old Drive file: {approval.file_id}")
            except Exception as e:
                app.logger.warning(f"[BACKEND] Failed to delete old file {approval.file_id}: {e}")
                
        # Update DB record
        approval.file_url = new_file_url
        approval.file_id = new_file_id
        approval.last_updated = get_current_utc()
        db.session.commit()

    finally:
        # Clean up temp files safely even if an exception occurs
        for path in [temp_image_path, local_excel_path, updated_excel_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    app.logger.debug(f"[BACKEND] Temp file removed: {path}")
            except Exception as e:
                app.logger.warning(f"[BACKEND] Failed to remove temp file {path}: {e}")

# ============================================================
#  Email Utility
# ============================================================
def send_email(recipients, subject, body, attachments=None):
    # attachments: list of dicts, each dict has keys: 'filename' and 'url'

    try:
        # Ensure recipients is always a list
        app.logger.info(f"[BACKEND] Preparing to send email to: {recipients}")
        if isinstance(recipients, str):
            recipients = [recipients]

        msg = Message(subject, recipients=recipients, body=body)

        # Attach files if any
        if attachments:
            for att in attachments:
                url = att.get('url')
                filename = att.get('filename', 'attachment.pdf')
                try:
                    # Normalize Google Drive link to direct download
                    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url or "")
                    if m:
                        file_id = m.group(1)
                        url = f"https://drive.google.com/uc?export=download&id={file_id}"

                    app.logger.info(f"[BACKEND] Fetching attachment: {filename} from {url}")
                    resp = requests.get(url, allow_redirects=True, timeout=15)
                    resp.raise_for_status()
                    msg.attach(filename, "application/pdf", resp.content)
                except Exception as e:
                    app.logger.error(f"[BACKEND] Failed to attach {filename} from {url}: {e}")

        mail.send(msg)
        app.logger.info("[BACKEND] Email sent successfully.")
        return True

    except Exception as e:
        app.logger.error(f"[BACKEND] Failed to send email: {e}")
        return False

# ============================================================
#  Approval Status Helpers
# ============================================================
def is_already_voided(approval):
    if "Voided" in approval.status:
        return render_template_string(f"""
            <h2 style="text-align: center; color: red;">This request has already been voided.</h2>
            <p style="text-align: center;">Status: {approval.status}</p>
        """)
    return None

def is_already_reviewed(approval, expected_statuses):
    if approval.status not in expected_statuses:
        return render_template_string(f"""
            <h2 style="text-align: center; color: red;">This request has already been reviewed.</h2>
            <p style="text-align: center;">Current Status: {approval.status}</p>
        """)
    return None

# ============================================================
#  API Routes
# ============================================================
@app.route('/get_departments')
@handle_db_connection
def get_departments():
    try:
        departments = Department.query.all()
        return jsonify({
            'success': True,
            'departments': [{'department_id': d.department_id, 
                            'department_code': d.department_code, 
                           'department_name': d.department_name} 
                          for d in departments]
        })
    except Exception as e:
        app.logger.error(f"[BACKEND] Error retrieving departments: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_heads')
@handle_db_connection
def get_heads():
    try:
        heads = Head.query.all()
        return jsonify({
            'success': True,
            'heads': [{'head_id': h.head_id,
                             'name': h.name} 
                          for h in heads]
        })
    except Exception as e:
        app.logger.error(f"[BACKEND] Error retrieving heads: {e}")
        return jsonify({'success': False, 'message': str(e)})
