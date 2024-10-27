from app import db

# Drop all tables
db.drop_all()

# Create all tables
db.create_all()

print("Database tables have been reset successfully!")
