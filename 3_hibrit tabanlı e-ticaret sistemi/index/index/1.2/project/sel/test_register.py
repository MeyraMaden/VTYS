import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from .config import BASE_URL, get_driver

def test_register_new_user():
    driver = get_driver()
    driver.implicitly_wait(3)  # Global 3 saniye bekleme
    driver.get(f"{BASE_URL}/register.html")

    try:
        random_email = f"selenium{random.randint(1000,9999)}@test.com"
        password = "123456"

        driver.find_element(By.ID, "email").send_keys(random_email)
        time.sleep(1)

        driver.find_element(By.ID, "password").send_keys(password)
        time.sleep(1)

        select = Select(driver.find_element(By.ID, "role"))
        select.select_by_value("customer")
        time.sleep(1)

        driver.find_element(By.ID, "register-button").click()

        # login.html sayfasına yönlendirilene kadar bekle
        WebDriverWait(driver, 10).until(EC.url_contains("login.html"))
        assert "login.html" in driver.current_url

    except NoSuchElementException as e:
        assert False, f"Element bulunamadı: {e}"
    finally:
        time.sleep(1)
        driver.quit()

def test_register_existing_email_shows_error():
    driver = get_driver()
    driver.implicitly_wait(3)  # Global 3 saniye bekleme
    driver.get(f"{BASE_URL}/register.html")

    try:
        existing_email = "test@example.com"
        password = "123456"

        driver.find_element(By.ID, "email").send_keys(existing_email)
        time.sleep(1)

        driver.find_element(By.ID, "password").send_keys(password)
        time.sleep(1)

        select = Select(driver.find_element(By.ID, "role"))
        select.select_by_value("customer")
        time.sleep(1)

        driver.find_element(By.ID, "register-button").click()

        # Hata mesajının görünmesini bekle
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.ID, "error-msg").is_displayed()
        )
        error_msg = driver.find_element(By.ID, "error-msg").text.lower()
        assert "kayıt" in error_msg or "zaten" in error_msg

    except NoSuchElementException as e:
        assert False, f"Element bulunamadı: {e}"
    finally:
        time.sleep(1)
        driver.quit()

def test_login_link_from_register_page():
    driver = get_driver()
    driver.implicitly_wait(5)  # Global 5 saniye bekleme
    driver.get(f"{BASE_URL}/register.html")

    try:
        login_link = driver.find_element(By.LINK_TEXT, "Giriş Yap")
        login_link.click()

        WebDriverWait(driver, 10).until(EC.url_contains("login.html"))
        assert "login.html" in driver.current_url

    except NoSuchElementException as e:
        assert False, f"Giriş Yap bağlantısı bulunamadı: {e}"
    finally:
        time.sleep(2)
        driver.quit()


  #  cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
    #   pytest sel/test_register.py -v