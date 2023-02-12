from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user_postgres:postgres_password@0.0.0.0/db_store'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#db.init_app(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Product %r>' % self.name


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),
                           nullable=False)
    product = db.relationship('Product', backref=db.backref('carts', lazy=True))
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Cart %r>' % self.product.name

with app.app_context():
    db.create_all()


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_list.append(
            {'id': product.id, 'name': product.name, 'price': product.price})
    return jsonify({'products': product_list})


@app.route('/products', methods=['POST'])
def create_product():
    product = Product(name=request.json['name'], price=request.json['price'])
    db.session.add(product)
    db.session.commit()
    return jsonify({'product': {'id': product.id, 'name': product.name,
                                'price': product.price}})


@app.route('/carts', methods=['POST'])
def add_to_cart():
    cart = Cart(product_id=request.json['product_id'],
                quantity=request.json['quantity'])
    db.session.add(cart)
    db.session.commit()
    return jsonify({'cart': {'id': cart.id, 'product_id': cart.product_id,
                             'quantity': cart.quantity}})


@app.route('/carts/<int:cart_id>', methods=['PUT'])
def update_cart(cart_id):
    cart = Cart.query.get(cart_id)
    cart.quantity = request.json['quantity']
    db.session.commit()
    return jsonify({'cart': {'id': cart.id, 'product_id': cart.product_id,
                             'quantity': cart.quantity}})

if __name__ == '__main__':
    app.run(debug=True) 

