import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User, Product

class TestModels(unittest.TestCase):
    
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
    
    def test_user_creation(self):
        with app.app_context():
            user = User(username="testuser", email="test@test.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            retrieved = User.query.filter_by(email="test@test.com").first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.username, "testuser")
            self.assertTrue(retrieved.check_password("password123"))
    
    def test_product_creation(self):
        with app.app_context():
            product = Product(
                name="Test Product",
                price=100,
                category="clothing"
            )
            db.session.add(product)
            db.session.commit()
            
            retrieved = Product.query.first()
            self.assertEqual(retrieved.name, "Test Product")
            self.assertEqual(retrieved.price, 100)
    
    def test_product_to_dict(self):
        with app.app_context():
            product = Product(
                id=1,
                name="Test Product",
                price=100,
                category="clothing"
            )
            product_dict = product.to_dict()
            self.assertEqual(product_dict['id'], 1)
            self.assertEqual(product_dict['name'], "Test Product")
            self.assertEqual(product_dict['price'], 100)

if __name__ == '__main__':
    unittest.main()