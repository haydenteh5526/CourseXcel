import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql://if0_37251857:ShKv8cddwqF@localhost/if0_37251857_coursepdfextractor'
    SQLALCHEMY_TRACK_MODIFICATIONS = False