import json
import os
import random
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from tests.pages.cart_page import CartPage
from tests.pages.checkout_page import CheckoutPage
from tests.pages.home_page import HomePage
from tests.pages.login_page import LoginPage
from tests.pages.product_page import ProductPage
from tests.pages.search_results_page import SearchResultsPage
from tests.steps.helpers import expect_status, open_store

scenarios("../features/purchase.feature")

DATA_DIR = Path(__file__).parent.parent / "data"
INVOICE_NUMBER = re.compile(r"INV-\d+")


def random_entry(file_name: str) -> dict:
    return random.choice(json.loads((DATA_DIR / file_name).read_text(encoding="utf-8")))


@pytest.fixture
def buyer() -> dict:
    chosen = random_entry("buyers.json")
    print(f"Buyer: {chosen['first_name']} {chosen['last_name']}")
    return chosen


@pytest.fixture
def card() -> dict:
    chosen = random_entry("cards.json")
    print(f"Card: {chosen['label']}")
    return chosen


@when(parsers.parse('busca "{product}"'), target_fixture="results_page")
def search_product(home_page: HomePage, product: str, evidence):
    home_page.type_search(product)
    evidence.capture("busqueda")
    results, response = home_page.submit_search()
    expect_status(response, 200)
    # The screenshot must show the filtered list, not the home list still on screen.
    results.wait_until_filtered(product)
    evidence.capture("resultados")
    return results


@then(parsers.parse('ve resultados y todos contienen "{product}"'))
def see_matching_results(results_page: SearchResultsPage, product: str):
    expect(results_page.product_names.first).to_contain_text(product)
    expect(results_page.non_matching(product)).to_have_count(0)


@when(
    parsers.parse('abre "{product}" desde los resultados'),
    target_fixture="product_page",
)
def open_product(results_page: SearchResultsPage, product: str):
    return results_page.open_product(product)


@when("agrega el producto al carrito", target_fixture="detail_price")
def add_to_cart(product_page: ProductPage, evidence):
    price = product_page.loaded_price()
    evidence.capture("producto")
    response = product_page.add_to_cart()
    expect_status(response, 200)
    return price


@when("abre el carrito", target_fixture="cart_page")
def open_cart(product_page: ProductPage):
    cart, response = product_page.open_cart()
    expect_status(response, 200)
    return cart


@then(
    parsers.parse(
        've en el carrito "{product}" con cantidad 1 y el mismo precio del detalle'
    )
)
def see_product_in_cart(
    cart_page: CartPage, product: str, detail_price: str, evidence
):
    expect(cart_page.product_titles).to_have_count(1)
    expect(cart_page.product_titles).to_contain_text(product)
    expect(cart_page.quantities).to_have_value("1")
    expect(cart_page.prices).to_have_text(f"${detail_price}")
    evidence.capture("carrito")


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        pytest.fail(f"{name} is not set; define it in the environment or in .env")
    return value


def log_in(login: LoginPage, evidence):
    login.fill(required_env("TEST_USER_EMAIL"), required_env("TEST_USER_PASSWORD"))
    # The screenshot must not reveal the password.
    expect(login.password).to_have_attribute("type", "password")
    evidence.capture("login")
    expect_status(login.submit(), 200)


ACCESS_TYPES = ("invitado", "login_checkout", "login_home")


# parsers.parse cannot match an empty value, and an empty cell means "invitado".
@given(
    parsers.re(r'que el usuario usa el acceso "(?P<access>[^"]*)"'),
    target_fixture="access",
)
def choose_access(
    page: Page, home_page: HomePage, access: str, evidence
) -> str:
    access = access or "invitado"
    if access not in ACCESS_TYPES:
        pytest.fail(
            f'Unknown access "{access}"; expected one of {", ".join(ACCESS_TYPES)} '
            "or an empty cell"
        )
    if access == "login_home":
        log_in(home_page.open_login(), evidence)
        expect(page).to_have_url(re.compile(r"/account"))
        back_home = open_store(page)
        expect(back_home.user_menu).to_be_visible()
        evidence.capture("home")
    return access


STAGES = ("checkout", "confirmacion")


@given(
    parsers.parse('que la compra llega hasta la etapa "{stage}"'),
    target_fixture="stage",
)
def choose_stage(stage: str) -> str:
    if stage not in STAGES:
        pytest.fail(f'Unknown stage "{stage}"; expected one of {", ".join(STAGES)}')
    return stage


@when("continúa la compra", target_fixture="checkout_page")
def continue_checkout(cart_page: CartPage, access: str, buyer: dict, evidence):
    checkout = cart_page.proceed_to_checkout()
    if access == "invitado":
        checkout.fill_guest(buyer["email"], buyer["first_name"], buyer["last_name"])
        evidence.capture("invitado")
        checkout.submit_guest()
        return checkout
    if access == "login_checkout":
        log_in(checkout.login, evidence)
        checkout.proceed_as_user()
        # The address step asks for the profile again (GET /users/me) and fills
        # the form with it; typing before it lands loses the address.
        expect(checkout.street).not_to_have_value("")
        return checkout
    # Already logged in, the checkout fills the address from the profile on
    # arrival; entering the address step before that requests the profile again,
    # and the late copy wipes the address typed afterwards.
    expect(checkout.street).not_to_have_value("")
    checkout.proceed_as_user()
    return checkout


@when(
    parsers.parse(
        'ingresa la dirección "{street}" "{house_number}" '
        'con código postal "{postal_code}" en "{country}"'
    ),
    target_fixture="lookup",
)
def enter_address(
    checkout_page: CheckoutPage,
    street: str,
    house_number: str,
    postal_code: str,
    country: str,
) -> dict:
    response = checkout_page.fill_address(country, postal_code, house_number, street)
    expect_status(response, 200)
    return response.json()


@then("la ciudad y el estado se autocompletan según el código postal")
def see_city_and_state_autocompleted(
    checkout_page: CheckoutPage, lookup: dict, evidence
):
    expect(checkout_page.city).to_have_value(lookup["city"])
    expect(checkout_page.state).to_have_value(lookup["state"] or "")
    evidence.capture("direccion")


@when("llena la tarjeta de prueba")
def fill_test_card(checkout_page: CheckoutPage, buyer: dict, card: dict, evidence):
    checkout_page.proceed_to_payment()
    checkout_page.fill_card(card, f"{buyer['first_name']} {buyer['last_name']}")
    evidence.capture("pago")


@then("la compra termina según la etapa")
def finish_purchase(checkout_page: CheckoutPage, stage: str, evidence):
    if stage == "checkout":
        expect(checkout_page.finish_button).to_be_enabled()
        return
    expect_status(checkout_page.submit_payment(), 200)
    see_payment_success(checkout_page, evidence)
    confirm_order(checkout_page)
    see_invoice_number(checkout_page, evidence)


def see_payment_success(checkout_page: CheckoutPage, evidence):
    expect(checkout_page.payment_success_message).to_have_text(
        "Payment was successful"
    )
    evidence.capture("pago-exitoso")


def confirm_order(checkout_page: CheckoutPage):
    expect_status(checkout_page.confirm_order(), 201)


def see_invoice_number(checkout_page: CheckoutPage, evidence):
    expect(checkout_page.order_confirmation).to_contain_text(INVOICE_NUMBER)
    evidence.capture("factura")
    invoice = INVOICE_NUMBER.search(checkout_page.order_confirmation.inner_text())
    assert invoice, "invoice number not found in the confirmation text"
    evidence.append_to_folder(invoice.group())
