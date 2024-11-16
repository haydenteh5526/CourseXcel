from functools import wraps
from flask import current_app
from sqlalchemy.exc import OperationalError
from app import db
import time

def handle_db_connection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                result = f(*args, **kwargs)
                db.session.commit()
                return result
            except OperationalError as e:
                if retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(0.5)
                    db.session.rollback()
                    continue
                raise
            except Exception as e:
                db.session.rollback()
                raise
        return f(*args, **kwargs)
    return decorated_function

def cleanup_db():
    """Clean up database connections"""
    db.session.remove()
    db.engine.dispose()
