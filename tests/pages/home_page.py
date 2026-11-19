from playwright.sync_api import Page, Response

from tests.pages.api import is_api_call
from tests.pages.login_page import LoginPage
from tests.pages.search_results_page import SearchResultsPage


class HomePage:
    def __init__(self, page: Page):
        self.page = page
        self.product_names = page.get_by_test_id("product-name")
        self.search_input = page.get_by_test_id("search-query")
        self.search_button = page.get_by_test_id("search-submit")
        self.sign_in_link = page.get_by_test_id("nav-sign-in")

    # Toolshop lists products with the HTTP QUERY method, not GET.
    def open(self) -> Response:
        with self.page.expect_response(
            lambda r: is_api_call(r.request, "QUERY", "/products")
        ) as response_info:
            self.page.goto("/")
        return response_info.value

    def type_search(self, term: str):
        self.search_input.fill(term)

    def submit_search(self) -> tuple[SearchResultsPage, Response]:
        with self.page.expect_response(
            lambda r: is_api_call(r.request, "QUERY", "/products/search")
        ) as response_info:
            self.search_button.click()
        return SearchResultsPage(self.page), response_info.value

    def open_login(self) -> LoginPage:
        self.sign_in_link.click()
        return LoginPage(self.page)
