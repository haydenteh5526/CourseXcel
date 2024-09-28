from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register Blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
