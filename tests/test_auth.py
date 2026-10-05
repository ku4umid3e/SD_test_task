import os
import unittest

# This token is only for an isolated in-memory test application.
os.environ['API_TOKEN'] = 'test-only-token-never-used-in-production-0123456789'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
from main import app, db, Product, Cart


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.auth = {'Authorization': 'Bearer ' + os.environ['API_TOKEN']}
        with app.app_context():
            db.create_all()
            db.session.add(Product(id=1, name='phone', price=100))
            db.session.add(Cart(id=1, product_id=1, quantity=1))
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def test_all_routes_reject_unauthenticated_requests_without_mutation(self):
        requests = [('GET', '/products', None), ('GET', '/products/1', None),
                    ('POST', '/products', {'name': 'extra', 'price': 5}),
                    ('PUT', '/products/1', {'name': 'changed'}),
                    ('DELETE', '/products/1', None),
                    ('POST', '/carts', {'product_id': 1, 'quantity': 2}),
                    ('PUT', '/carts/1', {'quantity': 9}), ('DELETE', '/carts/1', None)]
        for headers in ({}, {'Authorization': 'Bearer wrong'}, {'Authorization': 'Bearer непроверенный'}):
            for method, url, body in requests:
                with self.subTest(method=method, url=url, headers=headers):
                    self.assertEqual(self.client.open(url, method=method, json=body, headers=headers).status_code, 401)
        with app.app_context():
            self.assertEqual(Product.query.count(), 1)
            self.assertEqual(db.session.get(Product, 1).name, 'phone')
            self.assertEqual(db.session.get(Cart, 1).quantity, 1)

    def test_authenticated_client_can_read_and_modify(self):
        self.assertEqual(self.client.get('/products?order=desc', headers=self.auth).status_code, 200)
        response = self.client.post('/products', json={'name': 'new', 'price': 20}, headers=self.auth)
        self.assertEqual(response.status_code, 201)
        product_id = response.json['id']
        self.assertEqual(self.client.put(f'/products/{product_id}', json={'price': 25}, headers=self.auth).status_code, 200)
        self.assertEqual(self.client.get(f'/products/{product_id}', headers=self.auth).json['price'], 25)
        self.assertEqual(self.client.delete(f'/products/{product_id}', headers=self.auth).status_code, 200)

    def test_query_parameter_is_not_a_credential(self):
        self.assertEqual(self.client.get('/products?token=' + os.environ['API_TOKEN']).status_code, 401)


if __name__ == '__main__':
    unittest.main()
