import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sel.config import BASE_URL, get_driver

# Elementi kırmızı kenarlık ve metin rengiyle vurgular.
def highlight(element, driver, duration=3):
    driver.execute_script(
        "arguments[0].style.border='3px solid red';"
        "arguments[0].style.color='red';",
        element
    )
    time.sleep(duration)
    driver.execute_script(
        "arguments[0].style.border='';"
        "arguments[0].style.color='';",
        element
    )


def logout(driver):
    try:
        logout_btn = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable((By.ID, "logout-btn"))
        )
        highlight(logout_btn, driver, duration=2)
        logout_btn.click()
        WebDriverWait(driver, 10).until(EC.url_contains("login.html"))
        time.sleep(2)
    except Exception:
        pass


def test_customer_can_add_to_cart(login_driver_customer):
    driver = login_driver_customer
    assert "index.html" in driver.current_url

    button = WebDriverWait(driver, 7).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "add-cart-btn"))
    )
    highlight(button, driver, duration=2)
    button.click()
    time.sleep(4)

    cart_btn = WebDriverWait(driver, 7).until(
        EC.element_to_be_clickable((By.ID, "to-cart"))
    )
    highlight(cart_btn, driver, duration=2)
    cart_btn.click()

    WebDriverWait(driver, 7).until(EC.url_contains("cart.html"))
    assert "cart.html" in driver.current_url
    time.sleep(3)

    cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
    assert len(cart_items) > 0, "Sepette ürün bulunamadı"

    logout(driver)


def test_customer_cannot_see_add_product_form(login_driver_customer):
    driver = login_driver_customer
    time.sleep(3)
    supplier_section = driver.find_elements(By.ID, "supplier-actions")
    assert not supplier_section or not supplier_section[0].is_displayed()
    time.sleep(3)
    logout(driver)


def test_supplier_can_add_product(login_driver_supplier):
    driver = login_driver_supplier
    assert "index.html" in driver.current_url

    product_name_input = driver.find_element(By.NAME, "product_name")
    highlight(product_name_input, driver, duration=2)
    product_name_input.send_keys("Selenium Test Ürünü")
    time.sleep(3)

    price_input = driver.find_element(By.NAME, "price")
    highlight(price_input, driver, duration=2)
    price_input.send_keys("99")
    time.sleep(3)

    add_button = driver.find_element(By.CSS_SELECTOR, "#new-product-form button")
    highlight(add_button, driver, duration=2)
    add_button.click()
    time.sleep(4)

    logout(driver)


def test_supplier_can_update_own_product(login_driver_supplier):
    driver = login_driver_supplier
    time.sleep(2)

    update_buttons = [
        btn for btn in driver.find_elements(By.CLASS_NAME, "update-btn")
        if btn.is_enabled()
    ]
    assert update_buttons, "Aktif güncelleme butonu bulunamadı"

    highlight(update_buttons[0], driver, duration=2)
    update_buttons[0].click()
    time.sleep(3)

    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    assert "ad" in alert.text.lower()
    alert.send_keys("Güncellenmiş Ürün")
    alert.accept()
    time.sleep(3)

    WebDriverWait(driver, 5).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    assert "fiyat" in alert.text.lower()
    alert.send_keys("888")
    alert.accept()

    time.sleep(2)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Güncellenmiş Ürün" in body_text

    logout(driver)


def test_supplier_can_delete_own_product(login_driver_supplier):
    driver = login_driver_supplier
    time.sleep(3)

    delete_buttons = [
        btn for btn in driver.find_elements(By.CLASS_NAME, "delete-btn")
        if btn.is_enabled()
    ]
    assert delete_buttons, "Aktif silme butonu bulunamadı"

    driver.execute_script("window.confirm = () => true")
    highlight(delete_buttons[0], driver, duration=2)
    delete_buttons[0].click()
    time.sleep(4)

    assert "index.html" in driver.current_url

    logout(driver)


def test_navbar_buttons_work(login_driver_supplier):
    driver = login_driver_supplier

    profile_btn = WebDriverWait(driver, 7).until(
        EC.element_to_be_clickable((By.ID, "to-profile"))
    )
    highlight(profile_btn, driver, duration=2)
    profile_btn.click()
    time.sleep(3)

    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])

    WebDriverWait(driver, 7).until(EC.url_contains("profile.html"))
    assert "profile.html" in driver.current_url

    logout(driver)


    #  cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
    #   pytest sel/test_index.py -v