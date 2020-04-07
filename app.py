from flask import render_template, redirect, session, request, flash
from config import app, db, bcrypt, alerts, scheduler, Config
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import json
import stripe

# import database classes
from models import User, Order, Product, Pizza, Topping, PizzaSizePrice

##### Stripe test ###################################
# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = 'sk_test_DiwZEGuAn4420iiVbgzrSafP00OrftivE3'

# session = stripe.checkout.Session.create(
#   payment_method_types=['card'],
#   line_items=[{
#     'name': 'T-shirt',
#     'description': 'Comfortable cotton t-shirt',
#     'images': ['https://example.com/t-shirt.png'],
#     'amount': 500,
#     'currency': 'usd',
#     'quantity': 1,
#   },{
#     'name': 'T-shirt',
#     'description': 'Comfortable cotton t-shirt',
#     'images': ['https://example.com/t-shirt.png'],
#     'amount': 500,
#     'currency': 'usd',
#     'quantity': 1,
#   }],
#   success_url='http://localhost:5000/success?session={CHECKOUT_SESSION_ID}',
#   cancel_url='https://localhost:5000/cancel',
# )

def fill_items(order):
    result = [];
    products = order.order_products

    for product in products:
        currItem = {
        'name': product.type.capitalize(),
        'description': f'Delicious {product.type}.',
        'amount': int(product.product_price * 100),
        'currency': 'usd',
        'quantity': product.quantity
        }
        result.append(currItem)

    return result

@app.route("/checkout/session/create")
def create_session():
    items = fill_items(Order.query.filter_by(id=session['currOrder_id']).first())

    stripe_session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items = items,
    success_url='http://localhost:5000/success',
    cancel_url='https://localhost:5000/cancel',
    )

    return json.dumps(stripe_session.id)


#########################################

#success page
@app.route("/success")
def success():
    #update current order to complete
    fulfilled_order = Order.query.filter_by(id=session['currOrder_id']).first()
    fulfilled_order.status = 'complete'
    db.session.commit()

    # create a new order for this user
    new_order_id = Order.create_order(session['user_id'])

    session['currOrder_id'] = new_order_id

    alerts.append("Thank you for ordering with us!")
    return redirect("/dashboard")



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

# process login
@app.route("/login/process", methods=["POST"])
def process_login():
    result = User.attempt_login(request.form)
    user_id = User.query.filter_by(email=request.form['login_email']).first().id
    session['user_id'] = user_id

    # check for if an order already exists, else create a
    order = db.session.query(User).filter_by(id=user_id).first().orders.filter_by(status='incomplete').first()
    if order:
        print(f"found an order, id: {order.id}")
        session['currOrder_id'] = order.id
    else:
        new_order = Order(total_price=0, user_id=user_id,status='incomplete')
        db.session.add(new_order)
        db.session.commit()
        session['currOrder_id'] =   db.session.query(User).filter_by(id=user_id).first().orders.filter_by(status='incomplete').first().id

    if result:
        print(session['user_id'])
        user = User.query.filter_by(id=user_id).first()
        user.logged_in = True
        db.session.commit()
        return redirect("/dashboard")

    return redirect("/login")

# logout
@app.route("/logout")
def logout():
    user = User.query.filter_by(id=session['user_id']).first()
    user.logged_in = False
    db.session.commit()
    session.clear()
    return redirect("/")

#main page after logging in
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


# order a pizza page
@app.route("/order/pizza")
def order_pizza():
    small_price = PizzaSizePrice.query.filter_by(size='small').first().price
    medium_price = PizzaSizePrice.query.filter_by(size='medium').first().price
    large_price = PizzaSizePrice.query.filter_by(size='large').first().price
    return render_template("pizza_order.html", small_price=small_price,medium_price=medium_price,large_price=large_price)

# process ordering a pizza
@app.route("/order/pizza/process", methods=["POST"])
def process_order_pizza():

    toppings = [val for key, val in request.form.items() if 'add_' in key]

    #calculate pizze price
    pizza_price = PizzaSizePrice.query.filter_by(size=request.form['pizza_size']).first().price

    #now add price of toppings (all toppings are 0.5c for now)
    toppings_price = 0.5 * len(toppings)

    #create a new product and get the id
    new_product_id = Product.create_product(type='pizza', order_id=session['currOrder_id'], product_price=pizza_price + toppings_price)

    #create a new pizza and get the object back to add toppings
    new_pizza_obj = Pizza.create_pizza(request.form, new_product_id, pizza_price)


    for item in toppings:
        currTopping = Topping.query.filter_by(name=item).first()
        new_pizza_obj.toppings_on_this_pizza.append(currTopping)
        db.session.commit()

    return redirect(f"/checkout/{session['currOrder_id']}")

