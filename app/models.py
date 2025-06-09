from app import db

class Admin(db.Model):    
    __tablename__ = 'admin'

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.CHAR(76), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Admin {self.email}>'

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
        return f'<Department {self.department_code}>'

class Lecturer(db.Model):    
    __tablename__ = 'lecturer'

    lecturer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.CHAR(76), nullable=True)
    level = db.Column(db.String(5), nullable=True)
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete='SET NULL'), nullable=True)
    ic_no = db.Column(db.String(12), unique=True, nullable=False)

    files = db.relationship('LecturerFile', backref='lecturer', cascade='all, delete', passive_deletes=True)

    def __repr__(self):
        return f'<Lecturer: {self.email}>'
    
class LecturerFile(db.Model):
    __tablename__ = 'lecturer_file'

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete='CASCADE'), nullable=False)
    lecturer_name = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<File: {self.file_id}>'
    
class LecturerSubject(db.Model):
    __tablename__ = 'lecturer_subject'

    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_level = db.Column(db.String(50))
    subject_code = db.Column(db.String(15), unique=True, nullable=False)
    subject_title = db.Column(db.String(100))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    lecture_hours = db.Column(db.Integer, default=0)
    tutorial_hours = db.Column(db.Integer, default=0)
    practical_hours = db.Column(db.Integer, default=0)
    blended_hours = db.Column(db.Integer, default=0)
    lecture_weeks = db.Column(db.Integer, default=0)
    tutorial_weeks = db.Column(db.Integer, default=0)
    practical_weeks = db.Column(db.Integer, default=0)
    blended_weeks = db.Column(db.Integer, default=0)
    hourly_rate = db.Column(db.Integer, default=0)
    total_cost = db.Column(db.Integer, default=0)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id'), nullable=False)

class ProgramOfficer(db.Model):
    __tablename__ = 'program_officer'

    po_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100),unique=True, nullable=False)
    password = db.Column(db.CHAR(76), nullable=True)
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete='SET NULL'), nullable=True)

    def __repr__(self):
        return f'<ProgramOfficer: {self.email}>'
    
class Other(db.Model):
    __tablename__ = 'other'

    other_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Other: {self.email}>'
    
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

    def __repr__(self):
        return f'<Subject {self.subject_title}>'
    
class Head(db.Model):
    __tablename__ = 'head'

    head_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete='SET NULL'), nullable=True)

    subjects = db.relationship('Subject', backref='head', passive_deletes=True)

    def __repr__(self):
        return f'<Head: {self.email}>'

class RequisitionApproval(db.Model):
    __tablename__ = 'requisition_approval'

    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lecturer_name = db.Column(db.String(50), nullable=True)
    subject_level = db.Column(db.String(50), nullable=True)
    sign_col = db.Column(db.Integer, nullable=True)
    po_email = db.Column(db.String(100), nullable=True)
    head_email = db.Column(db.String(100), nullable=True)
    dean_email = db.Column(db.String(100), nullable=True)
    ad_email = db.Column(db.String(100), nullable=True)
    hr_email = db.Column(db.String(100), nullable=True)
    file_id = db.Column(db.String(100), nullable=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    last_updated = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Approval: {self.status}>'
    
class ClaimApproval(db.Model):
    __tablename__ = 'claim_approval'

    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lecturer_name = db.Column(db.String(50), nullable=True)
    sign_col = db.Column(db.Integer, nullable=True)
    lecturer_email = db.Column(db.String(100), nullable=True)
    po_email = db.Column(db.String(100), nullable=True)
    head_email = db.Column(db.String(100), nullable=True)
    dean_email = db.Column(db.String(100), nullable=True)
    ad_email = db.Column(db.String(100), nullable=True)
    hr_email = db.Column(db.String(100), nullable=True)
    file_id = db.Column(db.String(100), nullable=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    last_updated = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Approval: {self.status}>'
