import time
import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .config import BASE_URL, get_driver


def test_login_success():
    driver = get_driver()
    driver.get(f"{BASE_URL}/login.html")

    try:
        # Giriş bilgileri
        email = "test@example.com"
        password = "123456"

        # Giriş alanları
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()

        # Sayfanın yüklenmesini bekle
        time.sleep(2)

        # Giriş sonrası ana sayfaya yönlenme kontrolü
        assert "index.html" in driver.current_url or "Ürünler" in driver.page_source

    except NoSuchElementException as e:
        pytest.fail(f"Sayfada beklenen bir element bulunamadı: {e}")

    finally:
        driver.quit()


  #  cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
    #   pytest sel/test_login.py -v