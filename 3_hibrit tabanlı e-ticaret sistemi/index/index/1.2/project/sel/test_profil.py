import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from sel.config import BASE_URL, get_driver


@pytest.fixture(scope="function")
def driver():
    drv = get_driver()
    yield drv
    drv.quit()


@pytest.fixture(scope="function")
def login_and_go_to_profile(driver):
    driver.get(f"{BASE_URL}/login.html")
    driver.find_element(By.ID, "email").send_keys("supplier@test.com")
    driver.find_element(By.ID, "password").send_keys("123456")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 20).until(EC.url_contains("index.html"))
    time.sleep(2)  # Ana sayfa yüklenince biraz bekle

    driver.get(f"{BASE_URL}/profile.html")
    time.sleep(2)  # Profil sayfası yüklenince bekle
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "email-display")))

    return driver


def highlight_element(driver, element, duration=2):
    """Test esnasında elementi kırmızı çerçeve ile vurgular."""
    original_style = element.get_attribute('style')
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                          element, "border: 3px solid red;")
    time.sleep(duration)
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                          element, original_style)


def test_profile_info_displayed(login_and_go_to_profile):
    driver = login_and_go_to_profile
    email = driver.find_element(By.ID, "email-display").text.strip()
    role = driver.find_element(By.ID, "role-display").text.strip()

    # Vurgulu kontrol için
    if email == "":
        element = driver.find_element(By.ID, "email-display")
        highlight_element(driver, element)
        pytest.fail("E-posta bilgisi boş olmamalı")

    if role not in ["customer", "supplier"]:
        element = driver.find_element(By.ID, "role-display")
        highlight_element(driver, element)
        pytest.fail(f"Geçersiz rol bilgisi: {role}")

    time.sleep(2)  # Kontrol sonrası bekle


def test_navbar_buttons_on_profile_page(login_and_go_to_profile):
    driver = login_and_go_to_profile

    home_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "to-home"))
    )
    highlight_element(driver, home_btn, duration=2)
    home_btn.click()

    WebDriverWait(driver, 20).until(EC.url_contains("index.html"))
    time.sleep(2)  # Ana sayfa yüklensin diye bekle

    assert "index.html" in driver.current_url, f"index.html'e yönlenemedi: {driver.current_url}"

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "products-list"))
        )
    except:
        driver.save_screenshot("products_list_not_found.png")
        pytest.fail("products-list elementi bulunamadı. Ekran görüntüsü alındı.")

    driver.get(f"{BASE_URL}/profile.html")
    time.sleep(2)  # Profil sayfası yüklenmesi için bekle
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "logout")))

    logout_btn = driver.find_element(By.ID, "logout")
    highlight_element(driver, logout_btn, duration=2)
    logout_btn.click()

    WebDriverWait(driver, 20).until(EC.url_contains("login.html"))
    time.sleep(2)  # Login sayfası yüklenene kadar bekle

    assert "login.html" in driver.current_url, f"login.html'e yönlenemedi: {driver.current_url}"


#cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
# pytest sel/test_profil.py -v  