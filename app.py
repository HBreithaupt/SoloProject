from flask import render_template, redirect, session, request
from config import app, db, bcrypt

# import database classes
from models import User


# home-page
@app.route("/")
def index():
    return render_template("index.html")

# add a user
@app.route("/users/add", methods=["POST"])
def add_user():
    # check email format
    if not User.verify_email(request.form['input_email']):
        flash("Invalid email.")

    #check password
    pw_hash = bcrypt.generate_password_hash(request.form['input_password'])
    if not request.form['input_password'] == request.form['input_confirm_password']:
        flash("Passwords don't match.")


    data = request.form
    print(data['input_state'])
    # every other field must be filled to get to this point so add a user
    if not '_flashes' in session.keys():
        new_user = User(first_name=data['input_fname'], last_name=data['input_lname'], email=data['input_email'],address=data['input_address'],city=data['input_address'],state=data['input_state'],password=pw_hash)

        db.session.add(new_user)
        db.session.commit()

    return redirect("/")

# login page
@app.route("/login")
def login():
    return render_template("login.html")




if __name__ == "__main__":
    app.run(debug=True)
