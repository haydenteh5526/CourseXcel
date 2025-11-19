import io, logging, os, re, zipfile
from app import app, db
from app.database import handle_db_connection
from app.excel_generator import generate_report_excel
from app.models import Admin, ClaimApproval, ClaimAttachment, ClaimReport, Department, Head, Lecturer, LecturerClaim, LecturerSubject, Other, ProgramOfficer, Rate, RequisitionApproval, RequisitionAttachment, RequisitionReport, Subject 
from app.shared_routes import delete_requisition_and_attachment, get_current_utc, get_drive_service, send_email, upload_to_drive
from datetime import date, datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from flask import jsonify, redirect, render_template, request, send_file, session, url_for
from flask_bcrypt import Bcrypt
from io import BytesIO
from googleapiclient.http import MediaIoBaseDownload
from openpyxl import load_workbook
from openpyxl.workbook.protection import WorkbookProtection
from openpyxl.utils.protection import hash_password
from sqlalchemy import desc, extract, func
from sqlalchemy.orm import joinedload

bcrypt = Bcrypt()
logger = logging.getLogger(__name__)

# Configurations
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/adminHomepage', methods=['GET', 'POST'])
@handle_db_connection
def adminHomepage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    admin = Admin.query.get(session.get('admin_id'))
    departments = Department.query.all() 

    # Subject counts per lecturer
    lecturer_subject_counts = (
        db.session.query(
            Lecturer.department_id,
            Lecturer.name,
            func.count(LecturerSubject.subject_id).label("subject_count")
        )
        .join(LecturerSubject, Lecturer.lecturer_id == LecturerSubject.lecturer_id)
        .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
        .filter(RequisitionApproval.status == "Completed")   # only completed requisitions
        .group_by(Lecturer.department_id, Lecturer.name)
        .all()
    )

    # Convert to dict by department
    dept_subjects = {}
    for dept_id, lecturer_name, subject_count in lecturer_subject_counts:
        dept_subjects.setdefault(dept_id, []).append({
            "lecturer": lecturer_name,
            "count": subject_count
        })

    # Aggregate claims: sum per department per year+month
    claim_trends = (
        db.session.query(
            Lecturer.department_id,
            extract('year', LecturerClaim.date).label('year'),
            extract('month', LecturerClaim.date).label('month'),
            func.sum(LecturerClaim.total_cost).label("total_claims")
        )
        .join(Lecturer, Lecturer.lecturer_id == LecturerClaim.lecturer_id)
        .join(ClaimApproval, LecturerClaim.claim_id == ClaimApproval.approval_id)
        .filter(ClaimApproval.status == "Completed")   # only completed claims
        .group_by(Lecturer.department_id,
                extract('year', LecturerClaim.date),
                extract('month', LecturerClaim.date))
        .all()
    )

    # Convert to nested dict: dept → year → list
    dept_claims = {}
    for dept_id, year, month, total_claims in claim_trends:
        dept_claims.setdefault(dept_id, {}).setdefault(int(year), []).append({
            "month": int(month),
            "total_claims": float(total_claims)
        })

    # Aggregate claims: sum per department per month/year
    dept_map = {d.department_id: d.department_code for d in departments}

    # Aggregate claims: sum per department per month/year
    peak_claims = (
        db.session.query(
            Lecturer.department_id,
            extract('year', LecturerClaim.date).label('year'),
            extract('month', LecturerClaim.date).label('month'),
            func.sum(LecturerClaim.total_cost).label("total_claims")
        )
        .join(Lecturer, Lecturer.lecturer_id == LecturerClaim.lecturer_id)
        .join(ClaimApproval, LecturerClaim.claim_id == ClaimApproval.approval_id)
        .filter(ClaimApproval.status == "Completed")   # only completed claims
        .group_by(Lecturer.department_id,
                extract('year', LecturerClaim.date),
                extract('month', LecturerClaim.date))
        .all()
    )

    # Convert to dict by year → then filter top 6 months
    year_claims = {}
    for dept_id, year, month, total_claims in peak_claims:
        year = int(year)
        year_claims.setdefault(year, []).append({
            "department_id": dept_id,
            "month": int(month),
            "total_claims": float(total_claims)
        })

    # Keep only the highest 6 months per year
    for year, entries in year_claims.items():
        # Sum claims across departments per month
        monthly_totals = {}
        for e in entries:
            monthly_totals[e["month"]] = monthly_totals.get(e["month"], 0) + e["total_claims"]

        # Get top 6 months by total claims
        top_months = sorted(monthly_totals.items(), key=lambda x: x[1], reverse=True)[:6]
        top_months_set = {m for m, _ in top_months}

        # Filter entries to only keep those months
        year_claims[year] = [e for e in entries if e["month"] in top_months_set]

    # Count queries
    records_counts = [
        Department.query.count(),
        Subject.query.count(),
        ProgramOfficer.query.count(),
        Lecturer.query.count(),
        Head.query.count()
    ]

    return render_template('adminHomepage.html', admin_id=admin.admin_id, 
                           two_factor_enabled=admin.two_factor_enabled,
                           departments=departments,
                           dept_subjects=dept_subjects,
                           dept_claims=dept_claims,
                           dept_map=dept_map,
                           year_claims=year_claims,
                           records_counts=records_counts)
    
