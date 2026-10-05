import hmac
import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise RuntimeError('Set DATABASE_URL in the process environment')
API_TOKEN = os.environ.get('API_TOKEN', '')
if len(API_TOKEN) < 32:
    raise RuntimeError('Set a random API_TOKEN of at least 32 characters')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Создание таблиц в базе данных.
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),
                           nullable=False)
    product = db.relationship('Product', backref=db.backref('carts', lazy=True))
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Cart {self.product.name}>'


@app.cli.command('init-db')
def init_db():
    """Initialize tables explicitly, never as an import side effect."""
    db.create_all()


@app.before_request
def require_api_token():
    scheme, _, token = request.headers.get('Authorization', '').partition(' ')
    if scheme.lower() != 'bearer' or not hmac.compare_digest(token.encode('utf-8'), API_TOKEN.encode('utf-8')):
        response = jsonify({'error': 'Authentication required'})
        response.status_code = 401
        response.headers['WWW-Authenticate'] = 'Bearer'
        return response


# Работа с товарами в магазине.
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    product = Product(name=data['name'], price=data['price'])
    db.session.add(product)
    db.session.commit()
    return jsonify({'id': product.id}), 201


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify({'id': product.id, 'name': product.name, 'price': product.price}), 200


@app.route('/products', methods=['GET'])
def get_products():
    sort_by = request.args.get('sort_by', 'name')
    search_query = request.args.get('search_query')
    order = request.args.get('order', 'asc')
    products = Product.query
    if search_query:
        products = products.filter(Product.name.ilike('%' + search_query + '%'))
    column = Product.price if sort_by == 'price' else Product.name
    products = products.order_by(column.desc() if order == 'desc' else column.asc())
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} for p in products.all()]), 200


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    name = data.get('name')
    price = data.get('price')
    if name:
        product.name = name
    if price:
        product.price = price
    db.session.commit()
    return jsonify({'id': product.id, 'name': product.name, 'price': product.price}), 200


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200


# Работа с товарами в корзине.
@app.route('/carts', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product = Product.query.get(data['product_id'])
    cart = Cart(product=product, quantity=data['quantity'])
    db.session.add(cart)
    db.session.commit()
    return jsonify({'id': cart.id}), 200


@app.route('/carts/<int:cart_id>', methods=['PUT'])
def update_cart_item(cart_id):
    data = request.get_json()
    cart = Cart.query.get(cart_id)
    cart.quantity = data['quantity']
    db.session.commit()
    return jsonify({'id': cart.id, 'quatity': cart.quantity}), 200


@app.route('/carts/<int:cart_id>', methods=['DELETE'])
def delete_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    db.session.delete(cart)
    db.session.commit()
    return jsonify({'message': 'Cart has been deleted'}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False)

