from flask import render_template, redirect, session
from config import app,db

@app.route("/")
def index():
    return render_template("index.html")










app.run(debug=True)
