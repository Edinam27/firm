# models.py
from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True)
    status = db.Column(db.String(50), default='pending')
    subtotal = db.Column(db.Float, nullable=False)
    shipping = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.DateTime)
    
    shipping_address = db.relationship('ShippingAddress', backref='order', uselist=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class ShippingAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))  # Changed from image to image_url
    stock = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)

class User(UserMixin, db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(60), nullable=False) 
    user_type = db.Column(db.String(20), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    
#Relationship
individual_profile = db.relationship('IndividualProfile', backref='user', uselist=False)
company_profile = db.relationship('CompanyProfile', backref='user', uselist=False)
charity_profile = db.relationship('CharityProfile', backref='user', uselist=False)
group_profile = db.relationship('GroupProfile', backref='user', uselist=False)



class IndividualProfile(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    first_name = db.Column(db.String(50), nullable=False) 
    last_name = db.Column(db.String(50), nullable=False) 
    phone = db.Column(db.String(20)) 
    address = db.Column(db.String(200)) 
    date_of_birth = db.Column(db.Date)

class CompanyProfile(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    company_name = db.Column(db.String(100), nullable=False) 
    registration_number = db.Column(db.String(50)) 
    contact_person = db.Column(db.String(100)) 
    business_phone = db.Column(db.String(20)) 
    business_address = db.Column(db.String(200)) 
    industry = db.Column(db.String(100))

class CharityProfile(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    charity_name = db.Column(db.String(100), nullable=False) 
    charity_number = db.Column(db.String(50)) 
    contact_person = db.Column(db.String(100)) 
    charity_phone = db.Column(db.String(20)) 
    charity_address = db.Column(db.String(200)) 
    mission_statement = db.Column(db.Text)

class GroupProfile(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    group_name = db.Column(db.String(100), nullable=False) 
    group_type = db.Column(db.String(50)) 
    contact_person = db.Column(db.String(100)) 
    group_phone = db.Column(db.String(20)) 
    group_address = db.Column(db.String(200)) 
    member_count = db.Column(db.Integer)

# models.py
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plan.id'), nullable=False)
    status = db.Column(db.String(20), default='active')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    next_billing_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='subscriptions')
    plan = db.relationship('SubscriptionPlan')
    
class Review(db.Model):
    __tablename__ = 'review'  # Changed from 'reviews' to match naming convention
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Changed from 'products.id'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Changed from 'users.id'
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('reviews', lazy=True))
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    
    # This would be handled separately if you're storing images
    # images = db.relationship('ReviewImage', backref='review', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Review {self.id} for Product {self.product_id}>'
    
    @property
    def avatar(self):
        # Return a default avatar or user's avatar if available
        # This is a placeholder - implement based on your user model
        return 'default-avatar.jpg'
    
    @property
    def name(self):
        # Return the user's name
        # This is a placeholder - implement based on your user model
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return "Anonymous"
    
    @property
    def images(self):
        # Placeholder for review images
        # In a real implementation, this would return actual image paths
        return []

class SubscriptionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    billing_interval = db.Column(db.String(20), default='monthly')  # monthly, quarterly, yearly
    stripe_price_id = db.Column(db.String(100), nullable=False)
    features = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    
def set_password(self, password):
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password_hash, password)

def __repr__(self):
    return f'<User {self.email}>'


# If these methods aren't already defined by UserMixin, add them:
def get_id(self):
    return str(self.id)

@property
def is_authenticated(self):
    return True

@property
def is_active(self):
    return True

@property
def is_anonymous(self):
    return False
    
