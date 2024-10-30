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

    lecturers = db.relationship('Lecturer', backref='department')
    persons = db.relationship('Person', backref='department')

    def __repr__(self):
        return f'<Department {self.department_code}, {self.department_name}>'

class Lecturer(db.Model):    
    lecturer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lecturer_name = db.Column(db.String(50))
    level = db.Column(db.String(5))
    ic_no = db.Column(db.String(12), nullable=False)
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return f'<Lecturer: {self.lecturer_name}, {self.department_code}>'

class Person(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.CHAR(76), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department_code = db.Column(db.String(10), db.ForeignKey('department.department_code', ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return f'<Person: {self.email}>'

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
