from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)


class CartProduct(Base):
    __tablename__ = 'cart_products'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)


class ProductIn(BaseModel):
    name: str
    price: int


class CartProductIn(BaseModel):
    product_id: int
    quantity: int


app = FastAPI()

engine = create_engine('postgresql://user:password@localhost/dbname')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@app.post('/product')
def create_product(product: ProductIn):
    session = Session()
    new_product = Product(name=product.name, price=product.price)
    session.add(new_product)
    session.commit()
    session.close()
    return {'message': 'Product created'}


@app.get('/products')
def get_products(skip: int = 0, limit: int = 100, sort: str = 'asc', name: str = None):
    session = Session()
    products = session.query(Product).offset(skip).limit(limit)
    if name:
        products = products.filter(Product.name.like(f"%{name}%"))
    if sort == 'asc':
        products = products.order_by(Product.name)
    else:
        products = products.order_by(Product.name.desc())
    return products


@app.post('/cart')
def add_to_cart(cart_product: CartProductIn):
    session = Session()
    new_cart_product = CartProduct(product_id=cart_product.product_id,
                                   quantity=cart_product.quantity)
    session.add(new_cart_product)
    session.commit()
    session.close()
    return {'message': 'Product added to cart'}
