from config import db, bcrypt
from sqlalchemy.sql import func
from config import alerts
from flask import session
import re


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
        return True
