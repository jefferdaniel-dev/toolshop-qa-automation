import re

from playwright.sync_api import Page

from tests.pages.cart_page import CartPage


class ProductPage:
    def __init__(self, page: Page):
        self.page = page
        self.unit_price = page.get_by_test_id("unit-price")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")
        self.cart_link = page.get_by_test_id("nav-cart")

    def loaded_price(self) -> str:
        self.unit_price.filter(has_text=re.compile(r"\d")).wait_for()
        return self.unit_price.inner_text()

    def add_to_cart(self):
        with self.page.expect_response(
            lambda r: r.url.endswith("/carts")
            and r.request.method == "POST"
            and r.status == 201
        ):
            self.add_to_cart_button.click()

    def open_cart(self) -> CartPage:
        self.cart_link.click()
        return CartPage(self.page)
