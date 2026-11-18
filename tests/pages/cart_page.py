from playwright.sync_api import Page

from tests.pages.checkout_page import CheckoutPage


class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.product_titles = page.get_by_test_id("product-title")
        self.quantities = page.get_by_test_id("product-quantity")
        self.prices = page.get_by_test_id("product-price")
        self.proceed_button = page.get_by_test_id("proceed-1")

    def proceed_to_checkout(self) -> CheckoutPage:
        self.proceed_button.click()
        return CheckoutPage(self.page)
