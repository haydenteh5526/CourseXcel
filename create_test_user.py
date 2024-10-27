from app import db, bcrypt
from app.models import Person

def create_test_user():
    try:
        # Check if test user already exists
        existing_user = Person.query.filter_by(email='test@example.com').first()
        
        if existing_user:
            print("Test user already exists:")
            print(f"Email: {existing_user.email}")
            print("Password: password")
        else:
            # Create new test user
            test_user = Person(
                email='test@example.com',
                password=bcrypt.generate_password_hash('password').decode('utf-8')
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully!")
            print("Email: test@example.com")
            print("Password: password")
            
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    create_test_user()