@app.route('/adminSubjectsPage', methods=['GET', 'POST'])
@handle_db_connection
def adminSubjectsPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'adminSubjectsPage_currentTab' not in session:
        session['adminSubjectsPage_currentTab'] = 'subjects'
        
    subjects = Subject.query.options(joinedload(Subject.head)).order_by(Subject.subject_code.asc()).all() 
    departments = Department.query.order_by(Department.department_name.asc()).all() 
    rates = Rate.query.order_by(Rate.amount.asc()).all() 

    return render_template('adminSubjectsPage.html', 
                           subjects=subjects,
                           departments=departments,
                           rates=rates)

@app.route('/set_adminSubjectsPage_tab', methods=['POST'])
def set_adminSubjectsPage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['adminSubjectsPage_currentTab'] = data.get('adminSubjectsPage_currentTab')
    return jsonify({'success': True})

@app.route('/adminUsersPage', methods=['GET', 'POST'])
@handle_db_connection
def adminUsersPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'adminUsersPage_currentTab' not in session:
        session['adminUsersPage_currentTab'] = 'lecturers'

    lecturers = Lecturer.query.order_by(Lecturer.name.asc()).all()        
    heads = Head.query.order_by(Head.name.asc()).all()
    programOfficers = ProgramOfficer.query.order_by(ProgramOfficer.name.asc()).all()
    others = Other.query.order_by(Other.name.asc()).all()

    return render_template('adminUsersPage.html', 
                           lecturers=lecturers, 
                           heads=heads,
                           programOfficers=programOfficers,
                           others=others)

@app.route('/set_adminUsersPage_tab', methods=['POST'])
def set_adminUsersPage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['adminUsersPage_currentTab'] = data.get('adminUsersPage_currentTab')
    return jsonify({'success': True})

