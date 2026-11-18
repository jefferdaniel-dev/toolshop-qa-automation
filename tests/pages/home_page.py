from playwright.sync_api import Page

from tests.pages.search_results_page import SearchResultsPage


class HomePage:
    def __init__(self, page: Page):
        self.page = page
        self.product_names = page.get_by_test_id("product-name")
        self.search_input = page.get_by_test_id("search-query")
        self.search_button = page.get_by_test_id("search-submit")

    def open(self):
        with self.page.expect_response(
            lambda r: (r.url.endswith("/products") or "/products?" in r.url)
            and r.status == 200
        ):
            self.page.goto("/")

    def search(self, term: str) -> SearchResultsPage:
        self.search_input.fill(term)
        with self.page.expect_response(
            lambda r: "/products/search" in r.url and r.status == 200
        ):
            self.search_button.click()
        return SearchResultsPage(self.page)
