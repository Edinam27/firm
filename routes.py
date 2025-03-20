# routes.py
from flask import Blueprint, jsonify, request, redirect, url_for, render_template, session, flash, request, jsonify, session, current_app
from models import (
    User, 
    Order, 
    ShippingAddress, 
    OrderItem, 
    Product, 
    IndividualProfile, 
    CompanyProfile, 
    CharityProfile, 
    GroupProfile, 
    Subscription, 
    SubscriptionPlan,
    Review
)
from extensions import db
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField, IntegerField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
import stripe
import logging
import json
import os
from flask_wtf.csrf import generate_csrf

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

@bp.after_request 
def add_csrf_token(response): 
    if 'text/html' in response.headers.get('Content-Type', ''): 
        response.set_cookie('csrf_token', generate_csrf()) 
        return response

@bp.route('/api/place-order', methods=['POST'])
def place_order():
    if 'cart' not in session:
        return jsonify({'success': False, 'error': 'Empty cart'})

    try:
        order = Order(
            user_id=session['user_id'],
            order_number=str(uuid.uuid4().hex[:8]),
            subtotal=calculate_subtotal(session['cart']),
            shipping=2.00,
            tax=calculate_tax(session['cart']),
            expected_delivery_date=datetime.utcnow() + timedelta(days=3)
        )
        order.total = order.subtotal + order.shipping + order.tax

        shipping_address = ShippingAddress(
            full_name=f"{request.form['firstName']} {request.form['lastName']}",
            street=request.form['address'],
            city=request.form['city'],
            postal_code=request.form['postalCode']
        )
        
        order.shipping_address = shipping_address

        for item in session['cart']:
            order_item = OrderItem(
                product_id=item['product_id'],
                quantity=item['quantity'],
                size=item['size']
            )
            order.items.append(order_item)

        db.session.add(order)
        db.session.commit()

        session.pop('cart', None)
        return jsonify({
            'success': True,
            'order_id': order.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session.get('user_id'):
        return redirect(url_for('login'))
        
    return render_template('order-confirmation.html', order=order)

def calculate_subtotal(cart):
    total = 0
    for item in cart:
        product = Product.query.get(item['product_id'])
        total += product.price * item['quantity']
    return total

def calculate_tax(cart):
    return calculate_subtotal(cart) * 0.08

@bp.route('/')
def index():
    products = Product.query.filter_by(is_featured=True).limit(3).all()
    return render_template('index.html', products=products)


@bp.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Get product reviews
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    
    # Get related products (same category or similar products)
    related_products = Product.query.filter(Product.id != product_id).limit(3).all()
    
    # Check if product is in user's wishlist
    in_wishlist = False
    if current_user.is_authenticated:
        # Assuming you have a Wishlist model with user_id and product_id fields
        # in_wishlist = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None
        pass
    
    return render_template(
        'product_detail.html',
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
        related_products=related_products,
        in_wishlist=in_wishlist,
        now=datetime.utcnow()  # For displaying dates
    )

@bp.route('/submit-review/<int:product_id>', methods=['POST'])
@login_required
def submit_review(product_id):
    product = Product.query.get_or_404(product_id)
    
    try:
        # Create new review
        review = Review(
            product_id=product_id,
            user_id=current_user.id,
            rating=int(request.form.get('rating')),
            title=request.form.get('title'),
            comment=request.form.get('comment'),
            created_at=datetime.utcnow()
        )
        
        # Handle image uploads if any
        if 'images' in request.files:
            images = request.files.getlist('images')
            # Process and save images
            # This would depend on your file storage solution
        
        db.session.add(review)
        db.session.commit()
        
        flash('Your review has been submitted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting review: {str(e)}', 'danger')
    
    return redirect(url_for('main.product_detail', product_id=product_id))

@bp.route('/api/cart-count')
def cart_count():
    count = 0
    if isinstance(session.get('cart'), dict):
        for item in session['cart'].values():
            count += item['quantity']
    return jsonify({'count': count})

@bp.route('/cart')
def cart():
    cart_items = []
    subtotal = 0.0
    
    try:
        if isinstance(session.get('cart'), dict):
            for cart_key, item_data in session['cart'].items():
                product_id = cart_key.split('_')[0]
                product = Product.query.get(int(product_id))
                
                if product:
                    quantity = item_data['quantity']
                    size = item_data['size']
                    
                    # Calculate price based on size
                    base_price = product.price
                    if size == '1L':
                        base_price *= 1.8
                    elif size == '2L':
                        base_price *= 3.2
                    
                    item_total = base_price * quantity
                    
                    cart_items.append({
                        'product': product,
                        'quantity': quantity,
                        'size': size,
                        'price': base_price,
                        'total': item_total
                    })
                    
                    subtotal += item_total
        
        shipping = 5.00 if subtotal > 0 else 0.00
        tax = subtotal * 0.08
        total = subtotal + shipping + tax
        
        print("Cart items:", cart_items)  # Debug line
        
        return render_template('cart.html',
                             cart_items=cart_items,
                             subtotal=subtotal,
                             shipping=shipping,
                             tax=tax,
                             total=total)
                             
    except Exception as e:
        print(f"Cart error: {str(e)}")
        session['cart'] = {}
        session.modified = True
        return render_template('cart.html', cart_items=[])

@bp.route('/checkout')
def checkout():
    if not current_user.is_authenticated:
        # Redirect to login with the correct blueprint prefix
        return redirect(url_for('main.login'))
    
    cart_items = []
    subtotal = 0.0
    
    try:
        if isinstance(session.get('cart'), dict):
            for cart_key, item_data in session['cart'].items():
                product_id = cart_key.split('_')[0]
                product = Product.query.get(int(product_id))
                
                if product:
                    quantity = item_data['quantity']
                    size = item_data['size']
                    base_price = product.price
                    
                    # Apply size multipliers
                    if size == '1L':
                        base_price *= 1.8
                    elif size == '2L':
                        base_price *= 3.2
                    
                    item_total = base_price * quantity
                    cart_items.append({
                        'product': product,
                        'quantity': quantity,
                        'size': size,
                        'price': base_price,
                        'total': item_total
                    })
                    subtotal += item_total
        
        shipping = 5.00 if subtotal > 0 else 0.00
        tax = subtotal * 0.08
        total = subtotal + shipping + tax
        
        # Create form for checkout
        form = CheckoutForm()
        
        # Pre-fill form with user data if available
        if current_user.is_authenticated:
            # Get user profile based on user type
            if current_user.user_type == 'individual':
                profile = IndividualProfile.query.filter_by(user_id=current_user.id).first()
                if profile:
                    form.firstName.data = profile.first_name
                    form.lastName.data = profile.last_name
                    form.address.data = profile.address
                    form.phone.data = profile.phone
            # Add similar blocks for other user types
        
        return render_template('checkout.html',
                             cart_items=cart_items,
                             subtotal=subtotal,
                             shipping=shipping,
                             tax=tax,
                             total=total,
                             form=form,
                             now=datetime.utcnow())
                             
    except Exception as e:
        flash('An error occurred during checkout', 'danger')
        return redirect(url_for('main.cart'))

from logging import getLogger

@bp.route('/api/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        logger.debug(f"Received add-to-cart request: {request.json}")

        if not request.json:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        product_id = request.json.get('product_id')
        size = request.json.get('size')
        quantity = request.json.get('quantity', 1)
        buy_now = request.json.get('buy_now', False)

        if not product_id or not size:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Initialize cart if needed
        if 'cart' not in session:
            session['cart'] = {}

        cart_key = f"{product_id}_{size}"
        product = Product.query.get(int(product_id))
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404

        # Calculate price based on size
        base_price = product.price
        if size == '1L':
            base_price *= 1.8
        elif size == '2L':
            base_price *= 3.2

        # Update cart
        if cart_key in session['cart']:
            session['cart'][cart_key]['quantity'] += quantity
        else:
            session['cart'][cart_key] = {
                'quantity': quantity,
                'size': size,
                'price': float(base_price),
                'total': float(base_price) * quantity,
                'product_name': product.name
            }

        session.modified = True

        # Calculate cart totals
        cart_count = sum(item['quantity'] for item in session['cart'].values())
        cart_total = sum(item['total'] for item in session['cart'].values())

        response_data = {
            'success': True,
            'cart_count': cart_count,
            'cart_total': round(cart_total, 2)
        }
        
        # If buy_now is true, include a redirect URL
        if buy_now:
            response_data['redirect'] = url_for('main.checkout')

        return jsonify(response_data)

    except Exception as e:
        logger.exception("Error in add_to_cart:")
        return jsonify({'success': False, 'error': str(e)}), 500


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    accept_terms = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number')
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Your Message', validators=[DataRequired()])
    subscribe = BooleanField('Subscribe to our newsletter')

class CheckoutForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Street Address', validators=[DataRequired()])
    addressLine2 = StringField('Apartment, Suite, etc.')
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', validators=[DataRequired()])
    zip = StringField('Zip Code', validators=[DataRequired()])
    deliveryInstructions = TextAreaField('Delivery Instructions')
    paymentMethod = SelectField('Payment Method', choices=[('creditCard', 'Credit Card'), ('paypal', 'PayPal')])
    sameAsShipping = BooleanField('Same as shipping address')
    termsAgree = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[DataRequired()])

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.account'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.account'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.account'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('main.register'))

        # Create new user
        user = User(
            email=email,
            password=generate_password_hash(password),
            user_type='individual'  # Default to individual for simplified registration
        )
        db.session.add(user)
        db.session.flush()  # Get user ID before committing

        # Create individual profile
        profile = IndividualProfile(
            user_id=user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )

        db.session.add(profile)
        db.session.commit()

        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('main.account'))

    return render_template('register.html', form=form)

@bp.route('/account')
@login_required
def account():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('account.html', orders=orders)

@bp.route('/api/update-cart', methods=['POST'])
def update_cart():
    try:
        # Validate Request Data
        if not request.json:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        product_id = request.json.get('product_id')
        size = request.json.get('size')
        quantity = request.json.get('quantity', 1)
        
        if not all([product_id, size, quantity]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        cart_key = f"{product_id}_{size}"
        
        # Update Cart
        if cart_key in session.get('cart', {}):
            if quantity <= 0:
                del session['cart'][cart_key]
            else:
                session['cart'][cart_key]['quantity'] = quantity
                session['cart'][cart_key]['total'] = round(
                    session['cart'][cart_key]['price'] * quantity, 2
                )
            session.modified = True
        
        # Calculate Cart Totals
        cart_count = sum(item['quantity'] for item in session.get('cart', {}).values())
        cart_total = sum(item['total'] for item in session.get('cart', {}).values())
        
        return jsonify({
            'success': True,
            'cart_count': cart_count,
            'cart_total': round(cart_total, 2)
        })
    except Exception as e:
        logger.exception("Error updating cart:")
        return jsonify({'success': False, 'error': str(e)}), 500
    
# Remove from Cart Endpoint
@bp.route('/api/remove-from-cart', methods=['POST'])
def remove_from_cart():
    try:
        if not request.json:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        product_id = request.json.get('product_id')
        size = request.json.get('size')

        if not all([product_id, size]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        cart_key = f"{product_id}_{size}"

        if cart_key in session.get('cart', {}):
            del session['cart'][cart_key]
            session.modified = True

        # Calculate cart totals
        cart_count = sum(item['quantity'] for item in session.get('cart', {}).values())
        cart_total = sum(item['total'] for item in session.get('cart', {}).values())

        return jsonify({
            'success': True,
            'cart_count': cart_count,
            'cart_total': round(cart_total, 2)
        })

    except Exception as e:
        logger.exception("Error removing from cart:")
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_cart_total(cart):
    total = 0
    for item in cart:
        product = Product.query.get(item['product_id'])
        total += product.price * item['quantity']
    return total

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Process the contact form submission
        # This could involve sending an email, saving to database, etc.
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('contact.html', form=form)

@bp.route('/api/newsletter-signup', methods=['POST'])
def newsletter_signup():
    email = request.json.get('email')
    if not email:
        return jsonify({'success': False, 'error': 'Email required'})
    
    # Add newsletter signup logic here
    return jsonify({'success': True})

@bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@bp.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/faq')
def faq():
    """Render the FAQ page."""
    return render_template('support/faq.html')


@bp.route('/shipping')
def shipping():
    """Render the Shipping Information page."""
    return render_template('support/shipping.html')


@bp.route('/returns')
def returns():
    """Render the Returns Policy page."""
    return render_template('support/returns.html')


@bp.route('/terms')
def terms():
    """Render the Terms of Service page."""
    return render_template('support/terms.html')


@bp.route('/privacy')
def privacy():
    """Render the Privacy Policy page."""
    return render_template('support/privacy.html')

stripe.api_key = 'your_stripe_secret_key'

@bp.route("/subscribe")
def subscribe():
    subscription_plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    form = SubscriptionForm()
    return render_template('subscribe.html', subscription_plans=subscription_plans, form=form)

class SubscriptionForm(FlaskForm):
    plan = SelectField('Plan', choices=[('basic', 'Basic Plan'), ('family', 'Family Plan'), ('premium', 'Premium Plan')])
    waterType = SelectField('Water Type', choices=[
        ('Spring Water', 'Spring Water'),
        ('Mineral Water', 'Mineral Water'),
        ('Alkaline Water', 'Alkaline Water'),
        ('Sparkling Water', 'Sparkling Water'),
        ('Mix (Premium plan only)', 'Mix (Premium plan only)')
    ])
    bottleSize = SelectField('Bottle Size', choices=[
        ('5 Liter', '5 Liter'),
        ('10 Liter', '10 Liter'),
        ('20 Liter', '20 Liter')
    ])
    deliveryFrequency = SelectField('Delivery Frequency', choices=[
        ('Weekly', 'Weekly'),
        ('Bi-weekly', 'Bi-weekly'),
        ('Monthly', 'Monthly')
    ])
    preferredDay = SelectField('Preferred Delivery Day', choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday')
    ])
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Street Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = SelectField('State', validators=[DataRequired()])
    zip = StringField('Zip Code', validators=[DataRequired()])
    deliveryInstructions = TextAreaField('Delivery Instructions')
    paymentMethod = SelectField('Payment Method', choices=[('creditCard', 'Credit Card'), ('paypal', 'PayPal')])
    termsAgree = BooleanField('I agree to the Terms and Conditions and Privacy Policy', validators=[DataRequired()])

@bp.route("/api/create-subscription", methods=['POST'])
@login_required
def create_subscription():
    try:
        data = request.json
        plan = SubscriptionPlan.query.get(data['planId'])
        
        if not plan:
            return jsonify({'success': False, 'error': 'Invalid plan'})

        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                payment_method=data['paymentMethodId'],
                invoice_settings={
                    'default_payment_method': data['paymentMethodId'],
                },
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()
        else:
            # Update payment method
            stripe.PaymentMethod.attach(
                data['paymentMethodId'],
                customer=current_user.stripe_customer_id,
            )

        # Create Stripe subscription
        stripe_subscription = stripe.Subscription.create(
            customer=current_user.stripe_customer_id,
            items=[{'price': plan.stripe_price_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )

        # Create local subscription record
        subscription = Subscription(
            user_id=current_user.id,
            plan_id=plan.id,
            start_date=datetime.utcnow(),
            next_billing_date=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(subscription)
        db.session.commit()

        return jsonify({
            'success': True,
            'subscription': stripe_subscription.id
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route("/subscription/success")
@login_required
def subscription_success():
    return render_template('subscription_success.html')

# Add this to your initialization script or create a new management command
def initialize_subscription_plans():
    plans = [
        {
            'name': 'Basic Hydration',
            'price': 29.00,
            'description': '4 x 5-gallon bottles monthly',
            'stripe_price_id': 'price_basic_xxxx',
            'is_active': True
        },
        {
            'name': 'Premium Hydration',
            'price': 49.00,
            'description': '8 x 5-gallon bottles monthly',
            'stripe_price_id': 'price_premium_xxxx',
            'is_active': True
        },
        {
            'name': 'Business Hydration',
            'price': 89.00,
            'description': '16 x 5-gallon bottles monthly',
            'stripe_price_id': 'price_business_xxxx',
            'is_active': True
        }
    ]

    for plan in plans:
        existing_plan = SubscriptionPlan.query.filter_by(name=plan['name']).first()
        if not existing_plan:
            new_plan = SubscriptionPlan(**plan)
            db.session.add(new_plan)
    
    db.session.commit()
    
@bp.route('/orders')
def orders():
    # If you have user authentication, you might want to check if the user is logged in
    # For example: if not current_user.is_authenticated: return redirect(url_for('main.login'))
    
    # Fetch orders from the database
    # This is a placeholder - replace with your actual database query
    orders = []  # In a real app, you would fetch this from your database
    
    # Example of what the orders data might look like:
    # orders = [
    #     {
    #         'id': 'ORD-12345',
    #         'date_created': datetime.datetime.now(),
    #         'items': ['Product 1', 'Product 2'],
    #         'total': 129.99,
    #         'status': 'Delivered',
    #         'status_color': 'success'  # Bootstrap color class
    #     }
    # ]
    
    return render_template('orders.html', orders=orders)

# You might also want to add a route for order details
@bp.route('/orders/<order_id>')
def order_details(order_id):
    # Fetch specific order details
    # order = Order.query.get_or_404(order_id)
    
    # For now, just redirect to orders page
    return redirect(url_for('main.orders'))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset requests."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real application, you would send an email with a reset token
            flash('Check your email for instructions to reset your password', 'info')
            return redirect(url_for('main.login'))
        else:
            flash('Email not found', 'danger')
    
    return render_template('reset_password_request.html', form=form)


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')