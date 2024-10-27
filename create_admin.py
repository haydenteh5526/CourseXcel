from app import db, bcrypt
from app.models import Admin

def create_admin():
    try:
        # Create new admin user with the same credentials as before
        admin = Admin(
            admin_id=1,
            email='admin1@example.com',
            password=bcrypt.generate_password_hash('password').decode('utf-8')
        )
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Email: admin1@example.com")
        print("Password: password")
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.session.rollback()

if __name__ == "__main__":
    create_admin()
