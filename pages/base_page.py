from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.header import Header

class BasePage:
    BASE_URL = "https://eco-city-tours.vercel.app"

    def __init__(self, driver):
        self.driver = driver
        self.header = Header(driver)

    def open(self, path=""):
        self.driver.get(f"{self.BASE_URL}{path}")

    def get_current_url(self):
        return self.driver.current_url