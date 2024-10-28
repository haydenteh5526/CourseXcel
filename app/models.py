from app import db
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Admin(db.Model):    
    __tablename__ = 'admin'
    __table_args__ = {'extend_existing': True}
    admin_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(76))
    email = db.Column(db.String(100))

    def __repr__(self):
        return f'<Admin {self.email}>'

class Department(db.Model):
    __tablename__ = 'department'
    __table_args__ = {'extend_existing': True}
    
    department_code = db.Column(db.String(10), primary_key=True)
    department_name = db.Column(db.String(50))

    def __repr__(self):
        return f'<Department {self.department_name}>'

class Lecturer(db.Model):
    __tablename__ = 'lecturer'
    __table_args__ = {'extend_existing': True}
    
    lecturer_id = db.Column(db.String(10), primary_key=True)
    lecturer_name = db.Column(db.String(50))
    email_address = db.Column(db.String(100))
    level = db.Column(db.Integer)
    hourly_rate = db.Column(db.DECIMAL(10,2))
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code'))
    ic_no = db.Column(db.String(12), nullable=False)

    def __repr__(self):
        return f'<Lecturer: {self.name}, {self.department_id}>'

class Person(db.Model):
    __tablename__ = 'person'
    __table_args__ = {'extend_existing': True}
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(76))
    email = db.Column(db.String(100))
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code'))

    def __repr__(self):
        return f'<Person: {self.email}>'

class Program(db.Model):
    __tablename__ = 'program'
    __table_args__ = {'extend_existing': True}
    
    program_code = db.Column(db.String(10), primary_key=True)
    program_name = db.Column(db.String(50))
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code'))
    level = db.Column(db.String(20))

    def __repr__(self):
        return f'<Program {self.program_code}, {self.program_name}>'

class Subject(db.Model):
    __tablename__ = 'subject'
    __table_args__ = {'extend_existing': True}
    
    subject_code = db.Column(db.String(10), primary_key=True)
    subject_title = db.Column(db.String(100))
    program_code = db.Column(db.String(10), db.ForeignKey('program.program_code'))
    lecturer_id = db.Column(db.String(10), db.ForeignKey('lecturer.lecturer_id'))
    lecture_hours = db.Column(db.Float)
    tutorial_hours = db.Column(db.Float)
    practical_hours = db.Column(db.Float)
    blended_hours = db.Column(db.Float)
    lecture_weeks = db.Column(db.Integer)
    tutorial_weeks = db.Column(db.Integer)
    practical_weeks = db.Column(db.Integer)
    blended_weeks = db.Column(db.Integer)
    course_level = db.Column(db.String(50))

    def __repr__(self):
        return f'<Subject {self.subject_code}>'
