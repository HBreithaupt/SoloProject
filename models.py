from config import db, bcrypt
from sqlalchemy.sql import func
from config import alerts
from flask import session
import re

pizza_toppings_table = db.Table('pizza_toppings',
db.Column('pizza_id', db.Integer, db.ForeignKey('pizzas.id', ondelete='cascade'), primary_key=True),
db.Column('topping_id', db.Integer, db.ForeignKey('toppings.id', ondelete='cascade'), primary_key=True))

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(20))
    address = db.Column(db.String(50))
    city = db.Column(db.String(20))
    state = db.Column(db.String(2))
    password = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__=(db.UniqueConstraint('email'),)


    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

    @classmethod
    def verify_email(cls, email):
        if not User.EMAIL_REGEX.match(email):
            return False

        return True

    @classmethod
    def add_user(cls, data):
        pw_hash = bcrypt.generate_password_hash(data['input_password'])

        new_user = User(first_name=data['input_fname'], last_name=data['input_lname'], email=data['input_email'],address=data['input_address'],city=data['input_address'],state=data['input_state'],password=pw_hash)

        db.session.add(new_user)
        db.session.commit()

        return

    @classmethod
    def attempt_login(cls, data):
        user_attempt = User.query.filter_by(email=data['login_email']).first()

        # check for account existence and validity of data
        if not user_attempt:
            alerts.append("No account found with that email.")
            return False
        elif not bcrypt.check_password_hash(user_attempt.password, data['login_password']):
            alerts.append("Incorrect username/password combination.")
            return False

        # valid login here
        session['user_id'] = user_attempt.id
        session['user_name'] = user_attempt.first_name
        return True

    @classmethod
    def update_user(cls, data, user_id):
        user_to_update = User.query.get(user_id)

        if data['update_fname']:
            user_to_update.first_name = data['update_fname']

        if data['update_lname']:
            user_to_update.last_name = data['update_lname']

        if data['update_email']:
            user_to_update.email = data['update_email']

        if data['update_city']:
            user_to_update.city = data['update_city']

        if data['update_address']:
            user_to_update.address = data['update_address']

        if data['update_state']:
            user_to_update.state = data['update_state']

        db.session.commit()
        alerts.append("Account updated.")
        return
class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref="user_orders")


class Pizza(db.Model):
    __tablename__ = "pizzas"
    id = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String(15))
    size = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    #order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete="cascade"), nullable=False)
    # order = db.relationship('Order', foreign_keys=[order_id], backref="pizza_order")
    toppings_on_this_pizza = db.relationship('Topping', secondary=pizza_toppings_table)


class Topping(db.Model):
    __tablename__ = "toppings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default = func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    #pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id", ondelete="cascade"), nullable=False)
    # order = db.relationship('Pizza', foreign_keys=[pizza_id], backref="pizza_toppings")
    pizzas_with_this_topping = db.relationship('Pizza', secondary=pizza_toppings_table)
