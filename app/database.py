import logging, time
from app import db
from functools import wraps
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, StatementError

logger = logging.getLogger(__name__)

def handle_db_connection(f):
    """
    Decorator that ensures a stable database connection for any Flask route or function.
    Automatically retries failed connections up to 3 times before raising an error.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Verify DB connection
                db.session.execute(text('SELECT 1'))
                logger.debug("[BACKEND] Database connection check successful.")

                # Execute the wrapped function
                result = f(*args, **kwargs)

                # Commit if no issues
                db.session.commit()
                logger.debug("[BACKEND] Database transaction committed successfully.")
                return result

            except (OperationalError, StatementError) as e:
                db.session.rollback()
                logger.warning(
                    f"[BACKEND] Database operational/statement error: {e}. "
                    f"Attempt {retry_count + 1} of {max_retries}."
                )

                # Retry logic
                if retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(0.5)  # Short delay before retry
                    db.session.remove()
                    db.engine.dispose()
                    logger.info("[BACKEND] Retrying database connection...")
                    continue
                else:
                    logger.error(f"[BACKEND] Database connection failed after {max_retries} retries: {e}")
                    raise

            except Exception as e:
                # Catch-all for other errors
                db.session.rollback()
                logger.error(f"[BACKEND] Unexpected database error in function '{f.__name__}': {e}")
                raise

        # Fallback (should not reach here)
        logger.critical("[BACKEND] Unexpected code path reached in handle_db_connection.")
        return f(*args, **kwargs)

    return decorated_function

def cleanup_db():
    """
    Clean up database sessions and connections safely.
    Useful during app shutdown or error handling.
    """
    try:
        db.session.remove()
        db.engine.dispose()
        logger.info("[BACKEND] Database session and engine disposed successfully.")
    except Exception as e:
        logger.warning(f"[BACKEND] Database cleanup encountered an issue: {e}")
