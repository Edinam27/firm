# utils.py
from flask_mail import Message
from app import mail
from flask import render_template
import uuid
from datetime import datetime

def send_order_confirmation(order):
    msg = Message(
        f'Order Confirmation #{order.order_number}',
        sender='noreply@pureflow.com',
        recipients=[order.user.email]
    )
    msg.html = render_template('email/order_confirmation.html', order=order)
    mail.send(msg)

def generate_order_number():
    return f'ORD-{datetime.utcnow().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}'