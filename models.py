from config import db
from sqlalchemy.sql import func
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