@app.route('/adminApprovalsPage', methods=['GET', 'POST'])
@handle_db_connection
def adminApprovalsPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'adminApprovalsPage_currentTab' not in session:
        session['adminApprovalsPage_currentTab'] = 'requisitionApprovals'

    departments = Department.query.all()
    lecturers = Lecturer.query.order_by(Lecturer.name).all()

    requisitionApprovals = RequisitionApproval.query.order_by(RequisitionApproval.approval_id.desc()).all()
    requisitionAttachments = RequisitionAttachment.query.order_by(RequisitionAttachment.requisition_id.desc()).all()
    claimApprovals = ClaimApproval.query.order_by(ClaimApproval.approval_id.desc()).all()
    claimAttachments = ClaimAttachment.query.order_by(ClaimAttachment.claim_id.desc()).all()

    # Get all LecturerSubject records linked to completed requisitions
    subjects = (
        db.session.query(
            LecturerSubject,
            Lecturer,
            Subject.subject_code,
            Subject.subject_title,
            Subject.subject_level
        )
        .join(Lecturer, LecturerSubject.lecturer_id == Lecturer.lecturer_id)
        .join(Subject, LecturerSubject.subject_id == Subject.subject_id)
        .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
        .filter(RequisitionApproval.status == 'Completed')
        .order_by(desc(RequisitionApproval.approval_id))
        .all()
    )

    claimDetails = []

    for ls, lecturer, code, title, level in subjects:
        claimed = (
            db.session.query(
                func.coalesce(func.sum(LecturerClaim.lecture_hours), 0),
                func.coalesce(func.sum(LecturerClaim.tutorial_hours), 0),
                func.coalesce(func.sum(LecturerClaim.practical_hours), 0),
                func.coalesce(func.sum(LecturerClaim.blended_hours), 0)
            )
            .join(ClaimApproval, LecturerClaim.claim_id == ClaimApproval.approval_id)
            .filter(
                LecturerClaim.lecturer_id == lecturer.lecturer_id,
                LecturerClaim.subject_id == ls.subject_id,
                ClaimApproval.status == 'Completed'
            )
            .first()
        )

        remaining = {
            'lecturer': lecturer,
            'subject_code': code,
            'subject_title': title,
            'subject_level': level,
            'start_date': ls.start_date,
            'end_date': ls.end_date,
            'hourly_rate': ls.rate.amount if ls.rate else 0,
            'lecture_hours': ls.total_lecture_hours - claimed[0],
            'tutorial_hours': ls.total_tutorial_hours - claimed[1],
            'practical_hours': ls.total_practical_hours - claimed[2],
            'blended_hours': ls.total_blended_hours - claimed[3],
        }
        claimDetails.append(remaining)
    
    return render_template('adminApprovalsPage.html', 
                           departments=departments,
                           lecturers=lecturers,
                           requisitionApprovals=requisitionApprovals,
                           requisitionAttachments=requisitionAttachments,
                           claimApprovals=claimApprovals,
                           claimAttachments=claimAttachments,
                           claimDetails=claimDetails)

@app.route('/set_adminApprovalsPage_tab', methods=['POST'])
def set_adminApprovalsPage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['adminApprovalsPage_currentTab'] = data.get('adminApprovalsPage_currentTab')
    return jsonify({'success': True})

from datetime import datetime, timedelta, timezone

@app.route('/check_requisition_period/<int:approval_id>')
def check_requisition_period(approval_id):
    approval = RequisitionApproval.query.get_or_404(approval_id)
    
    last_updated = approval.last_updated
    if not last_updated:
        return jsonify({'expired': False, 'reason': 'No last_updated found'})

    # Ensure both datetimes are timezone-aware (UTC)
    if last_updated.tzinfo is None:
        last_updated = last_updated.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    expired = (now - last_updated) > timedelta(days=30)

    return jsonify({'expired': expired})

@app.route('/api/admin_void_requisition/<approval_id>', methods=['POST'])
@handle_db_connection
def admin_void_requisition(approval_id):
    try:
        data = request.get_json()
        reason = data.get("reason", "").strip()

        if not reason:
            return jsonify(success=False, error="Reason for voiding is required."), 400

        approval = RequisitionApproval.query.get(approval_id)
        if not approval:
            return jsonify(success=False, error="Approval record not found."), 404

        approval.status = f"Voided by Admin - {reason}"
        approval.last_updated = get_current_utc()
        delete_requisition_and_attachment(approval.approval_id, "VOIDED")
        
        hr = Other.query.filter_by(role="Human Resources").first()
        final_hr = Other.query.filter_by(role="Head of Human Resources").first()
        recipients = [approval.po.email, hr.email, final_hr.email]

        # Send notification emails
        subject = f"Part-time Lecturer Requisition Request Voided - {approval.lecturer.name} ({approval.subject_level})"
        body = (
            f"Dear All,\n\n"
            f"The part-time lecturer requisition request has been voided by the Admin.\n"
            f"Reason: {reason}\n\n"
            f"Please review the file here:\n{approval.file_url}\n\n"
            "Thank you,\n"
            "The CourseXcel Team"
        )

        if recipients:
            success = send_email(recipients, subject, body)
            if not success:
                logger.error(f"Failed to send void notification email to: {recipients}")
        
        return jsonify(success=True)

    except Exception as e:
        logger.error(f"Error voiding requisition: {e}")
        return jsonify(success=False, error="Internal server error."), 500

