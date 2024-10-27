from app import db

# Association table for many-to-many relationship between Lecturer and Subject
lecturer_subject = db.Table('lecturer_subject',
    db.Column('lecturer_id', db.String(10), db.ForeignKey('lecturer.lecturer_id'), primary_key=True),
    db.Column('subject_code', db.String(10), db.ForeignKey('subject.subject_code'), primary_key=True)
)

class Admin(db.Model):    
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.CHAR(76))
    email = db.Column(db.String(100))

    def __repr__(self):
        return f'<Admin {self.email}>'

class Department(db.Model):    
    __tablename__ = 'department'
    department_code = db.Column(db.String(10), primary_key=True)
    department_name = db.Column(db.String(50))

    lecturers = db.relationship('Lecturer', backref='department')
    programs = db.relationship('Program', backref='department')
    persons = db.relationship('Person', backref='department')

    def __repr__(self):
        return f'<Department {self.department_code}, {self.department_name}>'

class Lecturer(db.Model):    
    __tablename__ = 'lecturer'
    lecturer_id = db.Column(db.String(10), primary_key=True)
    lecturer_name = db.Column(db.String(50))
    email_address = db.Column(db.String(100))
    level = db.Column(db.Integer)
    hourly_rate = db.Column(db.Numeric(10,2))
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code'))
    ic_no = db.Column(db.String(12), nullable=False)
    
    # Relationship with subjects
    subjects = db.relationship('Subject', backref='lecturer')

    def __repr__(self):
        return f'<Lecturer: {self.lecturer_name}, {self.department_code}>'

class Person(db.Model):
    __tablename__ = 'person'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.CHAR(76))
    email = db.Column(db.String(100))
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete='CASCADE'))

    def __repr__(self):
        return f'<Person: {self.email}>'

class Program(db.Model):
    __tablename__ = 'program'
    program_code = db.Column(db.String(10), primary_key=True)
    program_name = db.Column(db.String(50))
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete='CASCADE'))
    level = db.Column(db.String(20))
    
    # Add overlaps parameter
    subjects = db.relationship('Subject', back_populates='program', overlaps="program")

    def __repr__(self):
        return f'<Program {self.program_code}, {self.program_name}>'

class Subject(db.Model):
    __tablename__ = 'subject'
    subject_code = db.Column(db.String(10), primary_key=True)
    subject_title = db.Column(db.String(100))
    program_code = db.Column(db.String(10), db.ForeignKey('program.program_code', ondelete='CASCADE', onupdate='CASCADE'))
    lecturer_id = db.Column(db.String(10), db.ForeignKey('lecturer.lecturer_id', ondelete='SET NULL'))
    program_level = db.Column(db.String(20))
    L = db.Column(db.Integer, default=0)
    T = db.Column(db.Integer, default=0)
    P = db.Column(db.Integer, default=0)

    # Add overlaps parameter
    program = db.relationship('Program', back_populates='subjects', overlaps="subjects")

    def __repr__(self):
        return f'<Subject {self.subject_code}>'
