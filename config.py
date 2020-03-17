from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_apscheduler.auth import HTTPBasicAuth

app = Flask(__name__)
app.secret_key = "I solemnly swear that I am up to no good"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pizza_time.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
scheduler = APScheduler()
scheduler.init_app(app)
alerts =[]


class Config(object):
    SCHEDULER_API_ENABLED = True
    SCHEDULER_AUTH = HTTPBasicAuth()
