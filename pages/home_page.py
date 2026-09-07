from pages.base_page import BasePage
from selenium.webdriver.common.by import By

class HomePage(BasePage):
    def __init__ (self, driver): 
        super().__init__(driver)
        self.hero_title_label = (By.XPATH, "//h1")
        self.tours_section = (By.ID, "tours")
        self.guide_section = (By.ID, "guide")
        self.contact_section = (By.ID, "contact")

    def open(self):
        pass

    def get_hero_title_text(self):
        text = self.driver.find_element(*self.hero_title_label).text
        return " ".join(text.split())
    
    def is_tours_section_visible(self): 
        return self.driver.find_element(*self.tours_section).is_displayed()
    
    def is_guide_section_visible(self):
        return self.driver.find_element(*self.guide_section).is_displayed()
    
    def is_contact_section_visible(self):
        return self.driver.find_element(*self.contact_section).is_displayed()