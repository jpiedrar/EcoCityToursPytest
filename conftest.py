import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    #driver.maximize_window()
    driver.get("https://eco-city-tours.vercel.app/")
    
    yield driver
    
    driver.quit()