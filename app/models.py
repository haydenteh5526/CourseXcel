from app import app, db
from cryptography.fernet import Fernet
from sqlalchemy import DateTime, func, Numeric

def encrypt_data(data):
    cipher_suite = Fernet(app.config['CRYPTO_KEY'])
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data):
    cipher_suite = Fernet(app.config['CRYPTO_KEY'])
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
    return decrypted_data

class Admin(db.Model):    
    __tablename__ = 'admin'

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.CHAR(76), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Admin {self.admin_id}>'

class Department(db.Model):    
    __tablename__ = 'department'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_code = db.Column(db.String(10), unique=True, nullable=False)
    department_name = db.Column(db.String(50), nullable=True)
    dean_name = db.Column(db.String(50), nullable=True)
    dean_email = db.Column(db.String(100), nullable=True)

    lecturers = db.relationship('Lecturer', back_populates='department', passive_deletes=True)
    program_officers = db.relationship('ProgramOfficer', back_populates='department', passive_deletes=True)
    heads = db.relationship('Head', back_populates='department', passive_deletes=True)
    requisition_approvals = db.relationship('RequisitionApproval', back_populates='department', passive_deletes=True)
    claim_approvals = db.relationship('ClaimApproval', back_populates='department', passive_deletes=True)

    def __repr__(self):
        return f'<Department {self.department_id}>'

class Subject(db.Model):
    __tablename__ = 'subject'

    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_code = db.Column(db.String(15), nullable=False)
    subject_title = db.Column(db.String(100), nullable=True)
    subject_level = db.Column(db.String(50), nullable=True)
    lecture_hours = db.Column(db.Integer, default=0)
    tutorial_hours = db.Column(db.Integer, default=0)
    practical_hours = db.Column(db.Integer, default=0)
    blended_hours = db.Column(db.Integer, default=0)
    lecture_weeks = db.Column(db.Integer, default=0)
    tutorial_weeks = db.Column(db.Integer, default=0)
    practical_weeks = db.Column(db.Integer, default=0)
    blended_weeks = db.Column(db.Integer, default=0)
    head_id = db.Column(db.Integer, db.ForeignKey('head.head_id', ondelete='SET NULL'), nullable=True)

    head = db.relationship('Head', back_populates='subjects')
    lecturer_subjects = db.relationship('LecturerSubject', backref='subject', passive_deletes=True)

    def __repr__(self):
        return f'<Subject {self.subject_id}>'
    
class Head(db.Model):
    __tablename__ = 'head'

    head_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)

    department = db.relationship('Department', back_populates='heads')
    requisition_approvals = db.relationship('RequisitionApproval', back_populates='head', passive_deletes=True)
    claim_approvals = db.relationship('ClaimApproval', back_populates='head', passive_deletes=True)
    subjects = db.relationship('Subject', back_populates='head', passive_deletes=True)

    def __repr__(self):
        return f'<Head: {self.head_id}>'

class ProgramOfficer(db.Model):
    __tablename__ = 'program_officer'

    po_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.CHAR(76), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)

    department = db.relationship('Department', back_populates='program_officers')
    requisition_approvals = db.relationship('RequisitionApproval', back_populates='program_officer', passive_deletes=True)
    claim_approvals = db.relationship('ClaimApproval', back_populates='program_officer', passive_deletes=True)

    def __repr__(self):
        return f'<Program Officer: {self.po_id}>'

class Lecturer(db.Model):    
    __tablename__ = 'lecturer'

    lecturer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.CHAR(76), nullable=True)
    level = db.Column(db.String(5), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)
    ic_no = db.Column(db.LargeBinary)  

    department = db.relationship('Department', back_populates='lecturers')
    files = db.relationship('LecturerFile', backref='lecturer', cascade='all, delete', passive_deletes=True)
    requisition_approvals = db.relationship('RequisitionApproval', backref='lecturer', passive_deletes=True)
    lecturer_subjects = db.relationship('LecturerSubject', backref='lecturer', passive_deletes=True)
    claim_approvals = db.relationship('ClaimApproval', backref='lecturer', passive_deletes=True)
    attachments = db.relationship('LecturerAttachment', backref='lecturer', cascade='all, delete', passive_deletes=True)

    def __repr__(self):
        return f'<Lecturer: {self.lecturer_id}>'
    
    def set_ic_no(self, ic_number):
        """Encrypt the IC number before saving."""
        self.ic_no = encrypt_data(ic_number)
    
    def get_ic_no(self):
        """Decrypt the IC number before displaying."""
        return decrypt_data(self.ic_no) if self.ic_no else None

class LecturerFile(db.Model):
    __tablename__ = 'lecturer_file'

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Lecturer File: {self.file_id}>'

