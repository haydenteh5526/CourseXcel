import os

class Config:
    # Use an environment variable for the secret key; fall back to a hardcoded value
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # Database URI for SQLAlchemy; ensure username, password, and db name are correct
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://if0_37251857:ShKv8cddwqF@localhost/if0_37251857_coursepdfextractor'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directories for file uploads and outputs
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.getcwd(), 'outputs')

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf'}
