from app import create_app
from extensions import db
from models import Product, User
from werkzeug.security import generate_password_hash

def reset_db():
    app = create_app()
    
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        # Create products
        products = [
            Product(
                name='Premium Spring Water',
                description='Pure spring water sourced from natural mountain springs.',
                price=2.99,
                image_url='/static/images/glass.jpg',
                stock=100,
                is_featured=True
            ),
            Product(
                name='Sparkling Mineral Water',
                description='Naturally carbonated mineral water with a refreshing fizz.',
                price=3.49,
                image_url='/static/images/bottle.jpg',
                stock=75,
                is_featured=True
            ),
            Product(
                name='Alkaline Water',
                description='pH balanced water for optimal hydration.',
                price=4.99,
                image_url='/static/images/bulk.webp',
                stock=50,
                is_featured=False
            ),
            Product(
                name='Electrolyte Water',
                description='Enhanced with essential minerals and electrolytes.',
                price=3.99,
                image_url='/static/images/glass.jpg',
                stock=80,
                is_featured=True
            ),
            Product(
                name='Vitamin-Infused Water',
                description='Water enriched with vitamins B and C.',
                price=4.49,
                image_url='/static/images/bottle.jpg',
                stock=60,
                is_featured=False
            ),
            Product(
                name='Mountain Spring Water',
                description='Crisp and clean water from mountain springs.',
                price=2.79,
                image_url='/static/images/bulk.webp',
                stock=120,
                is_featured=True
            ),
            Product(
                name='Artesian Well Water',
                description='Naturally filtered through layers of rock.',
                price=5.99,
                image_url='/static/images/glass.jpg',
                stock=40,
                is_featured=True
            )
        ]
        
        # Create users
        users = [
            User(
                email='admin@pureflow.com',
                password=generate_password_hash('admin123'),
                user_type='individual',
                is_active=True
            ),
            User(
                email='customer@example.com',
                password=generate_password_hash('customer123'),
                user_type='individual',
                is_active=True
            )
        ]
        
        # Add all products and users to the session
        for product in products:
            db.session.add(product)
        
        for user in users:
            db.session.add(user)
        
        # Commit the changes
        db.session.commit()
        print("Database reset complete! Added 7 products and 2 users.")

if __name__ == '__main__':
    reset_db()