class Other(db.Model):
    __tablename__ = 'other'

    other_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Other: {self.other_id}>'
    
class Rate(db.Model):
    __tablename__ = 'rate'

    rate_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Integer, default=0)
    status = db.Column(db.Boolean)

    lecturer_subject = db.relationship('LecturerSubject', backref='rate', passive_deletes=True)
    lecturer_claim = db.relationship('LecturerClaim', backref='rate', passive_deletes=True)

    def __repr__(self):
        return f'<Rate: {self.rate_id}>'

class RequisitionApproval(db.Model):
    __tablename__ = 'requisition_approval'

    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='SET NULL'), nullable=True)
    po_id = db.Column(db.Integer, db.ForeignKey('program_officer.po_id', ondelete='SET NULL'), nullable=True)
    head_id = db.Column(db.Integer, db.ForeignKey('head.head_id', ondelete='SET NULL'), nullable=True)
    subject_level = db.Column(db.String(50), nullable=True)
    sign_col = db.Column(db.Integer, nullable=True)
    file_id = db.Column(db.String(100), nullable=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    last_updated = db.Column(DateTime, default=func.now(), onupdate=func.now())

    department = db.relationship('Department', back_populates='requisition_approvals')
    program_officer = db.relationship('ProgramOfficer', back_populates='requisition_approvals')
    head = db.relationship('Head', back_populates='requisition_approvals')

    def __repr__(self):
        return f'<Requisition Approval: {self.approval_id}>'

class LecturerSubject(db.Model):
    __tablename__ = 'lecturer_subject'

    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='CASCADE'), nullable=False)
    requisition_id = db.Column(db.Integer, db.ForeignKey('requisition_approval.approval_id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id', ondelete='SET NULL'), nullable=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    total_lecture_hours = db.Column(db.Integer, default=0)
    total_tutorial_hours = db.Column(db.Integer, default=0)
    total_practical_hours = db.Column(db.Integer, default=0)
    total_blended_hours = db.Column(db.Integer, default=0)
    rate_id = db.Column(db.Integer, db.ForeignKey('rate.rate_id', ondelete='SET NULL'), nullable=True)
    total_cost = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.PrimaryKeyConstraint('lecturer_id', 'requisition_id', 'subject_id'),
    )

    def __repr__(self):
        return f'<Lecturer Subject: {self.requisition_id}>'

class ClaimApproval(db.Model):
    __tablename__ = 'claim_approval'

    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='SET NULL'), nullable=True)
    po_id = db.Column(db.Integer, db.ForeignKey('program_officer.po_id', ondelete='SET NULL'), nullable=True)
    head_id = db.Column(db.Integer, db.ForeignKey('head.head_id', ondelete='SET NULL'), nullable=True)
    subject_level = db.Column(db.String(50), nullable=True)
    sign_col = db.Column(db.Integer, nullable=True)
    file_id = db.Column(db.String(100), nullable=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    last_updated = db.Column(DateTime, default=func.now(), onupdate=func.now())

    department = db.relationship('Department', back_populates='claim_approvals')
    program_officer = db.relationship('ProgramOfficer', back_populates='claim_approvals')
    head = db.relationship('Head', back_populates='claim_approvals')

    def __repr__(self):
        return f'<Claim Approval: {self.approval_id}>'

class LecturerClaim(db.Model):
    __tablename__ = 'lecturer_claim'

    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='CASCADE'), nullable=False)
    requisition_id = db.Column(db.Integer, db.ForeignKey('requisition_approval.approval_id', ondelete='CASCADE'), nullable=False)
    claim_id = db.Column(db.Integer, db.ForeignKey('claim_approval.approval_id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id', ondelete='SET NULL'), nullable=True)
    date = db.Column(db.Date)
    lecture_hours = db.Column(db.Integer, default=0)
    tutorial_hours = db.Column(db.Integer, default=0)
    practical_hours = db.Column(db.Integer, default=0)
    blended_hours = db.Column(db.Integer, default=0)
    rate_id = db.Column(db.Integer, db.ForeignKey('rate.rate_id', ondelete='SET NULL'), nullable=True)
    total_cost = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.PrimaryKeyConstraint('lecturer_id', 'requisition_id', 'claim_id', 'subject_id'),
    )

    def __repr__(self):
        return f'<Lecturer Claim: {self.claim_id}>'

class LecturerAttachment(db.Model):
    __tablename__ = 'lecturer_attachment'

    attachment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attachment_name = db.Column(db.String(100), nullable=True)
    attachment_url = db.Column(db.String(500), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='CASCADE'), nullable=False)
    claim_id = db.Column(db.Integer, db.ForeignKey('claim_approval.approval_id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Lecturer Attachment: {self.attachment_id}>'