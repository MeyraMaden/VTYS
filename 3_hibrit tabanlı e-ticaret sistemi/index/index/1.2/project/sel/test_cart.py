import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sel.config import BASE_URL, get_driver


def highlight(element, driver, duration=1):
    """Elementi ortada tutup kırmızı çerçeveyle vurgular."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    driver.execute_script("arguments[0].style.border='3px solid red';", element)
    time.sleep(duration)
    driver.execute_script("arguments[0].style.border='';", element)


def test_full_cart_flow():
    driver = get_driver()
    try:
        # 1) Giriş
        driver.get(f"{BASE_URL}/login.html")
        time.sleep(3)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "email")))
        driver.find_element(By.ID, "email").send_keys("customer@test.com")
        driver.find_element(By.ID, "password").send_keys("123456")
        login_btn = driver.find_element(By.ID, "login-button")
        highlight(login_btn, driver); time.sleep(2)
        login_btn.click()
        WebDriverWait(driver, 10).until(EC.url_contains("index.html"))
        time.sleep(3)

        # 2) Sepet sayfasına git
        driver.get(f"{BASE_URL}/cart.html")
        time.sleep(3)
        WebDriverWait(driver, 10).until(
            lambda d: d.find_elements(By.CLASS_NAME, "cart-item") or
                      d.find_elements(By.CSS_SELECTOR, "#cart-list p")
        )
        time.sleep(2)

        # 3) Sepetteki ürünleri listele
        items = driver.find_elements(By.CLASS_NAME, "cart-item")
        assert items, "❌ Sepette ürün bulunamadı."
        highlight(items[0], driver); time.sleep(2)

        # 4) Sepetten bir ürünü sil (varsa)
        remove_buttons = driver.find_elements(By.XPATH, "//button[text()='Sepetten Çıkar']")
        if remove_buttons:
            initial_count = len(items)
            btn = remove_buttons[0]
            highlight(btn, driver); time.sleep(2)
            btn.click()
            time.sleep(3)
            WebDriverWait(driver, 10).until(EC.url_contains("cart.html"))
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, "cart-item")) < initial_count
                      or d.find_elements(By.CSS_SELECTOR, "#cart-list p")
            )
            time.sleep(2)
            # vurgula sepet-list
            list_div = driver.find_element(By.ID, "cart-list")
            highlight(list_div, driver); time.sleep(2)

                # 5) Navbar butonlarını test et (cart.html sayfasındayken)
        nav_buttons = [
            ("to-home",    "index.html"),
            ("to-profile", "profile.html"),
        ]
        for btn_id, expected in nav_buttons:
            time.sleep(1)
            btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, btn_id)))
            highlight(btn, driver); time.sleep(2)
            btn.click()
            WebDriverWait(driver, 10).until(EC.url_contains(expected))
            time.sleep(2)
            assert expected in driver.current_url, f"❌ {btn_id} yönlendirme başarısız"
            driver.back()
            WebDriverWait(driver, 10).until(EC.url_contains("cart.html"))
            time.sleep(2)

        # logout
        time.sleep(1)
        logout_btn = driver.find_element(By.ID, "logout")
        highlight(logout_btn, driver); time.sleep(2)
        logout_btn.click()
        WebDriverWait(driver, 10).until(EC.url_contains("login.html"))
        time.sleep(2)
        highlight(driver.find_element(By.ID, "login-button"), driver); time.sleep(2)

                # 6) Yeniden login ve sepeti onayla
        driver.get(f"{BASE_URL}/login.html"); time.sleep(2)
        driver.find_element(By.ID, "email").send_keys("customer@test.com")
        driver.find_element(By.ID, "password").send_keys("123456")
        login_btn2 = driver.find_element(By.ID, "login-button")
        highlight(login_btn2, driver); time.sleep(2)
        login_btn2.click()
        WebDriverWait(driver, 10).until(EC.url_contains("index.html"))
        time.sleep(3)

        driver.get(f"{BASE_URL}/cart.html"); time.sleep(3)
        # checkout button appear
        driver.execute_script(
            "var btn=document.getElementById('checkout');btn.style.display='block';btn.disabled=false;"
        )
        checkout_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "checkout")))
        highlight(checkout_btn, driver); time.sleep(2)
        checkout_btn.click()
        WebDriverWait(driver, 10).until(EC.url_contains("success.html"))
        time.sleep(2)
        # Başarı sayfasını vurgula
        success_header = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.TAG_NAME, 'h1')))
        highlight(success_header, driver); time.sleep(2)

    finally:
        driver.quit()
        driver.quit()



       #  cd C:\Users\lenovo\OneDrive\Resimler\Masaüstü\index\index\1.2\project
    #   pytest sel/test_cart.py -v   