from flask import render_template, redirect, session
from config import app,db

# import database classes
from db_classes.users import User

@app.route("/")
def index():
    return render_template("index.html")









if __name__ == "__main__":
    app.run(debug=True)
