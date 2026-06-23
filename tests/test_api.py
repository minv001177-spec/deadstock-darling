import unittest
import requests
import json

class TestAPI(unittest.TestCase):
    
    BASE_URL = "http://localhost:5000"
    
    def setUp(self):
        # Проверка доступности сервера
        try:
            requests.get(f"{self.BASE_URL}/api/products", timeout=2)
        except requests.exceptions.ConnectionError:
            self.skipTest("Сервер не запущен")
    
    def test_get_products(self):
        response = requests.get(f"{self.BASE_URL}/api/products")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn('id', data[0])
            self.assertIn('name', data[0])
            self.assertIn('price', data[0])
    
    def test_get_product_by_id(self):
        response = requests.get(f"{self.BASE_URL}/api/products/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], 1)
        self.assertIn('name', data)
    
    def test_get_product_not_found(self):
        response = requests.get(f"{self.BASE_URL}/api/products/9999")
        self.assertEqual(response.status_code, 404)
    
    def test_cart_count(self):
        # Проверяем, что API корзины работает (может требовать авторизации)
        response = requests.get(f"{self.BASE_URL}/api/cart/count")
        # Может вернуть 302 (редирект на логин) или 200
        self.assertIn(response.status_code, [200, 302])

if __name__ == '__main__':
    unittest.main()