@app.route('/adminReportPage')
@handle_db_connection
def adminReportPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'adminReportsPage_currentTab' not in session:
        session['adminReportsPage_currentTab'] = 'requisitionReports'
    
    departments = Department.query.all()
    requisitionReports = RequisitionReport.query.order_by(RequisitionReport.report_id.desc()).all()
    claimReports = ClaimReport.query.order_by(ClaimReport.report_id.desc()).all()

    return render_template('adminReportPage.html', 
                           departments=departments,
                           requisitionReports=requisitionReports,
                           claimReports=claimReports)

@app.route('/set_adminReportsPage_tab', methods=['POST'])
def set_adminReportsPage_tab():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['adminReportsPage_currentTab'] = data.get('adminReportsPage_currentTab')
    return jsonify({'success': True})

@app.route('/reportConversionResult', methods=['POST'])
@handle_db_connection
def reportConversionResult():
    if 'admin_id' not in session:
        return jsonify(success=False, error="Session expired. Please log in again."), 401

    try:
        report_type = request.form.get('report_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Choose query and generator based on report type
        if report_type == "requisition":
            q = (
                db.session.query(
                    Department.department_code.label("department_code"),
                    Lecturer.name.label("lecturer_name"),
                    func.count(LecturerSubject.subject_id).label("total_subjects"),
                    func.coalesce(func.sum(LecturerSubject.total_lecture_hours), 0).label("lecture_hours"),
                    func.coalesce(func.sum(LecturerSubject.total_tutorial_hours), 0).label("tutorial_hours"),
                    func.coalesce(func.sum(LecturerSubject.total_practical_hours), 0).label("practical_hours"),
                    func.coalesce(func.sum(LecturerSubject.total_blended_hours), 0).label("blended_hours"),
                    func.coalesce(func.max(Rate.amount), 0).label("rate"),
                    func.coalesce(func.sum(LecturerSubject.total_cost), 0).label("total_cost"),
                )
                .join(Lecturer, Lecturer.department_id == Department.department_id)
                .join(LecturerSubject, LecturerSubject.lecturer_id == Lecturer.lecturer_id)
                .join(RequisitionApproval, RequisitionApproval.approval_id == LecturerSubject.requisition_id)
                .outerjoin(Rate, Rate.rate_id == LecturerSubject.rate_id)
                .filter(LecturerSubject.start_date >= start_date)
                .filter(LecturerSubject.end_date <= end_date)
                .group_by(Department.department_code, Lecturer.name)
                .order_by(Department.department_code.asc(), Lecturer.name.asc())
            )
            report_model = RequisitionReport

        elif report_type == "claim":
            q = (
                db.session.query(
                    Department.department_code.label("department_code"),
                    Lecturer.name.label("lecturer_name"),
                    func.count(LecturerClaim.subject_id).label("total_subjects"),
                    func.coalesce(func.sum(LecturerClaim.lecture_hours), 0).label("lecture_hours"),
                    func.coalesce(func.sum(LecturerClaim.tutorial_hours), 0).label("tutorial_hours"),
                    func.coalesce(func.sum(LecturerClaim.practical_hours), 0).label("practical_hours"),
                    func.coalesce(func.sum(LecturerClaim.blended_hours), 0).label("blended_hours"),
                    func.coalesce(func.max(Rate.amount), 0).label("rate"),
                    func.coalesce(func.sum(LecturerClaim.total_cost), 0).label("total_cost"),
                )
                .join(Lecturer, LecturerClaim.lecturer_id == Lecturer.lecturer_id)
                .join(Department, Lecturer.department_id == Department.department_id)
                .join(ClaimApproval, ClaimApproval.approval_id == LecturerClaim.claim_id)
                .outerjoin(Rate, Rate.rate_id == LecturerClaim.rate_id)
                .filter(LecturerClaim.date >= start_date)
                .filter(LecturerClaim.date <= end_date)
                .group_by(Department.department_code, Lecturer.name)
                .order_by(Department.department_code.asc(), func.coalesce(func.sum(LecturerClaim.total_cost), 0).desc())
            )
            report_model = ClaimReport

        else:
            return jsonify(success=False, error="Invalid report type."), 400

        # Build report_details
        report_details = [
            {
                "department_code": r.department_code or "",
                "lecturer_name": r.lecturer_name or "",
                "total_subjects": int(r.total_subjects or 0),
                "total_lecture_hours": int(r.lecture_hours or 0),
                "total_tutorial_hours": int(r.tutorial_hours or 0),
                "total_practical_hours": int(r.practical_hours or 0),
                "total_blended_hours": int(r.blended_hours or 0),
                "rate": int(r.rate or 0),
                "total_cost": int(r.total_cost or 0),
            }
            for r in q.all()
        ]

        # Check for empty result before generating
        if not report_details:
            return jsonify(success=False, error="No matching data found for the selected date range."), 404

        # Generate Excel
        output_path = generate_report_excel(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            report_details=report_details
        )

        file_name = os.path.basename(output_path)
        file_url, file_id = upload_to_drive(output_path, file_name)

        # Save to correct model
        new_report = report_model(
            file_id=file_id,
            file_name=file_name,
            file_url=file_url,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_report)
        db.session.commit()

        return jsonify(success=True, file_url=file_url)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error while converting report result: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/reportConversionResultPage')
def reportConversionResultPage():
    if 'admin_id' not in session:
        return redirect(url_for('loginPage'))

    report_type = request.args.get("type", "requisition")  # default
    if report_type == "claim":
        latest_report = ClaimReport.query.order_by(ClaimReport.report_id.desc()).first()
    else:
        latest_report = RequisitionReport.query.order_by(RequisitionReport.report_id.desc()).first()

    if not latest_report:
        return "No reports found", 404

    # Keep original link for preview
    view_url = latest_report.file_url

    # Default to original in case it's not Google Sheets
    download_url = view_url

    # Convert Google Sheets preview to downloadable link
    if "docs.google.com" in view_url and "/d/" in view_url:
        file_id = view_url.split("/d/")[1].split("/")[0]
        download_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"

    return render_template("reportConversionResultPage.html",
                           view_url=view_url,
                           download_url=download_url,
                           report_type=report_type)

@app.route('/adminProfilePage', methods=['GET', 'POST'])
def adminProfilePage():
    admin_email = session.get('admin_email')

    if not admin_email:
        return redirect(url_for('loginPage'))
    
    admin = Admin.query.filter_by(email=admin_email).first()
    
    drive_service = get_drive_service()

    if request.method == 'POST':  # To delete files
        file_ids = request.form.getlist('file_ids')  # Collect file IDs from the form
        for file_id in file_ids:
            try:
                drive_service.files().delete(fileId=file_id).execute()  # Delete the file by ID
            except Exception as e:
                print(f"Error deleting file with ID {file_id}: {e}")

    # Get the list of files to show
    results = drive_service.files().list(
        pageSize=20,
        fields="files(id, name, webViewLink)"
    ).execute()

    files = results.get('files', [])

    about = drive_service.about().get(fields="storageQuota").execute()
    storage_quota = about.get('storageQuota', {})

    # Convert bytes to GB for readability
    def bytes_to_gb(byte_str):
        return round(int(byte_str) / (1024**3), 2)

    used_gb = bytes_to_gb(storage_quota.get('usage', '0'))
    total_gb = bytes_to_gb(storage_quota.get('limit', '0'))

    # Pass to template
    return render_template('adminProfilePage.html', admin=admin, files=files, used_gb=used_gb, total_gb=total_gb)
    #return render_template('adminProfilePage.html', admin=admin)

def get_requisition_base_query(cutoff_date):
    """Return the base query for eligible requisitions based on shared conditions."""
    # LecturerSubject aggregation
    ls_agg = (
        db.session.query(
            LecturerSubject.requisition_id.label('rid'),
            func.max(LecturerSubject.end_date).label('max_end'),
            func.coalesce(func.sum(LecturerSubject.total_cost), 0).label('ls_total')
        )
        .group_by(LecturerSubject.requisition_id)
        .subquery()
    )

    # LecturerClaim aggregation
    lc_agg = (
        db.session.query(
            LecturerClaim.requisition_id.label('rid'),
            func.coalesce(func.sum(LecturerClaim.total_cost), 0).label('lc_total')
        )
        .group_by(LecturerClaim.requisition_id)
        .subquery()
    )

    # Main filter query
    q = (
        db.session.query(RequisitionApproval, ls_agg.c.max_end, ls_agg.c.ls_total,
                         func.coalesce(lc_agg.c.lc_total, 0).label('lc_total'))
        .join(ls_agg, ls_agg.c.rid == RequisitionApproval.approval_id)
        .outerjoin(lc_agg, lc_agg.c.rid == RequisitionApproval.approval_id)
        .filter(func.lower(func.coalesce(RequisitionApproval.status, '')) == 'completed')
        .filter(ls_agg.c.max_end <= cutoff_date)
        .filter((ls_agg.c.ls_total - func.coalesce(lc_agg.c.lc_total, 0)) == 0)
    )
    return q

def get_completed_claims_for_requisition(req_id):
    """Return completed ClaimApproval objects related to a given requisition."""
    claim_ids = {
        cid for (cid,) in db.session.query(LecturerClaim.claim_id)
                                    .filter(LecturerClaim.requisition_id == req_id)
                                    .distinct()
                                    .all()
    }
    if not claim_ids:
        return []

    return [
        ca for ca in ClaimApproval.query.filter(ClaimApproval.approval_id.in_(list(claim_ids))).all()
        if (ca.status or '').lower() == 'completed'
    ]

@app.route('/api/download_files_zip', methods=['POST'])
@handle_db_connection
def download_files_zip():
    """
    Conditions to download:
    1) RequisitionApproval.status == 'Completed'
    2) max(LecturerSubject.end_date) <= today - 4 months
    3) sum(LecturerSubject.total_cost) - sum(LecturerClaim.total_cost where same requisition_id) == 0
    If passes, include into ZIP with structure:

      Requisition_{dd MMM yyyy}/<Department Name>/Approvals/*.xlsx
                                                 /Attachments/*.pdf

      Claim_{dd MMM yyyy}/<Department Name>/Approvals/*.xlsx
                                          /Attachments/*.pdf
    """
    try:
        today = date.today()
        cutoff = today - relativedelta(months=4)   # fixed to 4 months
        stamp = format_dd_MMM_yyyy(today)

        rows = get_requisition_base_query(cutoff).all()
        if not rows:
            return jsonify({'error': 'No requisition or claim files meet the download criteria.'}), 400

        mem_zip = BytesIO()
        with zipfile.ZipFile(mem_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            req_root = f"Requisition_{stamp}"
            claim_root = f"Claim_{stamp}"

            for req, max_end, ls_total, lc_total in rows:
                dept_name = safe_name(
                    getattr(req.department, 'department_code', None) or
                    getattr(req.department, 'department_name', None) or
                    "Unknown_Department"
                )

                # Add requisition approval XLSX
                if req.file_url and (req.file_name or '').lower().endswith(('.xlsx', '.xlsm', '.xls')):
                    add_drive_approval_xlsx_to_zip(
                        zf, req.file_url,
                        f"{req_root}/{dept_name}/Approvals/{safe_name(req.file_name)}"
                    )

                # Add requisition attachments (PDF)
                for att in (req.requisition_attachments or []):
                    if att.attachment_url and (att.attachment_name or '').lower().endswith('.pdf'):
                        add_drive_attachment_pdf_to_zip(
                            zf, att.attachment_url,
                            f"{req_root}/{dept_name}/Attachments/{safe_name(att.attachment_name)}"
                        )

                # Add claim approvals & attachments
                for ca in get_completed_claims_for_requisition(req.approval_id):
                    if ca.file_url and (ca.file_name or '').lower().endswith(('.xlsx', '.xlsm', '.xls')):
                        add_drive_approval_xlsx_to_zip(
                            zf, ca.file_url,
                            f"{claim_root}/{dept_name}/Approvals/{safe_name(ca.file_name)}"
                        )
                    for catt in (ca.claim_attachments or []):
                        if catt.attachment_url and (catt.attachment_name or '').lower().endswith('.pdf'):
                            add_drive_attachment_pdf_to_zip(
                                zf, catt.attachment_url,
                                f"{claim_root}/{dept_name}/Attachments/{safe_name(catt.attachment_name)}"
                            )

        mem_zip.seek(0)
        return send_file(
            mem_zip,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"Approvals and Attachments_{stamp}.zip"
        )

    except Exception as e:
        logger.error(f"Error during ZIP download generation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup_downloaded_files', methods=['POST'])
@handle_db_connection
def cleanup_downloaded_files():
    try:
        today = date.today()
        cutoff = today - relativedelta(months=4)

        rows = get_requisition_base_query(cutoff).all()
        if not rows:
            return jsonify({'error': 'No matching records to clean up.'}), 400

        deleted_requisition_ids = []
        deleted_claim_ids = set()

        for req, max_end, ls_total, lc_total in rows:
            # Delete requisition files
            if req.file_url:
                drive_delete_by_url(req.file_url)
            for att in (req.requisition_attachments or []):
                if att.attachment_url:
                    drive_delete_by_url(att.attachment_url)

            # Delete claim files
            for ca in get_completed_claims_for_requisition(req.approval_id):
                if ca.file_url:
                    drive_delete_by_url(ca.file_url)
                for catt in (ca.claim_attachments or []):
                    if catt.attachment_url:
                        drive_delete_by_url(catt.attachment_url)
                deleted_claim_ids.add(ca.approval_id)

            deleted_requisition_ids.append(req.approval_id)

        # DB deletions
        if deleted_claim_ids:
            ClaimApproval.query.filter(
                ClaimApproval.approval_id.in_(list(deleted_claim_ids))
            ).delete(synchronize_session=False)

        if deleted_requisition_ids:
            RequisitionApproval.query.filter(
                RequisitionApproval.approval_id.in_(deleted_requisition_ids)
            ).delete(synchronize_session=False)

        db.session.commit()

        return jsonify({
            'success': True,
            'deleted_requisition_ids': deleted_requisition_ids,
            'deleted_claim_ids': sorted(list(deleted_claim_ids))
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error while cleaning up downloaded files: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/change_rate_status/<int:id>', methods=['PUT'])
def change_rate_status(id):
    try:
        rate = Rate.query.get_or_404(id)
        # Toggle; if status is None, treat as False
        rate.status = not bool(rate.status)
        db.session.commit()
        return jsonify({'success': True, 'status': bool(rate.status), 'message': 'Rate status updated successfully.'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error while changing rate status: {str(e)}")
        return jsonify({'error': str(e)}), 500

def safe_name(s: str) -> str: 
    if not s: 
        return "Unknown" 
    return re.sub(r'[\\/:*?"<>|\r\n]+', '_', s).strip() 

def format_dd_MMM_yyyy(d: date) -> str: 
    return d.strftime('%d %b %Y')

# Extract fileId from common URLs
def extract_drive_file_id(url: str) -> str | None:
    # Sheets url
    m = re.search(r"docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if m: return m.group(1)
    # Drive file url
    m = re.search(r"drive\.google\.com/file/d/([a-zA-Z0-9-_]+)", url)
    if m: return m.group(1)
    # open?id=<ID>
    m = re.search(r"[?&]id=([a-zA-Z0-9-_]+)", url)
    if m: return m.group(1)
    return None

# Get metadata (name, mimeType)
def drive_get_metadata(file_id: str) -> dict:
    svc = get_drive_service()
    return svc.files().get(fileId=file_id, fields="id, name, mimeType").execute()

# Download (export for Google-native, get_media for binary) into memory
def drive_download_bytes(file_id: str, export_mime: str | None = None) -> bytes:
    svc = get_drive_service()
    if export_mime:
        request = svc.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        request = svc.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        # (optional) you can inspect status.progress() here if you want
    fh.seek(0)
    return fh.read()

# Write approvals (Sheets -> XLSX) into ZIP by URL
APP_SHEET_PW = os.environ.get("EXCEL_SHEET_PW", "approval_excel_sheet_password")
APP_BOOK_PW  = os.environ.get("EXCEL_BOOK_PW", "approval_workbook_password")

def add_drive_approval_xlsx_to_zip(zf, url: str, arcname: str):
    file_id = extract_drive_file_id(url)
    if not file_id:
        return
    meta = drive_get_metadata(file_id)

    # Export Google Sheet → XLSX
    if meta.get("mimeType") == "application/vnd.google-apps.spreadsheet":
        data = drive_download_bytes(
            file_id,
            export_mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        # If it isn’t a Google Sheet, try direct bytes (already an Excel file in Drive)
        data = drive_download_bytes(file_id)

    # Protect the workbook/sheets
    data = protect_excel_bytes(data, sheet_password=APP_SHEET_PW, workbook_password=APP_BOOK_PW)

    # Ensure .xlsx extension
    if not arcname.lower().endswith(".xlsx"):
        base, _, _ = arcname.rpartition(".")
        arcname = (base or arcname) + ".xlsx"

    zf.writestr(arcname, data)

# Write attachments (PDF) into ZIP by URL
def add_drive_attachment_pdf_to_zip(zf, url: str, arcname: str):
    file_id = extract_drive_file_id(url)
    if not file_id:
        return
    meta = drive_get_metadata(file_id)
    mt = meta.get("mimeType", "")

    # Google-native → export to PDF
    if mt.startswith("application/vnd.google-apps."):
        data = drive_download_bytes(file_id, export_mime="application/pdf")
        # Ensure .pdf extension
        if not arcname.lower().endswith(".pdf"):
            base, _, _ = arcname.rpartition(".")
            arcname = (base or arcname) + ".pdf"
        zf.writestr(arcname, data)
        return

    # Non-native binary (likely already a PDF on Drive) → get_media
    data = drive_download_bytes(file_id, export_mime=None)
    # Keep arcname; optionally force .pdf if you know all should be PDF
    zf.writestr(arcname, data)

def protect_excel_bytes(xlsx_bytes: bytes,
                        sheet_password: str | None = None,
                        workbook_password: str | None = None) -> bytes:
    """
    - Locks every sheet (no edits).
    - Optionally sets sheet and workbook structure passwords.
    - Returns protected XLSX bytes.
    """
    bio = io.BytesIO(xlsx_bytes)
    wb = load_workbook(bio, data_only=False)

    for ws in wb.worksheets:
        # Lock the sheet and disallow edits
        ws.protection.sheet = True
        ws.protection.enable()
        ws.protection.formatCells = False
        ws.protection.formatColumns = False
        ws.protection.formatRows = False
        ws.protection.insertColumns = False
        ws.protection.insertRows = False
        ws.protection.insertHyperlinks = False
        ws.protection.deleteColumns = False
        ws.protection.deleteRows = False
        ws.protection.sort = False
        ws.protection.autoFilter = False
        ws.protection.pivotTables = False
        ws.protection.objects = True
        ws.protection.scenarios = True
        # Allow selecting cells so users can view content comfortably
        ws.protection.selectLockedCells = True
        ws.protection.selectUnlockedCells = True

        if sheet_password:
            # Sets hashed password inside the file (no prompt unless unprotecting)
            ws.protection.set_password(sheet_password)

    # Protect workbook structure (e.g., adding/removing sheets)
    wb.security = WorkbookProtection(lockStructure=True, lockWindows=False)
    if workbook_password:
        wb.security.workbookPassword = hash_password(workbook_password)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.read()

def drive_delete_by_url(url: str) -> bool:
    file_id = extract_drive_file_id(url)
    if not file_id:
        return False
    try:
        svc = get_drive_service()
        svc.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        logging.error(f"Drive delete failed for {url}: {e}")
        return False