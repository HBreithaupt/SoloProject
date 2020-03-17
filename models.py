from config import db, bcrypt
from sqlalchemy.sql import func
from config import alerts
from flask import session
import re
from datetime import datetime

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
    logged_in = db.Column(db.Boolean, default=False)
    logeed_in_time = db.Column(db.DateTime, onupdate=func.now())
    orders = db.relationship('Order', back_populates='owner',lazy='dynamic')
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
    total_price = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='cascade'), nullable=False)
    status = db.Column(db.String(10))
    owner = db.relationship('User', foreign_keys=[user_id], back_populates='orders')
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def create_order(cls, user_id):
        order = Order(total_price=0, user_id=user_id, status='incomplete')
        db.session.add(order)
        db.session.commit()
        db.session.refresh(order)
        return order.id



    def serialize_history(self):
        result = []
        products = self.order_products
        result.append({'date_total': self.updated_at.strftime("%x") + ' - Total: $' + str(self.total_price)})
        for product in products:
            currProduct = {}
            currDescription = product.type.capitalize() + ": "

            if(product.type == 'pizza'):
                currDescription += Pizza.query.filter_by(product_id=product.id).first().serialize_history()
                currDescription += f" ${product.product_price}"

            currProduct['description'] = currDescription

            result.append(currProduct)


        return result



    def __repr__(self):
        return f"{self.id}"



class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))
    quantity = db.Column(db.Integer)
    product_price = db.Column(db.Float)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id", ondelete='cascade'), nullable=False)
    full_order = db.relationship('Order', foreign_keys=[order_id], backref="order_products")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def create_product(cls, type, order_id, product_price):
        product = Product(type=type, quantity=1, order_id=order_id, product_price=product_price)
        db.session.add(product)
        db.session.flush()
        return product.id

    def serialize(self):
        result = { 'price': self.product_price, 'quantity': self.quantity}
        if self.type == 'pizza':
            pizza = Pizza.query.filter_by(product_id=self.id).first()
            return pizza.serialize(result)


class Pizza(db.Model):
    __tablename__ = "pizzas"
    id = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String(15))
    size = db.Column(db.String(15))
    pizza_price = db.Column(db.Float)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete='cascade'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    toppings_on_this_pizza = db.relationship('Topping', secondary=pizza_toppings_table)

    @classmethod
    def create_pizza(self, data, product_id, pizza_price):
        new_pizza = Pizza(style=data['pizza_style'], size=data['pizza_size'], pizza_price=pizza_price, product_id=product_id)
        db.session.add(new_pizza)
        db.session.commit()
        db.session.expire(new_pizza)
        db.session.refresh(new_pizza)
        return new_pizza

    def __repr__(self):
        return f"{self.id, self.style, self.size, self.pizza_price}"

    def serialize(self, result):
        result['type'] = 'pizza'
        result['style'] = self.style
        result['size'] = self.size
        toppings = self.toppings_on_this_pizza
        toppings_str = ""
        for topping in toppings:
            toppings_str += topping.name + ", "

        toppings_str = toppings_str[:-2]
        result['toppings'] = toppings_str

        return result

    def serialize_history(self):
        result = ""
        result += self.size.capitalize() + ' ' + self.style.capitalize() + ' - '

        toppings = self.toppings_on_this_pizza
        toppings_str = ""
        for topping in toppings:
            toppings_str += topping.name.capitalize() + ', '

        toppings_str = toppings_str[:-2]
        result += toppings_str
        return result

class PizzaSizePrice(db.Model):
    __tablename__ = "pizza_size_price"
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(10))
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    __table_args__=(db.UniqueConstraint('size'),)

class Topping(db.Model):
    __tablename__ = "toppings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, unique=True)
    topping_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default = func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    pizzas_with_this_topping = db.relationship('Pizza', secondary=pizza_toppings_table)

    def __repr__(self):
        return f"id: {self.id}, name :{self.name}"
