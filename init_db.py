from app import app, db
from models import User, Lecturer, Subject
from datetime import date
from sqlalchemy.exc import ProgrammingError, IntegrityError

def init_db():
    with app.app_context():
        # Check if tables exist and create them if they don't
        try:
            db.create_all()
            print("Tables created or already exist.")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return

        # Check if data already exists and populate sample data
        try:
            if User.query.first() is None:
                # Create a sample user
                user = User(email='admin@example.com')
                user.set_password('password123')
                db.session.add(user)
                print("Sample user added.")

            if Lecturer.query.first() is None:
                # Create sample lecturers
                lecturers = [
                    Lecturer(name='John Doe', level='Senior Lecturer', email='john.doe@example.com', hourly_rate=50.0),
                    Lecturer(name='Jane Smith', level='Associate Professor', email='jane.smith@example.com', hourly_rate=60.0)
                ]
                db.session.add_all(lecturers)
                print("Sample lecturers added.")

            if Subject.query.first() is None:
                # Create sample subjects
                subjects = [
                    Subject(code='CS101', title='Introduction to Computer Science'),
                    Subject(code='CS201', title='Advanced Web Development')
                ]
                db.session.add_all(subjects)
                print("Sample subjects added.")

            # Commit the session
            db.session.commit()
            print("Database initialized with sample data.")
        except IntegrityError:
            db.session.rollback()
            print("IntegrityError: Data already exists or other integrity constraints were violated.")
        except Exception as e:
            db.session.rollback()
            print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    init_db()
