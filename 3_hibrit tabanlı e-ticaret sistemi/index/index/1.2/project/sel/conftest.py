import pytest
from selenium.webdriver.common.by import By
from sel.config import BASE_URL, get_driver
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="function")
def login_driver_customer():
    driver = get_driver()
    driver.get(f"{BASE_URL}/login.html")
    driver.find_element(By.ID, "email").send_keys("customer@test.com")
    driver.find_element(By.ID, "password").send_keys("123456")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def login_driver_supplier():
    driver = get_driver()
    driver.get(f"{BASE_URL}/login.html")
    driver.find_element(By.ID, "email").send_keys("supplier@test.com")
    driver.find_element(By.ID, "password").send_keys("123456")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    yield driver
    driver.quit()


