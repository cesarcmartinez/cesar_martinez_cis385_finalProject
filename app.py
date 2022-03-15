import os
import random
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, session, render_template
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Load environment variables
load_dotenv()

# Initialize flask app
app = Flask(__name__)
app.secret_key = "sEcReTkEy"
app.static_folder = 'static'
api = Api(app)

basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['POSTGRES_DB_CONNECTION_STRING']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

cart = []

class Users(db.Model):
    __tablename__ = 'users'
    userId = db.Column(db.Integer, primary_key=True)
    emailAddress = db.Column(db.Text)
    password = db.Column(db.Text)
    
    def __repr__(self):
        return '<Users %r>' % self.userId

class MenuItems(db.Model):
    __tablename__ = 'menuItems'
    menuItemId = db.Column(db.Integer, primary_key=True)
    itemType = db.Column(db.Text)
    itemName = db.Column(db.Text)
    basePriceCost = db.Column(db.Numeric)
    allowExtras = db.Column(db.Text)

    def __repr__(self):
        return '<MenuItems %r>' % self.itemName

class ExtraItems(db.Model):
    __tablename__ = 'extraItems'
    extraId = db.Column(db.Integer, primary_key=True)
    extraName = db.Column(db.Text)
    extraPrice = db.Column(db.Numeric)

    def __repr__(self):
        return '<ExtraItems %r>' % self.extraId

class Customers(db.Model):
    __tablename__ = 'customers'
    customerId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    phoneNumber = db.Column(db.Text) 

    def __repr__(self):
        return '<Customers %r>' % self.customerId

class Orders(db.Model):
    __tablename__ = 'orders'
    orderId = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Text)
    time = db.Column(db.Text)
    customerId = db.Column(db.Integer)
    customerName = db.Column(db.Text)
    customerPhone = db.Column(db.Text)

    def __repr__(self):
        return '<Orders %r>' % self.OrderId

class OrderItems(db.Model):
    __tablename__ = 'OrderItems'
    orderItemId = db.Column(db.Integer, primary_key=True)
    orderId = db.Column(db.Integer)
    menuItemId = db.Column(db.Integer)
    extraId = db.Column(db.Integer)

    def __repr__(self):
        return '<OrderItems %r>' % self.orderItemId

@app.route('/')
def hello():
    return render_template('index.html')
    
@app.route('/menu', methods=['GET'])
def menuReview():
    review1 = []
    review2 = ['None']
    review = MenuItems.query.all()
    for item in review:
        review1.append(item.itemName)
    extraReview = ExtraItems.query.all()
    for extra in extraReview:
        review2.append(extra.extraName)
    return render_template('menu.html', review1=review1, review2=review2)

@app.route('/reviewOrder', methods=['POST'])
def submit():
    total = 0
    currentOrder = [request.form.get("main_item"), request.form.get("extra_item")]
    cart.extend(currentOrder)
    for i in cart:
        j = MenuItems.query.filter_by(itemName=i).first()
        if j is not None:
            cost = float(j.basePriceCost)
            total = total + cost
        k = ExtraItems.query.filter_by(extraName=i).first()
        if k is not None:
            extra_cost = float(k.extraPrice)
            total = total + extra_cost
    session['total_form'] = "${:,.2f}".format(total)
    return render_template('checkout.html', cart=cart, total=session['total_form'])

@app.route('/userInfo', methods=['GET'])
def show_user_info():
    return render_template('details.html', total=session['total_form'])

@app.route('/confirmation', methods=['POST'])
def store_data():
    id = random.randint(10, 200)
    name = request.form.get("name")
    phone_num = request.form.get("phoneNumber")
    email_address = request.form.get("emailAddress")
    password = request.form.get("password")
    # add to tbl.customers
    newCustomer = Customers(customerId=id, name=name, phoneNumber=phone_num)
    db.session.add(newCustomer)
    db.session.commit()
    # add to tbl.users
    newUser = Users(userId=id, emailAddress=email_address, password=password)
    db.session.add(newUser)
    db.session.commit()
    # add to Order Table
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y")
    tm_string = now.strftime("%H:%M:%S")
    order_id = random.randint(10, 200)
    newOrder = Orders(orderId=order_id, date=dt_string, time=tm_string, customerId=id,
                      customerName=(name), customerPhone=phone_num)
    db.session.add(newOrder)
    db.session.commit()
    # add to tbl.orderItems
    extra_id = None
    menu_id = None
    for item in cart:
        t = MenuItems.query.filter_by(itemName=item).first()
        if t is not None:
            menu_id = t.menuItemId
        r = ExtraItems.query.filter_by(extraName=item).first()
        if r is not None:
            extra_id = r.extraId
        if menu_id is not None and extra_id is not None:
            new_orderItem = OrderItems(orderItemId=random.randint(
                10, 200), orderId=order_id, menuItemId=menu_id, extraId=extra_id)
            db.session.add(new_orderItem)
            db.session.commit()
            extra_id = None
            menu_id = None
    return render_template('confirmation.html', order_id=order_id)

if __name__ == '__main__':
    app.run(debug=True)
