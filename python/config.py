from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "I solemnly swear that I am up to no good"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pizza_time.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
