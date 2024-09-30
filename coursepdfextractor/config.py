import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://if0_37251857:ShKv8cddwqF@sql205.infinityfree.com/if0_37251857_coursepdfextractor'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'outputs'
