# selenium/config.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:5000"  # Flask çalıştığında gelen adres

def get_driver():
    options = Options()
   # options.add_argument("--headless=new")  # Tarayıcıyı gizli modda çalıştırır
    options.add_argument("--window-size=1920,1080")
    service = Service()  # varsayılan chromedriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver
