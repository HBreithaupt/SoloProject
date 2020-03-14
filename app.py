from flask import render_template, redirect, session, request, flash
from config import app, db, bcrypt, alerts
import json

# import database classes
from models import User



# home-page
@app.route("/")
def index():

    if 'user_id' in session.keys():
        return redirect("/dashboard")

    return render_template("index.html")

# add a user
@app.route("/users/add", methods=["POST"])
def add_user():

    isValid = True
    # check email format
    if not User.verify_email(request.form['input_email']):
        isValid = False
        alerts.append("Invalid email.")


    if User.query.filter_by(email=request.form['input_email']).all():
        isValid = False
        alerts.append("There is an account already registered with that email.")

    #check password
    if not request.form['input_password'] == request.form['input_confirm_password']:
        isValid = False
        alerts.append("Passwords don't match.")


    # add user
    if isValid:
        alerts.append("Account successfully created.")
        User.add_user(request.form)

    return redirect("/")

# login page
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login/process", methods=["POST"])
def process_login():
    result = User.attempt_login(request.form)

    if result:
        return redirect("/dashboard")

    return redirect("/login")

# logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session.keys():
        alerts.append("Not allowed")
        return redirect("/")

    return render_template("dashboard.html")


# account page
@app.route("/user/<user_id>/account")
def account(user_id):
    return render_template("account.html")

# update Account
@app.route("/user/<user_id>/account/update", methods=["POST"])
def account_update(user_id):
    User.update_user(request.form, user_id)
    return redirect("/user/<user_id>/account")



# retrieve alerts
@app.route('/alerts/retrieve')
def retrieve_alerts():
    result = json.dumps(alerts)
    alerts.clear()
    return result

if __name__ == "__main__":
    app.run(debug=True)