# retrieve user's address
@app.route("/user/address/retrieve")
def retrieve_address():
    user = User.query.filter_by(id=session['user_id']).first();
    address = {'street': user.address, 'city': user.city, 'state': user.state}

    return address

#check out route
@app.route("/checkout/<order_id>")
def checkout(order_id):
    currOrder = Order.query.filter_by(id=session['currOrder_id']).first()
    products = currOrder.order_products
    total_price = 0
    for product in products:
        total_price += product.product_price

    currOrder.total_price = total_price
    db.session.commit()

    return render_template("checkout.html", order_id=order_id)

@app.route("/order/history")
def order_history():
    all_orders = Order.query.filter_by(user_id=session['user_id'],status='complete').all()
    return json.dumps(all_orders, default=Order.serialize_history)

@app.route("/order/products/num/retrieve")
def retrieve_num_items():
    order = Order.query.filter_by(id=session['currOrder_id']).first()
    products = order.order_products
    return json.dumps(len(products))

# retrieve alerts
@app.route('/alerts/retrieve')
def retrieve_alerts():
    result = json.dumps(alerts)
    alerts.clear()
    return result

# retrieve the products from our ourder, for ajax
@app.route("/order/<order_id>/serialize")
def retrieve_order(order_id):
    order = Order.query.filter_by(id=order_id).first()
    products = order.order_products
    result = json.dumps(products, default=Product.serialize)
    result = result[:-1]
    result += f',{{"total_price": {order.total_price}}}]'
    return result

# functions to create test data
def create_toppings():
    toppings = [
    Topping(name='ham', topping_price=0.5),
    Topping(name='beef', topping_price=0.5),
    Topping(name='salami', topping_price=0.5),
    Topping(name='pepperoni', topping_price=0.5),
    Topping(name='sausage', topping_price=0.5),
    Topping(name='chicken', topping_price=0.5),
    Topping(name='bacon', topping_price=0.5),
    Topping(name='steak', topping_price=0.5),
    Topping(name="jalapeno", topping_price=0.5),
    Topping(name="onions", topping_price=0.5),
    Topping(name="black olives", topping_price=0.5),
    Topping(name="mushroom", topping_price=0.5),
    Topping(name="pineapple", topping_price=0.5),
    Topping(name="green peppers", topping_price=0.5),
    Topping(name="spinach", topping_price=0.5)
    ]


    try:
        db.session.bulk_save_objects(toppings)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("Toppings alreay exist, doing nothing.")

def create_test_user():
    user = User(first_name='Haven', last_name='Breithaupt', email='havenbreithaupt@gmail.com',address='4814 66th St Ct E',city='Tacoma',state='WA', password=bcrypt.generate_password_hash('bloody75'))

    try:
        db.session.add(user)
        db.session.commit()
    except (IntegrityError,InvalidRequestError) as e:
        db.session.rollback()
        print("User already exists, doing nothing.")

def create_pizze_prices():
    prices = [
    PizzaSizePrice(size='small', price=4.99),
    PizzaSizePrice(size='medium', price=6.99),
    PizzaSizePrice(size='large', price=8.99)
    ]

    try:
        db.session.bulk_save_objects(prices)
        db.session.commit()
    except IntegrityError:
        print("Prices already set, doing nothing.")
# scheduler tasks
def remove_incomplete_orders():
    orders_to_remove = Order.query.filter_by(status='incomplete').all()
    for order in orders_to_remove:
        if(order.owner.logged_in == False):
            print(f"Deleting order {order.id}")
            db.session.delete(order)

    db.session.commit()

if __name__ == "__main__":
    app.config.from_object(Config())
    app.apscheduler.add_job(id='test',func=remove_incomplete_orders, trigger='interval',seconds=3)
    #scheduler.start()
    create_test_user()
    create_toppings()
    create_pizze_prices()
    app.run(debug=True)
