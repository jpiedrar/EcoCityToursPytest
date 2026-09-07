import pytest
from pages.home_page import HomePage

def test_validate_url(driver):
    home_page = HomePage(driver)
    home_page.open()
    assert home_page.get_current_url() == f"{home_page.BASE_URL}/"

def test_validate_all_locators(driver):
    home_page = HomePage(driver)
    assert home_page.is_tours_section_visible()
    assert home_page.is_guide_section_visible()
    assert home_page.is_contact_section_visible()

def test_validate_title_label(driver):
    home_page = HomePage(driver)
    assert "Historias que se caminan." in home_page.get_hero_title_text()