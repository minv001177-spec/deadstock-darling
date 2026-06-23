import unittest
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestUI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Настройки для headless-режима (без GUI)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except:
            # Если Chrome недоступен, пробуем Firefox
            try:
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--headless")
                cls.driver = webdriver.Firefox(options=firefox_options)
            except:
                cls.driver = None
                print("⚠️ Selenium WebDriver не доступен, UI-тесты пропущены")
    
    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
    
    def test_homepage_load(self):
        if not self.driver:
            self.skipTest("WebDriver не доступен")
        
        self.driver.get("http://localhost:5000/")
        time.sleep(1)
        self.assertIn("Deadstock Darling", self.driver.title)
    
    def test_products_visible(self):
        if not self.driver:
            self.skipTest("WebDriver не доступен")
        
        self.driver.get("http://localhost:5000/")
        time.sleep(1)
        products = self.driver.find_elements(By.CLASS_NAME, "product-item")
        self.assertGreater(len(products), 0)
    
    def test_login_page(self):
        if not self.driver:
            self.skipTest("WebDriver не доступен")
        
        self.driver.get("http://localhost:5000/login")
        time.sleep(1)
        email_input = self.driver.find_element(By.NAME, "email")
        password_input = self.driver.find_element(By.NAME, "password")
        self.assertIsNotNone(email_input)
        self.assertIsNotNone(password_input)

if __name__ == '__main__':
    unittest.main()