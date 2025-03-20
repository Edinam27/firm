# create_tables.py
from app import create_app
from extensions import db
from models import Review, Order, ShippingAddress  # Import all models you need to create

# Create app with default config
app = create_app()

# Use app context to create tables
with app.app_context():
    db.create_all()
    print("Tables created successfully!")