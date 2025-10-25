import logging, os, re, tempfile
from app import app, db
from app.database import handle_db_connection
from app.excel_generator import generate_claim_excel
from app.models import Admin, ClaimApproval, ClaimAttachment, Department, Head, Lecturer, LecturerClaim, LecturerSubject, Other, ProgramOfficer, Rate, RequisitionApproval, Subject 
from app.shared_routes import format_utc, get_current_utc, get_drive_service, is_already_reviewed, is_already_voided, process_signature_and_upload, send_email, to_utc_aware, upload_to_drive
from datetime import datetime, timedelta
from flask import abort, jsonify, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from googleapiclient.http import MediaFileUpload
from sqlalchemy import and_, desc, extract, func

bcrypt = Bcrypt()
logger = logging.getLogger(__name__)

@app.route('/lecturerHomepage', methods=['GET', 'POST'])
@handle_db_connection
def lecturerHomepage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    
    lecturer_id = session.get("lecturer_id")
    two_factor_enabled = Lecturer.query.get(lecturer_id).two_factor_enabled

    # Subject counts
    subject_count = (
        db.session.query(func.count(LecturerSubject.subject_id))
        .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
        .filter(
            LecturerSubject.lecturer_id == lecturer_id,
            RequisitionApproval.status == "Completed"
        )
        .scalar()  # returns an integer directly
    )

    # Hours Taught vs Assigned (only for this lecturer)
    # Subquery: Assigned hours from LecturerSubject
    assigned_subq = (
        db.session.query(
            LecturerSubject.subject_id.label("subject_id"),
            func.sum(
                LecturerSubject.total_lecture_hours +
                LecturerSubject.total_tutorial_hours +
                LecturerSubject.total_practical_hours +
                LecturerSubject.total_blended_hours
            ).label("assigned_hours")
        )
        .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
        .filter(LecturerSubject.lecturer_id == lecturer_id)
        .filter(RequisitionApproval.status == "Completed")
        .group_by(LecturerSubject.subject_id)
        .subquery()
    )

    # Subquery: Taught hours from LecturerClaim
    taught_subq = (
        db.session.query(
            LecturerClaim.subject_id.label("subject_id"),
            func.coalesce(func.sum(
                LecturerClaim.lecture_hours +
                LecturerClaim.tutorial_hours +
                LecturerClaim.practical_hours +
                LecturerClaim.blended_hours
            ), 0).label("taught_hours")
        )
        .join(ClaimApproval, LecturerClaim.claim_id == ClaimApproval.approval_id, isouter=True)
        .filter(LecturerClaim.lecturer_id == lecturer_id)
        .filter((ClaimApproval.status == "Completed") | (ClaimApproval.status == None))
        .group_by(LecturerClaim.subject_id)
        .subquery()
    )

    # Final join: subjects + assigned + taught
    hours_data = (
        db.session.query(
            Subject.subject_code.label("subject"),
            func.coalesce(assigned_subq.c.assigned_hours, 0).label("assigned_hours"),
            func.coalesce(taught_subq.c.taught_hours, 0).label("taught_hours")
        )
        .join(assigned_subq, assigned_subq.c.subject_id == Subject.subject_id)
        .outerjoin(taught_subq, taught_subq.c.subject_id == Subject.subject_id)
        .all()
    )

    # Convert to list of dicts
    subject_hours = [
        {
            "subject": subj_code,
            "assigned": int(assigned or 0),
            "taught": int(taught or 0)
        }
        for subj_code, assigned, taught in hours_data
    ]

    # Claim Trends
    claim_trends = (
        db.session.query(
            extract('year', LecturerClaim.date).label('year'),
            extract('month', LecturerClaim.date).label('month'),
            func.sum(LecturerClaim.total_cost).label("total_claims")
        )
        .join(ClaimApproval, LecturerClaim.claim_id == ClaimApproval.approval_id)
        .filter(LecturerClaim.lecturer_id == lecturer_id)
        .filter(ClaimApproval.status == "Completed")   # optional: only approved claims
        .group_by(extract('year', LecturerClaim.date), extract('month', LecturerClaim.date))
        .order_by(extract('year', LecturerClaim.date), extract('month', LecturerClaim.date))
        .all()
    )

    # Convert to dict {year: [ {month, total_claims}, ... ]}
    subject_claims = {}
    for year, month, total_claims in claim_trends:
        subject_claims.setdefault(int(year), []).append({
            "month": int(month),
            "total_claims": float(total_claims)
        })

    return render_template('lecturerHomepage.html', two_factor_enabled=two_factor_enabled,
                           subject_count=subject_count, 
                           subject_hours=subject_hours, 
                           subject_claims=subject_claims)

