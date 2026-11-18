from playwright.sync_api import Page


class HomePage:
    def __init__(self, page: Page):
        self.page = page
        self.product_names = page.get_by_test_id("product-name")

    def open(self):
        self.page.goto("/")
