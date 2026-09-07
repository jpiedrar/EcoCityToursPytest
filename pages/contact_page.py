from pages.base_page import BasePage
from selenium.webdriver.common.by import By

class ContactPage(BasePage): 
    PATH = "/contact"

    def __init__ (self, driver): 
        super().__init__(driver)

    def open(self):
        super().open(self.PATH)