@app.route('/lecturerFormPage', methods=['GET', 'POST'])
@handle_db_connection
def lecturerFormPage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    
   # Sum of claimed cost per (lecturer, requisition, subject)
    claims_sum_subq = (
        db.session.query(
            LecturerClaim.lecturer_id.label('lecturer_id'),
            LecturerClaim.requisition_id.label('requisition_id'),
            LecturerClaim.subject_id.label('subject_id'),
            func.coalesce(func.sum(LecturerClaim.total_cost), 0).label('claimed_cost')
        )
        .group_by(
            LecturerClaim.lecturer_id,
            LecturerClaim.requisition_id,
            LecturerClaim.subject_id
        )
        .subquery()
    )

    levels_q = (
        db.session.query(Subject.subject_level)
        .join(LecturerSubject, Subject.subject_id == LecturerSubject.subject_id)
        .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
        .outerjoin(
            claims_sum_subq,
            and_(
                claims_sum_subq.c.lecturer_id == LecturerSubject.lecturer_id,
                claims_sum_subq.c.requisition_id == LecturerSubject.requisition_id,
                claims_sum_subq.c.subject_id == LecturerSubject.subject_id,
            )
        )
        .filter(LecturerSubject.lecturer_id == session.get('lecturer_id'))
        .filter(RequisitionApproval.status == 'Completed')  # only completed requisitions
        # keep entries that still have money left to claim:
        .filter((func.coalesce(LecturerSubject.total_cost, 0) - func.coalesce(claims_sum_subq.c.claimed_cost, 0)) != 0)
        .distinct()
    )

    levels = [row[0] for row in levels_q.all()]

    return render_template('lecturerFormPage.html', levels=levels)

@app.route('/get_subjects/<level>')
@handle_db_connection
def get_subjects(level):
    try:
        lecturer_id = session.get('lecturer_id')

        claims_sum_subq = (
            db.session.query(
                LecturerClaim.lecturer_id.label('lecturer_id'),
                LecturerClaim.requisition_id.label('requisition_id'),
                LecturerClaim.subject_id.label('subject_id'),
                func.coalesce(func.sum(LecturerClaim.total_cost), 0).label('claimed_cost')
            )
            .group_by(
                LecturerClaim.lecturer_id,
                LecturerClaim.requisition_id,
                LecturerClaim.subject_id
            )
            .subquery()
        )

        remaining_cost = (
            func.coalesce(LecturerSubject.total_cost, 0) -
            func.coalesce(claims_sum_subq.c.claimed_cost, 0)
        ).label('remaining_cost')

        rows = (
            db.session.query(
                LecturerSubject,
                Subject,
                RequisitionApproval
            )
            .join(Subject, LecturerSubject.subject_id == Subject.subject_id)
            .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
            .outerjoin(
                claims_sum_subq,
                and_(
                    claims_sum_subq.c.lecturer_id == LecturerSubject.lecturer_id,
                    claims_sum_subq.c.requisition_id == LecturerSubject.requisition_id,
                    claims_sum_subq.c.subject_id == LecturerSubject.subject_id,
                )
            )
            .filter(LecturerSubject.lecturer_id == lecturer_id)
            .filter(Subject.subject_level == level)
            .filter(RequisitionApproval.status == 'Completed')
            .filter(remaining_cost > 0)   # keep only if still has money to claim
            .all()
        )

        subject_list = []
        for ls, s, ra in rows:
            subject_list.append({
                'value': f"{s.subject_id}:{ls.requisition_id}",
                'label': f"{s.subject_code} - {s.subject_title} ({ls.start_date} → {ls.end_date})",
                'subject_code': s.subject_code,
                'subject_title': s.subject_title,
                'subject_id': s.subject_id,
                'requisition_id': ls.requisition_id,
                'start_date': ls.start_date.isoformat() if ls.start_date else '',
                'end_date': ls.end_date.isoformat() if ls.end_date else ''
            })

        return jsonify(success=True, subjects=subject_list)
    except Exception as e:
        logger.error(f"Error getting subjects by level: {e}")
        return jsonify(success=False, message=str(e), subjects=[])

@app.route('/get_subject_info')
@handle_db_connection
def get_subject_info():
    try:
        lecturer_id = session.get('lecturer_id')
        subject_id = request.args.get('subject_id', type=int)
        requisition_id = request.args.get('requisition_id', type=int)

        if not subject_id or not requisition_id:
            return jsonify(success=False, message="subject_id and requisition_id are required.")

        ls = (
            db.session.query(LecturerSubject)
            .filter_by(lecturer_id=lecturer_id, subject_id=subject_id, requisition_id=requisition_id)
            .first()
        )
        if not ls:
            return jsonify(success=False, message="LecturerSubject not found.")

        # Rate
        rate = Rate.query.get(ls.rate_id)
        hourly_rate = rate.amount if rate else 0

        # Claimed hours — IMPORTANT: filter by BOTH subject_id and requisition_id
        claimed = (
            db.session.query(
                func.sum(LecturerClaim.lecture_hours).label('claimed_lecture'),
                func.sum(LecturerClaim.tutorial_hours).label('claimed_tutorial'),
                func.sum(LecturerClaim.practical_hours).label('claimed_practical'),
                func.sum(LecturerClaim.blended_hours).label('claimed_blended')
            )
            .filter(
                LecturerClaim.lecturer_id == lecturer_id,
                LecturerClaim.subject_id == subject_id,
                LecturerClaim.requisition_id == requisition_id
            )
            .first()
        )

        claimed_lecture = claimed.claimed_lecture or 0
        claimed_tutorial = claimed.claimed_tutorial or 0
        claimed_practical = claimed.claimed_practical or 0
        claimed_blended = claimed.claimed_blended or 0

        return jsonify({
            'success': True,
            'start_date': ls.start_date.isoformat() if ls.start_date else '',
            'end_date': ls.end_date.isoformat() if ls.end_date else '',
            'unclaimed_lecture': max(0, (ls.total_lecture_hours or 0) - claimed_lecture),
            'unclaimed_tutorial': max(0, (ls.total_tutorial_hours or 0) - claimed_tutorial),
            'unclaimed_practical': max(0, (ls.total_practical_hours or 0) - claimed_practical),
            'unclaimed_blended': max(0, (ls.total_blended_hours or 0) - claimed_blended),
            'hourly_rate': hourly_rate,
            'rate_id': ls.rate_id or None
        })
    except Exception as e:
        logger.error(f"Error get_subject_info: {e}")
        return jsonify(success=False, message=str(e))

    
