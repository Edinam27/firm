# Create a file named seed_database.py

from app import create_app, db
from models import Product

def seed_products():
    app = create_app()
    
    with app.app_context():
        # Clear existing products
        Product.query.delete()
        
        # Create products
        products = [
            Product(
                name='Natural Spring Water',
                description='Pure, refreshing spring water from pristine mountain sources.',
                price=1.99,
                image_url='images/glass.jpg',
                stock=100,
                is_featured=True
            ),
            Product(
                name='Alkaline Water',
                description='pH balanced water with essential minerals for optimal hydration.',
                price=2.49,
                image_url='images/glass.jpg',
                stock=80,
                is_featured=True
            ),
            Product(
                name='Mineral-Enhanced Water',
                description='Enhanced with natural minerals for a crisp, refreshing taste.',
                price=2.29,
                image_url='images/glass.jpg',
                stock=90,
                is_featured=False
            ),
            Product(
                name='Electrolyte Water',
                description='Fortified with electrolytes for superior hydration and performance.',
                price=2.99,
                image_url='images/glass.jpg',
                stock=75,
                is_featured=True
            ),
            Product(
                name='Mountain Stream Water',
                description='Sourced from high-altitude mountain streams for ultimate purity.',
                price=2.19,
                image_url='images/glass.jpg',
                stock=85,
                is_featured=False
            ),
            Product(
                name='Premium Artesian Water',
                description='Naturally filtered through ancient rock layers for exceptional taste.',
                price=3.49,
                image_url='images/glass.jpg',
                stock=60,
                is_featured=True
            )
        ]
        
        # Add products to database
        for product in products:
            db.session.add(product)
            
        # Commit changes
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_products()