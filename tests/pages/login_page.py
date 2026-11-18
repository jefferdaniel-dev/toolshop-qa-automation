from playwright.sync_api import Page, Response


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.email = page.get_by_test_id("email")
        self.password = page.get_by_test_id("password")
        self.submit_button = page.get_by_test_id("login-submit")

    def fill(self, email: str, password: str):
        self.email.fill(email)
        self.password.fill(password)

    def submit(self) -> Response:
        with self.page.expect_response(
            lambda r: r.url.endswith("/users/login") and r.request.method == "POST"
        ) as response_info:
            self.submit_button.click()
        return response_info.value
