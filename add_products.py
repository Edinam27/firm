# add_products.py
from app import create_app
from extensions import db
from models import Product

def add_more_products():
    app = create_app()
    
    with app.app_context():
        new_products = [
            Product(
                name='Sparkling Mineral Water',
                description='Naturally carbonated mineral water with a refreshing fizz.',
                price=2.79,
                image_url='/static/images/glass.jpg',
                stock=70,
                is_featured=True
            ),
            Product(
                name='Vitamin Enhanced Water',
                description='Purified water enriched with essential vitamins and minerals.',
                price=3.29,
                image_url='/static/images/glass.jpg',
                stock=65,
                is_featured=False
            ),
            Product(
                name='Glacier Spring Water',
                description='Pure water sourced from pristine glacier springs.',
                price=2.89,
                image_url='/static/images/glass.jpg',
                stock=95,
                is_featured=True
            ),
            Product(
                name='Ionized Alkaline Water',
                description='Premium alkaline water with balanced pH and electrolytes.',
                price=3.99,
                image_url='/static/images/glass.jpg',
                stock=55,
                is_featured=True
            )
        ]
        
        for product in new_products:
            db.session.add(product)
        
        db.session.commit()
        print("Added 4 new products successfully!")

if __name__ == '__main__':
    add_more_products()