@app.route('/claimFormConversionResult', methods=['POST'])
@handle_db_connection
def claimFormConversionResult():
    if 'lecturer_id' not in session:
        return jsonify(success=False, error="Session expired. Please log in again."), 401

    try:
        # Debug: Print all form data
        print("Form Data:", request.form)
        
        # Get form data  
        lecturer = Lecturer.query.get(session.get('lecturer_id'))
        name = lecturer.name if lecturer else None
        department_code = lecturer.department.department_code if lecturer else None

        # Helper function to safely convert to int
        def safe_int(value, default=0):
            try:
                if isinstance(value, str):
                    return int(value.strip()) if value.strip() else default
                return int(value)
            except (ValueError, TypeError):
                return default

        subject_level = request.form.get('subject_level') 

        # Extract claim details from form
        claim_details = []
        i = 1
        while f'date{i}' in request.form:
            claim_details.append({
                'subject_id': int(request.form.get(f'subjectIdHidden{i}') or 0),
                'requisition_id': int(request.form.get(f'requisitionIdHidden{i}') or 0),
                'rate_id': int(request.form.get(f'rateIdHidden{i}') or 0),
                'subject_code': request.form.get(f'subjectCodeText{i}', ''),  # <— NEW
                'date': request.form.get(f'date{i}'),
                'lecture_hours': safe_int(request.form.get(f'lectureHours{i}'), 0),
                'tutorial_hours': safe_int(request.form.get(f'tutorialHours{i}'), 0),
                'practical_hours': safe_int(request.form.get(f'practicalHours{i}'), 0),
                'blended_hours': safe_int(request.form.get(f'blendedHours{i}'), 0),
                'remarks': request.form.get(f'remarks{i}')
            })
            i += 1

        if not claim_details:
            return jsonify(success=False, error="No claim details provided"), 400
               
        # Get department info
        department = Department.query.filter_by(department_code=department_code).first()
        department_id = department.department_id if department else None
        dean_name = department.dean_name if department else 'N/A'

        # Derive PO/Head from requisition_ids in the rows
        requisition_ids = {row['requisition_id'] for row in claim_details if row['requisition_id']}
        if not requisition_ids:
            return jsonify(success=False, error="No requisition linkage found in claim rows."), 400

        requisitions = (db.session.query(RequisitionApproval)
            .filter(RequisitionApproval.approval_id.in_(requisition_ids))
            .all())

        if not requisitions or len(requisitions) != len(requisition_ids):
            return jsonify(success=False, error="One or more requisitions not found."), 400

        # Enforce that all rows belong to the same PO/Head (simplest rule for a single approval)
        unique_po_ids = {r.po_id for r in requisitions if r.po_id is not None}
        unique_head_ids = {r.head_id for r in requisitions if r.head_id is not None}

        if len(unique_po_ids) != 1 or len(unique_head_ids) != 1:
            # You can choose to support mixed POs/Heads in one submission, but usually this is blocked.
            return jsonify(
                success=False,
                error="Selected program code(s) are assigned by different program officers and are under different Heads. "
                    "Please split into separate submissions."
            ), 400

        po_id = unique_po_ids.pop()
        head_id = unique_head_ids.pop()

        po = ProgramOfficer.query.get(po_id) if po_id else None
        head = Head.query.get(head_id) if head_id else None
        po_name = po.name if po else 'N/A'
        head_name = head.name if head else 'N/A'

        # Human Resources (excluding Ting Ting)
        hr = (Other.query
            .filter_by(role="Human Resources")
            .filter(Other.email != "tingting.eng@newinti.edu.my")
            .first())
        hr_name = hr.name if hr else 'N/A'

        # Validate required roles exist
        missing_roles = []
        if not po:   missing_roles.append("Program Officer")
        if not head: missing_roles.append("Head of Programme")
        if not department or not department.dean_name: missing_roles.append("Dean")
        if not hr:   missing_roles.append("Human Resources")
        if missing_roles:
            return jsonify(success=False, error=f"Missing required role(s): {', '.join(missing_roles)}"), 400

        # Generate Excel file
        output_path, sign_col = generate_claim_excel(
            name=name,
            department_code=department_code,
            subject_level=subject_level,
            claim_details=claim_details,
            po_name=po_name,
            head_name=head_name,
            dean_name=dean_name,
            hr_name=hr_name
        )

        file_name = os.path.basename(output_path)
        file_url, file_id = upload_to_drive(output_path, file_name)

        # Save to database
        approval = ClaimApproval(
            department_id=department_id,
            lecturer_id=session.get('lecturer_id'),
            po_id=po_id,
            head_id=head.head_id if head else None,
            subject_level=subject_level,
            sign_col=sign_col,
            file_id=file_id,
            file_name=file_name,
            file_url=file_url,
            status="Pending Acknowledgement by Lecturer",
            last_updated = get_current_utc()
        )

        db.session.add(approval)
        db.session.flush()  # Get approval_id before committing
        
        approval_id = approval.approval_id

        # Add lecturer_claim entries with claim_id
        for claim_data in claim_details:
            # rate_id from row
            rate_id = claim_data['rate_id'] or None
            rate_amount = 0
            if rate_id:
                r = Rate.query.get(rate_id)
                rate_amount = r.amount if r else 0

            total_cost = rate_amount * (
                claim_data['lecture_hours'] + claim_data['tutorial_hours'] + claim_data['practical_hours'] + claim_data['blended_hours']
            )

            lc = LecturerClaim(
                lecturer_id=session.get('lecturer_id'),
                requisition_id=claim_data['requisition_id'],
                claim_id=approval_id,
                subject_id=claim_data['subject_id'],
                date=datetime.strptime(claim_data['date'], "%Y-%m-%d").date(),
                lecture_hours=claim_data['lecture_hours'],
                tutorial_hours=claim_data['tutorial_hours'],
                practical_hours=claim_data['practical_hours'],
                blended_hours=claim_data['blended_hours'],
                rate_id=rate_id,
                total_cost=total_cost
            )
            db.session.add(lc)

        db.session.commit()

        # ======= Handle Attachments ========
        attachments = request.files.getlist('upload_claim_attachment')
        attachment_urls = []

        if attachments:
            drive_service = get_drive_service()
            lecturer_id = session.get('lecturer_id')
            if not lecturer_id:
                return jsonify({
                    'success': False,
                    'error': 'Lecturer session not found. Please login again.'
                }), 400

            for attachment in attachments:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    attachment.save(tmp.name)

                    file_metadata = {'name': attachment.filename}
                    media = MediaFileUpload(tmp.name, mimetype=attachment.mimetype, resumable=True)
                    uploaded = drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()

                    # Set public view permission
                    drive_service.permissions().create(
                        fileId=uploaded['id'],
                        body={'type': 'anyone', 'role': 'reader'},
                    ).execute()

                    file_url = f"https://drive.google.com/file/d/{uploaded['id']}/view"
                    attachment_urls.append((attachment.filename, file_url))
                    os.unlink(tmp.name)

            # Save to ClaimAttachment table
            for filename, url in attachment_urls:
                claim_attachment = ClaimAttachment(
                    attachment_name=filename,
                    attachment_url=url,
                    lecturer_id=lecturer_id,
                    claim_id=approval_id
                )
                db.session.add(claim_attachment)

            db.session.commit()

        return jsonify({
            'success': True,
            'file_url': file_url,
            'attachments': [{'name': fn, 'url': url} for fn, url in attachment_urls]
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error while converting claim result: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/claimFormConversionResultPage')
def claimFormConversionResultPage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    
    approval = ClaimApproval.query.filter_by(lecturer_id=session.get('lecturer_id')).order_by(ClaimApproval.approval_id.desc()).first()
    return render_template('claimFormConversionResultPage.html', file_url=approval.file_url)

@app.route('/lecturerClaimsPage')
@handle_db_connection
def lecturerClaimsPage():
    if 'lecturer_id' not in session:
        return redirect(url_for('loginPage'))
    
    # Set default tab if none exists
    if 'lecturerClaimsPage_currentTab' not in session:
        session['lecturerClaimsPage_currentTab'] = 'claimApprovals'

    lecturer_id = session['lecturer_id']

    claimApprovals = (
        ClaimApproval.query
        .filter_by(lecturer_id=lecturer_id)
        .order_by(ClaimApproval.approval_id.desc())
        .all()
    )

    claimAttachments = (
        ClaimAttachment.query
        .filter(ClaimAttachment.lecturer_id == lecturer_id)
        .order_by(ClaimAttachment.claim_id.desc())
        .all()
    )

    # Get all lecturer_subject records for the lecturer
    subjects = (
        db.session.query(
            LecturerSubject,
            Subject.subject_code,
            Subject.subject_title,
            Subject.subject_level
        )
        .join(Subject, LecturerSubject.subject_id == Subject.subject_id)
        .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
        .filter(LecturerSubject.lecturer_id == lecturer_id)
        .filter(RequisitionApproval.status == 'Completed')  # Only completed requisitions
        .order_by(desc(RequisitionApproval.approval_id))
        .all()
    )

    claimDetails = []

    for ls, code, title, level in subjects:
        # ✅ Only sum claims linked to COMPLETED claim approvals
        claimed = (
            db.session.query(
                func.coalesce(func.sum(LecturerClaim.lecture_hours), 0),
                func.coalesce(func.sum(LecturerClaim.tutorial_hours), 0),
                func.coalesce(func.sum(LecturerClaim.practical_hours), 0),
                func.coalesce(func.sum(LecturerClaim.blended_hours), 0)
            )
            .join(ClaimApproval, LecturerClaim.claim_id == ClaimApproval.approval_id)
            .filter(
                LecturerClaim.lecturer_id == lecturer_id,
                LecturerClaim.subject_id == ls.subject_id,
                ClaimApproval.status == 'Completed'   # ✅ New condition
            )
            .first()
        )

        remaining = {
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

    return render_template(
        'lecturerClaimsPage.html',
        claimApprovals=claimApprovals,
        claimAttachments=claimAttachments,
        claimDetails=claimDetails
    )

@app.route('/set_lecturerClaimsPage_tab', methods=['POST'])
def set_lecturerClaimsPage_tab():
    if 'lecturer_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    session['lecturerClaimsPage_currentTab'] = data.get('lecturerClaimsPage_currentTab')
    return jsonify({'success': True})

@app.route('/check_claim_status/<int:approval_id>')
def check_claim_status(approval_id):
    approval = ClaimApproval.query.get_or_404(approval_id)
    return jsonify({'status': approval.status})

@app.route('/api/lecturer_review_claim/<approval_id>', methods=['POST'])
@handle_db_connection
def lecturer_review_claim(approval_id):
    try:
        data = request.get_json()
        signature_data = data.get("image")

        if not signature_data or "," not in signature_data:
            return jsonify(success=False, error="Invalid image data format")

        # Fetch approval record
        approval = ClaimApproval.query.get(approval_id)
        if not approval:
            return jsonify(success=False, error="Approval record not found")

        # Process signature and upload updated file
        process_signature_and_upload(approval, signature_data, "A")

        # Update status after signature inserted
        approval.status = "Pending Acknowledgement by PO"
        approval.last_updated = get_current_utc()
        db.session.commit()

        try:
            notify_approval(approval, approval.program_officer.email if approval.program_officer else None, "po_review_claim", "Program Officer")
        except Exception as e:
            logger.error(f"Failed to notify PO: {e}")    

        return jsonify(success=True)

    except Exception as e:
        logger.error(f"Error uploading signature: {e}")
        return jsonify(success=False, error=str(e)), 500
    
@app.route('/api/po_review_claim/<approval_id>', methods=['GET', 'POST'])
def po_review_claim(approval_id):
    approval = ClaimApproval.query.get(approval_id)
    if not approval:
        abort(404, description="Approval record not found")

    # Check if already voided
    voided_response = is_already_voided(approval)
    if voided_response:
        return voided_response

    # Check if already reviewed
    reviewed_response = is_already_reviewed(approval, ["Pending Acknowledgement by PO"])
    if reviewed_response:
        return reviewed_response

    # Otherwise render the review page
    if request.method == 'GET':
        return render_template("reviewClaimApprovalRequest.html", approval=approval)

    # POST logic
    action = request.form.get('action')
    if action == 'approve':
        try:
            process_signature_and_upload(approval, request.form.get('signature_data'), "B")
            approval.status = "Pending Acknowledgement by HOP"
            approval.last_updated = get_current_utc()
            db.session.commit()

            try:
                notify_approval(approval, approval.head.email if approval.head else None, "head_review_claim", "Head of Programme")
            except Exception as e:
                logger.error(f"Failed to notify HOP: {e}")

            return '''<script>alert("Request approved successfully. You may now close this window.")</script>'''
        except Exception as e:
            return str(e), 500

    elif action == 'reject':
        reason = request.form.get('reject_reason')
        if not reason:
            return "Rejection reason required", 400
        
        approval.status = f"Rejected by PO - {reason.strip()}"
        approval.last_updated = get_current_utc()

        # Delete related records and rename approval file
        delete_claim_and_attachment(approval.approval_id, "REJECTED")

        try:
            send_rejection_email("PO", approval, reason.strip())
        except Exception as e:
            logger.error(f"Failed to send rejection email: {e}")

        return '''<script>alert("Request rejected successfully. You may now close this window.")</script>'''
    
    return "Invalid action", 400

@app.route('/api/head_review_claim/<approval_id>', methods=['GET', 'POST'])
def head_review_claim(approval_id):
    approval = ClaimApproval.query.get(approval_id)
    if not approval:
        abort(404, description="Approval record not found")

    # Check if already voided
    voided_response = is_already_voided(approval)
    if voided_response:
        return voided_response

    # Check if already reviewed
    reviewed_response = is_already_reviewed(approval, ["Pending Acknowledgement by HOP"])
    if reviewed_response:
        return reviewed_response

    # Otherwise render the review page
    if request.method == 'GET':
        return render_template("reviewClaimApprovalRequest.html", approval=approval)

    # POST logic
    action = request.form.get('action')
    if action == 'approve':
        try:
            process_signature_and_upload(approval, request.form.get('signature_data'), "C")
            approval.status = "Pending Acknowledgement by Dean / HOS"
            approval.last_updated = get_current_utc()
            db.session.commit()

            try:
                notify_approval(approval, approval.department.dean_email if approval.department else None, "dean_review_claim", "Dean / HOS")
            except Exception as e:
                logger.error(f"Failed to notify Dean: {e}")

            return '''<script>alert("Request approved successfully. You may now close this window.")</script>'''
        except Exception as e:
            return str(e), 500

    elif action == 'reject':
        reason = request.form.get('reject_reason')
        if not reason:
            return "Rejection reason required", 400
        
        approval.status = f"Rejected by HOP - {reason.strip()}"
        approval.last_updated = get_current_utc()

        # Delete related records and rename approval file
        delete_claim_and_attachment(approval.approval_id, "REJECTED")

        try:
            send_rejection_email("HOP", approval, reason.strip())
        except Exception as e:
            logger.error(f"Failed to send rejection email: {e}")

        return '''<script>alert("Request rejected successfully. You may now close this window.")</script>'''
    
    return "Invalid action", 400

@app.route('/api/dean_review_claim/<approval_id>', methods=['GET', 'POST'])
def dean_review_claim(approval_id):
    approval = ClaimApproval.query.get(approval_id)
    if not approval:
        abort(404, description="Approval record not found")

    # Check if already voided
    voided_response = is_already_voided(approval)
    if voided_response:
        return voided_response

    # Check if already reviewed
    reviewed_response = is_already_reviewed(approval, ["Pending Acknowledgement by Dean / HOS"])
    if reviewed_response:
        return reviewed_response

    # Otherwise render the review page
    if request.method == 'GET':
        return render_template("reviewClaimApprovalRequest.html", approval=approval)

    # POST logic
    action = request.form.get('action')
    if action == 'approve':
        try:
            process_signature_and_upload(approval, request.form.get('signature_data'), "E")
            approval.status = "Pending Acknowledgement by HR"
            approval.last_updated = get_current_utc()
            db.session.commit()

            hr = Other.query.filter(Other.role == "Human Resources", Other.email != "tingting.eng@newinti.edu.my").first()

            try:
                notify_approval(approval, hr.email if hr else None, "hr_review_claim", "HR")
            except Exception as e:
                logger.error(f"Failed to notify HR: {e}")

            return '''<script>alert("Request approved successfully. You may now close this window.")</script>'''
        except Exception as e:
            return str(e), 500

    elif action == 'reject':
        reason = request.form.get('reject_reason')
        if not reason:
            return "Rejection reason required", 400
        
        approval.status = f"Rejected by Dean / HOS - {reason.strip()}"
        approval.last_updated = get_current_utc()

        # Delete related records and rename approval file
        delete_claim_and_attachment(approval.approval_id, "REJECTED")

        try:
            send_rejection_email("Dean", approval, reason.strip())
        except Exception as e:
            logger.error(f"Failed to send rejection email: {e}")

        return '''<script>alert("Request rejected successfully. You may now close this window.")</script>'''
    
    return "Invalid action", 400

@app.route('/api/hr_review_claim/<approval_id>', methods=['GET', 'POST'])
def hr_review_claim(approval_id):
    approval = ClaimApproval.query.get(approval_id)
    if not approval:
        abort(404, description="Approval record not found")

    # Check if already voided
    voided_response = is_already_voided(approval)
    if voided_response:
        return voided_response

    # Check if already reviewed
    reviewed_response = is_already_reviewed(approval, ["Pending Acknowledgement by HR"])
    if reviewed_response:
        return reviewed_response

    # Otherwise render the review page
    if request.method == 'GET':
        return render_template("reviewClaimApprovalRequest.html", approval=approval)
    
    action = request.form.get('action')
    if action == 'approve':
        try:
            process_signature_and_upload(approval, request.form.get('signature_data'), "G")
            approval.status = "Completed"
            approval.last_updated = get_current_utc()
            db.session.commit()

            """ # ---- Save LecturerClaim rows related to this approval ----
            lecturer_claims = LecturerClaim.query.filter_by(claim_id=approval.approval_id).all()
            for claim in lecturer_claims:
                row = {
                    "lecturer_id": claim.lecturer_id,
                    "department_id": approval.department_id,
                    "subject_id": claim.subject_id,
                    "date": claim.date.isoformat() if claim.date else None,
                    "lecture_hours": claim.lecture_hours,
                    "tutorial_hours": claim.tutorial_hours,
                    "practical_hours": claim.practical_hours,
                    "blended_hours": claim.blended_hours,
                    "total_cost": claim.total_cost,
                    "date_saved": get_current_utc()
                }

                append_to_csv(
                    "lecturer_claim_history.csv",
                    [
                        "lecturer_id","department_id","subject_id",
                        "date","lecture_hours","tutorial_hours","practical_hours","blended_hours",
                        "total_cost","date_saved"
                    ],
                    row
                ) """

            try:
                subject = f"Part-time Lecturer Claim Approval Request Completed  - {approval.lecturer.name} ({approval.subject_level})"
                body = (
                    f"Dear All,\n\n"
                    f"The part-time lecturer claim request has been fully approved by all parties.\n\n"
                    f"Please click the link below to access the final approved file:\n"
                    f"{approval.file_url}\n\n"
                    "Thank you for your cooperation.\n\n"
                    "Attachments are included for your reference.\n\n"
                    "Thank you,\n"
                    "The CourseXcel Team"
                )

                # Get final HR
                final_hr = Other.query.filter_by(role="Head of Human Resources").first()

                # Base recipients from related models
                recipients = [
                    approval.lecturer.email if approval.lecturer else None,
                    approval.program_officer.email if approval.program_officer else None,
                    approval.head.email if approval.head else None,
                    approval.department.dean_email if approval.department else None,
                ]

                # Get "Other" roles
                hr = Other.query.filter_by(role="Human Resources").first()

                # Append first HR if exists
                if hr and hr.email:
                    recipients.append(hr.email)

                # Append final HR (Head of Human Resources)
                if final_hr and final_hr.email:
                    recipients.append(final_hr.email)

                # Append all admins
                admins = Admin.query.all()
                for a in admins:
                    if a.email:
                        recipients.append(a.email)

                # Filter out any Nones or duplicates
                recipients = list(filter(None, set(recipients)))

                send_email(recipients, subject, body)
            except Exception as e:
                logger.error(f"Failed to notify All: {e}")

            return '''<script>alert("Request approved successfully. You may now close this window.")</script>'''
        except Exception as e:
            return str(e), 500

    elif action == 'reject':
        reason = request.form.get('reject_reason')
        if not reason:
            return "Rejection reason required", 400
        
        approval.status = f"Rejected by HR - {reason.strip()}"
        approval.last_updated = get_current_utc()

        # Delete related records and rename approval file
        delete_claim_and_attachment(approval.approval_id, "REJECTED")

        try:
            send_rejection_email("HR", approval, reason.strip())
        except Exception as e:
            logger.error(f"Failed to send rejection email: {e}")
        
        return '''<script>alert("Request rejected successfully. You may now close this window.")</script>'''
    
    return "Invalid action", 400

@app.route('/api/void_claim/<approval_id>', methods=['POST'])
@handle_db_connection
def void_claim(approval_id):
    try:
        data = request.get_json()
        reason = data.get("reason", "").strip()

        if not reason:
            return jsonify(success=False, error="Reason for voiding is required."), 400

        approval = ClaimApproval.query.get(approval_id)
        if not approval:
            return jsonify(success=False, error="Approval record not found."), 404

        current_status = approval.status

        # Allow voiding only at specific stages
        if current_status in [
            "Pending Acknowledgement by Lecturer",
            "Pending Acknowledgement by PO",
            "Pending Acknowledgement by HOP",
            "Pending Acknowledgement by Dean / HOS",
            "Pending Acknowledgement by HR"
        ]:
            approval.status = f"Voided - {reason}"
            approval.last_updated = get_current_utc()

            # Delete related records and rename approval file
            delete_claim_and_attachment(approval.approval_id, "VOIDED")
     
        else:
            return jsonify(success=False, error="Request cannot be voided at this stage."), 400

        # Determine recipients based on current stage
        recipients = []
        if current_status == "Pending Acknowledgement by HOP":
            recipients = [approval.program_officer.email]
        elif current_status == "Pending Acknowledgement by Dean / HOS":
            recipients = [approval.program_officer.email, approval.head.email]
        elif current_status == "Pending Acknowledgement by HR":
            recipients = [approval.program_officer.email, approval.head.email, approval.department.dean_email]

        recipients = list(set(filter(None, recipients)))  # Remove duplicates and None

        # Send notification emails
        subject = f"Part-time Lecturer Claim Request Voided - {approval.lecturer.name} ({approval.subject_level})"
        body = (
            f"Dear All,\n\n"
            f"The part-time lecturer claim request has been voided by the Requester.\n"
            f"Reason: {reason}\n\n"
            f"Please review the file here:\n{approval.file_url}\n"
            "Please do not take any further action on this request.\n\n"
            "Thank you,\n"
            "The CourseXcel Team"
        )

        if recipients:
            success = send_email(recipients, subject, body)
            if not success:
                logger.error(f"Failed to send void notification email to: {recipients}")
        
        return jsonify(success=True)

    except Exception as e:
        logger.error(f"Error voiding claim: {e}")
        return jsonify(success=False, error="Internal server error."), 500

@app.route('/lecturerProfilePage')
def lecturerProfilePage():
    lecturer_email = session.get('lecturer_email')
    if not lecturer_email:
        return redirect(url_for('loginPage'))

    lecturer = Lecturer.query.filter_by(email=lecturer_email).first()

    return render_template('lecturerProfilePage.html', lecturer=lecturer)

def delete_claim_and_attachment(approval_id, suffix):
    # Fetch the approval record first
    approval = ClaimApproval.query.get(approval_id)
    if not approval:
        logger.warning(f"No approval record found for ID {approval_id}")
        return
    
    # Rename file
    if approval.file_name:
        name, ext = os.path.splitext(approval.file_name)
        new_file_name = f"{name}_{suffix}{ext}"

        # Update Google Drive file name
        if approval.file_id:
            try:
                drive_service = get_drive_service()
                file_metadata = {"name": new_file_name}
                drive_service.files().update(fileId=approval.file_id, body=file_metadata).execute()
                logger.info(f"Renamed Google Drive file {approval.file_name} -> {new_file_name}")
            except Exception as e:
                logger.error(f"Failed to rename Google Drive file '{approval.file_name}': {e}")

        # Update DB field
        approval.file_name = new_file_name
    
    # Delete linked LecturerClaim entries
    LecturerClaim.query.filter_by(claim_id=approval_id).delete(synchronize_session=False)

    # Delete related attachments
    try:
        drive_service = get_drive_service()
        attachments_to_delete = ClaimAttachment.query.filter_by(claim_id=approval_id).all()
        for attachment in attachments_to_delete:
            try:
                # Extract file ID from Google Drive URL
                match = re.search(r'/d/([a-zA-Z0-9_-]+)', attachment.attachment_url)
                if not match:
                    logger.warning(f"Invalid Google Drive URL format for attachment {attachment.attachment_name}")
                    continue
                drive_attachment_id = match.group(1)

                # Delete file from Google Drive
                drive_service.files().delete(fileId=drive_attachment_id).execute()

                # Delete attachment record from database
                db.session.delete(attachment)

            except Exception as e:
                logger.error(f"Failed to delete Drive attachment '{attachment.attachment_name}': {e}")
    except Exception as e:
        logger.error(f"Failed to initialize Drive service or delete attachments: {e}")

    # Commit DB changes
    db.session.commit()

def get_claim_attachments(approval_id):
    # Returns a list of ClaimAttachment objects
    return ClaimAttachment.query.filter_by(claim_id=approval_id).all()

def notify_approval(approval, recipient_email, next_review_route, greeting):
    if not recipient_email:
        logger.error("No recipient email provided for approval notification.")
        return

    review_url = url_for(next_review_route, approval_id=approval.approval_id, _external=True)

    # Get all attachments for this approval
    attachments = get_claim_attachments(approval.approval_id)
    attachment_list = [
        {'filename': att.attachment_name, 'url': att.attachment_url}
        for att in attachments
    ]

    subject = f"Part-time Lecturer Claim Approval Request - {approval.lecturer.name} ({approval.subject_level})"
    body = (
        f"Dear {greeting},\n\n"
        f"There is a part-time lecturer claim request pending your review and approval.\n\n"
        f"Please click the link below to review and approve or reject the request:\n"
        f"{review_url}\n\n"
    )

    if attachment_list:
        body += "Attachments are included for your reference.\n\n"

    body += "Thank you,\nThe CourseXcel Team"
    send_email(recipient_email, subject, body, attachments=attachment_list)

def send_rejection_email(role, approval, reason):
    subject = f"Part-time Lecturer Claim Request Rejected - {approval.lecturer.name} ({approval.subject_level})"

    role_names = {
        "PO": "Program Officer",
        "HOP": "Head of Programme",
        "Dean": "Dean / Head of School",
        "HR": "HR"
    }

    recipients_map = {
        "PO": [approval.lecturer.email] if approval.lecturer else [],
        "HOP": [
            approval.lecturer.email if approval.lecturer else None,
            approval.program_officer.email if approval.program_officer else None
        ],
        "Dean": [
            approval.lecturer.email if approval.lecturer else None,
            approval.program_officer.email if approval.program_officer else None,
            approval.head.email if approval.head else None
        ],
        "HR": [
            approval.lecturer.email if approval.lecturer else None,
            approval.program_officer.email if approval.program_officer else None,
            approval.head.email if approval.head else None,
            approval.department.dean_email if approval.department else None
        ]
    }

     # Clean up None values and deduplicate
    recipients = list(set(filter(None, recipients_map.get(role, []))))

    rejected_by = role_names.get(role, "Unknown Role")
    greeting = "Dear Requester" if role == "PO" else "Dear All"

    body = (
        f"{greeting},\n\n"
        f"The part-time lecturer claim approval request has been rejected by the {rejected_by}.\n\n"
        f"Reason for rejection: {reason}\n\n"
        f"You can review the file here:\n{approval.file_url}\n\n"
        "Please take necessary actions.\n\n"
        "Thank you,\n"
        "The CourseXcel Team"
    )

    send_email(recipients, subject, body)

def check_overdue_claims():
    now = get_current_utc()
    overdue_time = now - timedelta(hours=48)

    # Ensure overdue_time is UTC-aware
    overdue_time = to_utc_aware(overdue_time)

    # Filter pending > 48h
    approvals = ClaimApproval.query.filter(
        ClaimApproval.status.like("Pending%"),
        ClaimApproval.last_updated < overdue_time
    ).all()


    for approval in approvals:
        try:
            last_reminder = to_utc_aware(approval.last_reminder_sent)
            last_updated = to_utc_aware(approval.last_updated)

            # Skip if status updated within last 48h
            if last_updated and (now - last_updated) < timedelta(hours=48):
                continue

            # Skip if reminder already sent within last 48h
            if last_reminder and (now - last_reminder) < timedelta(hours=48):
                continue

            # Collect attachments
            attachments = get_claim_attachments(approval.approval_id)
            attachment_list = [
                {'filename': att.attachment_name, 'url': att.attachment_url}
                for att in attachments
            ]

            recipients, greeting, review_url = [], None, None

            # Map status → recipient and URL
            if approval.status == "Pending Acknowledgement by Lecturer" and approval.program_officer:
                recipients.append(approval.program_officer.email)
                greeting = "Lecturer"
                review_url = url_for("lecturer_review_requisition", approval_id=approval.approval_id, _external=True)

            elif approval.status == "Pending Acknowledgement by PO" and approval.program_officer:
                recipients.append(approval.program_officer.email)
                greeting = "Program Officer"
                review_url = url_for("po_review_requisition", approval_id=approval.approval_id, _external=True)

            elif approval.status == "Pending Acknowledgement by HOP" and approval.head:
                recipients.append(approval.head.email)
                greeting = "Head of Programme"
                review_url = url_for("head_review_requisition", approval_id=approval.approval_id, _external=True)

            elif approval.status == "Pending Acknowledgement by Dean / HOS" and approval.department:
                if approval.department.dean_email:
                    recipients.append(approval.department.dean_email)
                greeting = "Dean / HOS"
                review_url = url_for("dean_review_requisition", approval_id=approval.approval_id, _external=True)

            elif approval.status == "Pending Acknowledgement by HR":
                hr = Other.query.filter_by(role="Human Resources").first()
                if hr and hr.email:
                    recipients.append(hr.email)
                greeting = "HR"
                review_url = url_for("hr_review_requisition", approval_id=approval.approval_id, _external=True)

            if recipients and review_url:
                # Subject + body
                subject = f"REMINDER: Part-time Lecturer Claim Approval Request - {approval.lecturer.name} ({approval.subject_level})"
                body = (
                    f"Dear {greeting},\n\n"
                    f"This claim request has been pending since {format_utc(last_updated)}.\n"
                    f"Please review and take action using the link below:\n"
                    f"{review_url}\n\n"
                )

                if attachment_list:
                    body += "Attachments are included for your reference.\n\n"

                body += "Thank you,\nThe CourseXcel Team"
                send_email(recipients, subject, body, attachments=attachment_list)

                # Update reminder timestamp
                approval.last_reminder_sent = now
                db.session.commit()

                logger.info(f"Reminder sent to {recipients} for approval {approval.approval_id}")
            else:
                logger.warning(f"No recipients found for approval {approval.approval_id} with status {approval.status}")

        except Exception as e:
            logger.error(f"Failed to send reminder for {approval.approval_id}: {e}")
