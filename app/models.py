from app import db

class Admin(db.Model):    
    admin_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.CHAR(76), nullable=True)
    email = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Admin {self.email}>'

class Department(db.Model):    
    department_code = db.Column(db.String(10), primary_key=True)
    department_name = db.Column(db.String(50), nullable=True)
    dean_name = db.Column(db.String(50), nullable=True)
    dean_email = db.Column(db.String(100), nullable=True)

    lecturers = db.relationship('Lecturer', backref='department', passive_deletes=True)
    program_officers = db.relationship('ProgramOfficer', backref='department', passive_deletes=True)
    hops = db.relationship('Head', backref='department', passive_deletes=True)

    def __repr__(self):
        return f'<Department {self.department_code}>'

class Lecturer(db.Model):    
    lecturer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
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

class ProgramOfficer(db.Model):
    __tablename__ = 'program_officer'
    po_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.CHAR(76), nullable=True)
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete='SET NULL'), nullable=True)

    def __repr__(self):
        return f'<ProgramOfficer: {self.email}>'
    
class Other(db.Model):
    other_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<Other: {self.email}>'
    
class Subject(db.Model):
    subject_code = db.Column(db.String(15), primary_key=True)
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

    def __repr__(self):
        return f'<Subject {self.subject_title}>'
    
class Head(db.Model):
    head_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete='SET NULL'), nullable=True)

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
