import re

from playwright.sync_api import Page, Response

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

    def add_to_cart(self) -> Response:
        # POST /carts only creates the cart; the item is added by POST /carts/{id}.
        with self.page.expect_response(
            lambda r: re.search(r"/carts/[^/?]+$", r.url) is not None
            and r.request.method == "POST"
        ) as response_info:
            self.add_to_cart_button.click()
        return response_info.value

    def open_cart(self) -> tuple[CartPage, Response]:
        with self.page.expect_response(
            lambda r: re.search(r"/carts/[^/?]+$", r.url) is not None
            and r.request.method == "GET"
        ) as response_info:
            self.cart_link.click()
        return CartPage(self.page), response_info.value
