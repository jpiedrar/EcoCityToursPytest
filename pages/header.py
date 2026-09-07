from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Header: 
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.header_buttons = {
            "logo": (By.ID, "header-home-link"),
            "tours": (By.ID, "header-tours-link"),
            "san_jose": (By.ID, "header-tour-san-jose-link"),
            "cartago": (By.ID, "header-tour-irazu-cartago-orosi-link"),
            "team": (By.ID, "header-team-link"),
            "contact": (By.ID, "header-contact-link")
        }

    def navigate_to(self, page):
        locator = self.header_buttons[page.lower()]
        element = self.wait.until(
            EC.element_to_be_clickable(locator)
        )
        element.click()