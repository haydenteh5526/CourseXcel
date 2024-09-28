from app import create_app, db
from app.models import User, Lecturer, Subject
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def init_db():
    # Create the app context
    app = create_app()
    
    with app.app_context():
        # Create all tables if they do not exist
        db.create_all()
        print("Tables created successfully or already exist.")

        # Populate initial data only if no data exists
        try:
            # Check if a sample user exists, if not, create one
            if User.query.first() is None:
                user = User(email='admin@example.com')
                user.set_password('password123')  # Use the set_password method to hash the password
                db.session.add(user)
                print("Added sample user.")

            # Check if any lecturers exist, if not, create some
            if Lecturer.query.first() is None:
                lecturers = [
                    Lecturer(name='John Doe', level='Senior Lecturer', email='john.doe@example.com', hourly_rate=50.0),
                    Lecturer(name='Jane Smith', level='Associate Professor', email='jane.smith@example.com', hourly_rate=60.0)
                ]
                db.session.add_all(lecturers)
                print("Added sample lecturers.")

            # Check if any subjects exist, if not, create some
            if Subject.query.first() is None:
                subjects = [
                    Subject(code='CS101', title='Introduction to Computer Science'),
                    Subject(code='CS201', title='Advanced Web Development')
                ]
                db.session.add_all(subjects)
                print("Added sample subjects.")

            # Commit the changes to the database
            db.session.commit()
            print("Database initialized with sample data.")

        except IntegrityError:
            # Rollback the session in case of any constraint violations
            db.session.rollback()
            print("IntegrityError: Data already exists or integrity constraints were violated.")

        except Exception as e:
            # Rollback the session in case of unexpected errors
            db.session.rollback()
            print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    init_db()
