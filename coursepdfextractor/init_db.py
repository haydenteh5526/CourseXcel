from run import app, db
from models import User, Lecturer, Subject
from datetime import date
from sqlalchemy.exc import ProgrammingError, IntegrityError

def init_db():
    with app.app_context():
        # Check if tables exist
        try:
            User.query.first()
            Lecturer.query.first()
            Subject.query.first()
        except ProgrammingError:
            # Tables don't exist, create them
            db.create_all()
            print("Tables created.")
        
        # Check if data already exists
        if User.query.first() is None:
            # Create a sample user
            user = User(email='admin@example.com')
            user.set_password('password123')
            db.session.add(user)

        if Lecturer.query.first() is None:
            # Create sample lecturers
            lecturers = [
                Lecturer(name='John Doe', level='Senior Lecturer', email='john.doe@example.com', hourly_rate=50.0),
                Lecturer(name='Jane Smith', level='Associate Professor', email='jane.smith@example.com', hourly_rate=60.0)
            ]
            db.session.add_all(lecturers)

        if Subject.query.first() is None:
            # Create sample subjects
            subjects = [
                Subject(code='CS101', title='Introduction to Computer Science', start_date=date(2024, 1, 15), end_date=date(2024, 5, 15)),
                Subject(code='CS201', title='Advanced Web Development', start_date=date(2024, 2, 1), end_date=date(2024, 6, 1))
            ]
            db.session.add_all(subjects)

        try:
            db.session.commit()
            print("Database initialized with sample data.")
        except IntegrityError:
            db.session.rollback()
            print("Sample data already exists. Skipping initialization.")

if __name__ == '__main__':
    init_db()