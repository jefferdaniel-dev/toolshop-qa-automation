from playwright.sync_api import Page


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.guest_tab = page.get_by_role("tab", name="Continue as Guest")
        self.guest_email = page.get_by_test_id("guest-email")
        self.guest_first_name = page.get_by_test_id("guest-first-name")
        self.guest_last_name = page.get_by_test_id("guest-last-name")
        self.guest_submit = page.get_by_test_id("guest-submit")
        self.proceed_as_guest_button = page.get_by_test_id("proceed-2-guest")
        self.country = page.get_by_test_id("country")
        self.postal_code = page.get_by_test_id("postal_code")
        self.house_number = page.get_by_test_id("house_number")
        self.street = page.get_by_test_id("street")
        self.proceed_to_payment_button = page.get_by_test_id("proceed-3")
        self.payment_method = page.get_by_test_id("payment-method")
        self.card_number = page.get_by_test_id("credit_card_number")
        self.expiration_date = page.get_by_test_id("expiration_date")
        self.cvv = page.get_by_test_id("cvv")
        self.card_holder_name = page.get_by_test_id("card_holder_name")
        self.finish_button = page.get_by_test_id("finish")
        self.payment_success_message = page.get_by_test_id("payment-success-message")
        self.order_confirmation = page.get_by_text("Thanks for your order")

    def continue_as_guest(self, email: str, first_name: str, last_name: str):
        self.guest_tab.click()
        self.guest_email.fill(email)
        self.guest_first_name.fill(first_name)
        self.guest_last_name.fill(last_name)
        self.guest_submit.click()
        self.proceed_as_guest_button.click()

    def fill_address(self, address: dict):
        self.country.select_option(address["country"])
        # City and state are not typed: the API answers 422 when they differ from
        # the postcode lookup. Street is typed after every lookup response because
        # each response overwrites it.
        lookups = []

        def collect(request):
            if "/postcode-lookup" in request.url:
                lookups.append(request)

        self.page.on("request", collect)
        try:
            with self.page.expect_response(lambda r: "/postcode-lookup" in r.url):
                self.postal_code.fill(address["postal_code"])
                self.house_number.fill(address["house_number"])
        finally:
            self.page.remove_listener("request", collect)
        for request in lookups:
            response = request.response()
            if response is None:
                raise RuntimeError("postcode lookup request failed")
            response.finished()
        self.street.fill(address["street"])
        self.proceed_to_payment_button.click()

    def pay_with_card(self, card: dict, holder_name: str):
        self.payment_method.select_option("credit-card")
        self.card_number.fill(card["number"])
        self.expiration_date.fill(card["expiration"])
        self.cvv.fill(card["cvv"])
        self.card_holder_name.fill(holder_name)
        with self.page.expect_response(
            lambda r: r.url.endswith("/payment/check")
            and r.request.method == "POST"
            and r.status == 200
        ):
            self.finish_button.click()

    def confirm_order(self):
        with self.page.expect_response(
            lambda r: r.url.endswith("/invoices/guest")
            and r.request.method == "POST"
            and r.status == 201
        ):
            self.finish_button.click()
