from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from extensions import db, login_manager
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Initialize migrate after db
    migrate = Migrate(app, db)
    
    # Register blueprints
    from routes import bp
    app.register_blueprint(bp)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app

# Don't create app instance here, let create_app handle it
# This allows for more flexibility in testing and deployment

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
