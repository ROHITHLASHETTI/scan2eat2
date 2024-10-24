from flask import Flask, render_template, request, redirect, url_for
import qrcode
import io
import base64
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    restaurant = db.Column(db.String(100), nullable=False)
    menu_item = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)

# Ensure that the database tables are created within the application context
with app.app_context():
    db.create_all()

# Predefined menu items
menu_items = [
    {"name": "Biryani", "price": 10.0},
    {"name": "Pizza", "price": 8.0},
    {"name": "Roasted Chicken", "price": 5.0},
    {"name": "Pasta", "price": 7.0},
    {"name": "Samosa", "price": 4.0}
]

# Predefined restaurants
restaurants = [
    "Paradise Biryani",
    "Bawarchi",
    "Shah Ghouse Café & Restaurant",
    "Chutneys",
    "Hotel Shadab",
    "Ohri's",
    "Jewel of Nizam – The Minar",
    "The Spicy Venue",
    "Cafe Bahar",
    "Kritunga Restaurant"
]

@app.route('/')
def index():
    return render_template('index.html', menu_items=menu_items, restaurants=restaurants)

@app.route('/order', methods=['POST'])
def order():
    name = request.form['name']
    address = request.form['address']
    restaurant = request.form['restaurant']
    menu_item = request.form['menu_item']
    quantity = int(request.form['quantity'])
    price = float(request.form['price'])
    payment_type = request.form['payment_type']

    new_order = Order(name=name, address=address, restaurant=restaurant, menu_item=menu_item, quantity=quantity, price=price, payment_type=payment_type)
    db.session.add(new_order)
    db.session.commit()

    invoice = f"Name: {name}\nAddress: {address}\nRestaurant: {restaurant}\nMenu Item: {menu_item}\nQuantity: {quantity}\nPrice: {price}\nPayment Type: {payment_type}\nTotal: {quantity * price}"

    img = qrcode.make(invoice)
    buf = io.BytesIO()
    img.save(buf)
    img_str = base64.b64encode(buf.getvalue()).decode("utf-8")

    return render_template('order_summary.html', order=new_order, img_str=img_str)

@app.route('/report')
def report():
    # Query the database to count the number of items sold for each restaurant
    sold_items = db.session.query(
        Order.restaurant,
        db.func.sum(Order.quantity).label('total_quantity')
    ).group_by(Order.restaurant).all()

    return render_template('report.html', sold_items=sold_items)

if __name__ == '__main__':
    app.run(debug=True)
