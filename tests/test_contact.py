from pages.contact_page import ContactPage

def test_validate_url(driver):
    contact_page = ContactPage(driver)
    contact_page.header.navigate_to("contact")
    assert contact_page.get_current_url() == f"{contact_page.BASE_URL}/contact"