from app import db
from sqlalchemy import Numeric, DateTime, func

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

    lecturers = db.relationship('Lecturer', backref='department', passive_deletes=True)
    program_officers = db.relationship('ProgramOfficer', backref='department', passive_deletes=True)
    heads = db.relationship('Head', backref='department', passive_deletes=True)

    def __repr__(self):
        return f'<Department {self.department_id}>'

class Subject(db.Model):
    __tablename__ = 'subject'

    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_code = db.Column(db.String(15), unique=True, nullable=False)
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

    lecturer_subjects = db.relationship('LecturerSubject', backref='subject', passive_deletes=True)
    requisitions = db.relationship('RequisitionApproval', backref='subject', passive_deletes=True)

    def __repr__(self):
        return f'<Subject {self.subject_id}>'

class ProgramOfficer(db.Model):
    __tablename__ = 'program_officer'

    po_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100),unique=True, nullable=False)
    password = db.Column(db.CHAR(76), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)

    department = db.relationship('Department', backref='program_officer', passive_deletes=True)
    requisitions = db.relationship('RequisitionApproval', backref='program_officer', passive_deletes=True)
    claims = db.relationship('ClaimApproval', backref='program_officer', passive_deletes=True)

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
    ic_no = db.Column(db.String(12), unique=True, nullable=False)

    department = db.relationship('Department', backref='lecturer', passive_deletes=True)
    files = db.relationship('LecturerFile', backref='lecturer', cascade='all, delete', passive_deletes=True)
    requisitions = db.relationship('RequisitionApproval', backref='lecturer', passive_deletes=True)
    claims = db.relationship('ClaimApproval', backref='lecturer', passive_deletes=True)
    lecturer_subjects = db.relationship('LecturerSubject', backref='lecturer', passive_deletes=True)

    def __repr__(self):
        return f'<Lecturer: {self.lecturer_id}>'
    
class LecturerFile(db.Model):
    __tablename__ = 'lecturer_file'

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Lecturer File: {self.file_id}>'

class Head(db.Model):
    __tablename__ = 'head'

    head_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)

    department = db.relationship('Department', backref='head', passive_deletes=True)
    subjects = db.relationship('Subject', backref='head', passive_deletes=True)
    requisitions = db.relationship('RequisitionApproval', backref='head', passive_deletes=True)
    claims = db.relationship('ClaimApproval', backref='head', passive_deletes=True)

    def __repr__(self):
        return f'<Head: {self.head_id}>'

class Other(db.Model):
    __tablename__ = 'other'

    other_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Other: {self.other_id}>'

class RequisitionApproval(db.Model):
    __tablename__ = 'requisition_approval'

    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='SET NULL'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id', ondelete='SET NULL'), nullable=True)
    po_id = db.Column(db.Integer, db.ForeignKey('program_officer.po_id', ondelete='SET NULL'), nullable=True)
    head_id = db.Column(db.Integer, db.ForeignKey('head.head_id', ondelete='SET NULL'), nullable=True)
    sign_col = db.Column(db.Integer, nullable=True)
    file_id = db.Column(db.String(100), nullable=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    last_updated = db.Column(DateTime, default=func.now(), onupdate=func.now())

    department = db.relationship('Department', backref='requisition_approvals', passive_deletes=True)

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
    hourly_rate = db.Column(db.Integer, default=0)
    total_cost = db.Column(Numeric(9, 4), default=0)

    __table_args__ = (
        db.PrimaryKeyConstraint('lecturer_id', 'requisition_id', 'subject_id'),
    )

    def __repr__(self):
        return f'<Lecturer Subject: {self.subject_id}>'

class ClaimApproval(db.Model):
    __tablename__ = 'claim_approval'

    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id', ondelete='SET NULL'), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='SET NULL'), nullable=True)
    po_id = db.Column(db.Integer, db.ForeignKey('program_officer.po_id', ondelete='SET NULL'), nullable=True)
    head_id = db.Column(db.Integer, db.ForeignKey('head.head_id', ondelete='SET NULL'), nullable=True)    
    sign_col = db.Column(db.Integer, nullable=True)
    file_id = db.Column(db.String(100), nullable=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    last_updated = db.Column(DateTime, default=func.now(), onupdate=func.now())

    department = db.relationship('Department', backref='claim_approvals', passive_deletes=True)

    def __repr__(self):
        return f'<Claim Approval: {self.approval_id}>'
