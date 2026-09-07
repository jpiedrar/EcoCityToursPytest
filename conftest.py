import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from endpoints.payment import PaymentEndpoint
from endpoints.reservations import ReservationsEndpoint

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
    
@pytest.fixture(scope="session")
def api_config():
    return {
        "base_url": "https://mockedapi.com/api/",
        "timeout": 5
    }
    
@pytest.fixture
def payment_client(api_config):
    return PaymentEndpoint(base_url=api_config["base_url"],timeout=api_config["timeout"])

@pytest.fixture
def reservation_client(api_config):
    return ReservationsEndpoint(base_url=api_config["base_url"],timeout=api_config["timeout"])

