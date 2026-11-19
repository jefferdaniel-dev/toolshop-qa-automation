from playwright.sync_api import Page, Response

from tests.pages.api import is_api_call
from tests.pages.login_page import LoginPage


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.guest_tab = page.get_by_role("tab", name="Continue as Guest")
        self.guest_email = page.get_by_test_id("guest-email")
        self.guest_first_name = page.get_by_test_id("guest-first-name")
        self.guest_last_name = page.get_by_test_id("guest-last-name")
        self.guest_submit = page.get_by_test_id("guest-submit")
        self.proceed_as_guest_button = page.get_by_test_id("proceed-2-guest")
        self.login = LoginPage(page)
        self.proceed_as_user_button = page.get_by_test_id("proceed-2")
        self.country = page.get_by_test_id("country")
        self.postal_code = page.get_by_test_id("postal_code")
        self.house_number = page.get_by_test_id("house_number")
        self.street = page.get_by_test_id("street")
        self.city = page.get_by_test_id("city")
        self.state = page.get_by_test_id("state")
        self.proceed_to_payment_button = page.get_by_test_id("proceed-3")
        self.payment_method = page.get_by_test_id("payment-method")
        self.card_number = page.get_by_test_id("credit_card_number")
        self.expiration_date = page.get_by_test_id("expiration_date")
        self.cvv = page.get_by_test_id("cvv")
        self.card_holder_name = page.get_by_test_id("card_holder_name")
        self.finish_button = page.get_by_test_id("finish")
        self.payment_success_message = page.get_by_test_id("payment-success-message")
        self.order_confirmation = page.get_by_text("Thanks for your order")
        self.invoice_path = None

    def fill_guest(self, email: str, first_name: str, last_name: str):
        self.guest_tab.click()
        self.guest_email.fill(email)
        self.guest_first_name.fill(first_name)
        self.guest_last_name.fill(last_name)

    def submit_guest(self):
        self.guest_submit.click()
        self.proceed_as_guest_button.click()
        self.invoice_path = "/invoices/guest"

    def proceed_as_user(self):
        self.proceed_as_user_button.click()
        self.invoice_path = "/invoices"

    def fill_address(
        self, country: str, postal_code: str, house_number: str, street: str
    ) -> Response:
        self.country.select_option(country)
        # City and state are not typed: the API answers 422 when they differ from
        # the postcode lookup. Street is typed after every lookup response because
        # each response overwrites it.
        lookups = []

        def is_lookup(request) -> bool:
            return is_api_call(request, "GET", "/postcode-lookup")

        def collect(request):
            if is_lookup(request):
                lookups.append(request)

        self.page.on("request", collect)
        try:
            with self.page.expect_response(lambda r: is_lookup(r.request)):
                self.postal_code.fill(postal_code)
                self.house_number.fill(house_number)
        finally:
            self.page.remove_listener("request", collect)
        for request in lookups:
            response = request.response()
            if response is None:
                raise RuntimeError("postcode lookup request failed")
            response.finished()
        self.street.fill(street)
        return lookups[-1].response()

    def proceed_to_payment(self):
        self.proceed_to_payment_button.click()

    def fill_card(self, card: dict, holder_name: str):
        self.payment_method.select_option("credit-card")
        self.card_number.fill(card["number"])
        self.expiration_date.fill(card["expiration"])
        self.cvv.fill(card["cvv"])
        self.card_holder_name.fill(holder_name)

    def submit_payment(self) -> Response:
        with self.page.expect_response(
            lambda r: r.url.endswith("/payment/check")
            and r.request.method == "POST"
        ) as response_info:
            self.finish_button.click()
        return response_info.value

    def confirm_order(self) -> Response:
        with self.page.expect_response(
            lambda r: r.url.endswith(self.invoice_path)
            and r.request.method == "POST"
        ) as response_info:
            self.finish_button.click()
        return response_info.value
