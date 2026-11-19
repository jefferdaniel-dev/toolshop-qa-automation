from playwright.sync_api import Locator, Page

from tests.pages.product_page import ProductPage


class SearchResultsPage:
    def __init__(self, page: Page):
        self.page = page
        self.product_names = page.get_by_test_id("product-name")

    def non_matching(self, term: str) -> Locator:
        return self.product_names.filter(has_not_text=term)

    def wait_until_filtered(self, term: str):
        # The home list stays on screen for a moment after the search response;
        # first wait for it to go, then for the filtered list to render.
        self.non_matching(term).first.wait_for(state="detached")
        self.product_names.filter(has_text=term).first.wait_for()

    def open_product(self, name: str) -> ProductPage:
        self.product_names.filter(has_text=name).click()
        return ProductPage(self.page)
