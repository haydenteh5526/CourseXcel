from app import db

class Admin(db.Model):    
    admin_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.CHAR(76), nullable=True)

    def __repr__(self):
        return f'<Admin {self.email}>'

class Department(db.Model):    
    department_code = db.Column(db.String(10), primary_key=True)
    department_name = db.Column(db.String(50))
    dean_name = db.Column(db.String(50))
    dean_email = db.Column(db.String(100), unique=True, nullable=False)

    lecturers = db.relationship('Lecturer', backref='department')
    program_officers = db.relationship('ProgramOfficer', backref='department')

    def __repr__(self):
        return f'<Department {self.department_code}, {self.department_name}>'

class Lecturer(db.Model):    
    lecturer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.CHAR(76), nullable=True)
    ic_no = db.Column(db.String(12), nullable=False)
    level = db.Column(db.String(5))
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete="SET NULL"), nullable=True)

    files = db.relationship('LecturerFile', backref='lecturer', cascade='all, delete', lazy=True)

    def __repr__(self):
        return f'<Lecturer: {self.email}>'
    
class LecturerFile(db.Model):
    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturer.lecturer_id', ondelete="CASCADE"), nullable=False)
    lecturer_name = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<File: {self.file_id}>'

class ProgramOfficer(db.Model):
    po_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.CHAR(76), nullable=True)
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return f'<ProgramOfficer: {self.email}>'
    
class Other(db.Model):
    other_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50))

    def __repr__(self):
        return f'<Other: {self.email}>'

# Association table for subject-level relationship
subject_levels = db.Table('subject_levels',
    db.Column('subject_code', db.String(10), db.ForeignKey('subject.subject_code', ondelete="CASCADE"), primary_key=True),
    db.Column('level', db.String(50), primary_key=True)
)

class Subject(db.Model):
    subject_code = db.Column(db.String(10), primary_key=True)
    subject_title = db.Column(db.String(100), nullable=True)
    lecture_hours = db.Column(db.Integer)
    tutorial_hours = db.Column(db.Integer)
    practical_hours = db.Column(db.Integer)
    blended_hours = db.Column(db.Integer)
    lecture_weeks = db.Column(db.Integer)
    tutorial_weeks = db.Column(db.Integer)
    practical_weeks = db.Column(db.Integer)
    blended_weeks = db.Column(db.Integer)

    def get_levels(self):
        """Helper method to get levels for this subject"""
        result = db.session.query(subject_levels.c.level)\
            .filter(subject_levels.c.subject_code == self.subject_code)\
            .all()
        return [level[0] for level in result]

    def __repr__(self):
        return f'<Subject {self.subject_title}>'
    
class HOP(db.Model):
    hop_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.String(50))
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return f'<HOP: {self.email}>'
    
class Approval(db.Model):
    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50))
    last_updated = db.Column(db.String(50))

    def __repr__(self):
        return f'<Approval: {self.status}>'
