import json
import random
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import given, parsers, scenarios, then, when

from tests.pages.cart_page import CartPage
from tests.pages.checkout_page import CheckoutPage
from tests.pages.home_page import HomePage
from tests.pages.product_page import ProductPage
from tests.pages.search_results_page import SearchResultsPage

scenarios("../features/purchase.feature")

DATA_DIR = Path(__file__).parent.parent / "data"


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


@given(
    "que el usuario está en la tienda",
    target_fixture="home_page",
)
def store_with_products(page: Page):
    home = HomePage(page)
    home.open()
    expect(home.product_names.first).to_be_visible()
    return home


@when(parsers.parse('busca "{product}"'), target_fixture="results_page")
def search_product(home_page: HomePage, product: str):
    return home_page.search(product)


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
def add_to_cart(product_page: ProductPage):
    price = product_page.loaded_price()
    product_page.add_to_cart()
    return price


@when("abre el carrito", target_fixture="cart_page")
def open_cart(product_page: ProductPage):
    return product_page.open_cart()


@then(
    parsers.parse(
        've en el carrito "{product}" con cantidad 1 y el mismo precio del detalle'
    )
)
def see_product_in_cart(cart_page: CartPage, product: str, detail_price: str):
    expect(cart_page.product_titles).to_have_count(1)
    expect(cart_page.product_titles).to_contain_text(product)
    expect(cart_page.quantities).to_have_value("1")
    expect(cart_page.prices).to_have_text(f"${detail_price}")


@when(
    "continúa la compra como invitado con un comprador de prueba",
    target_fixture="checkout_page",
)
def continue_as_guest(cart_page: CartPage, buyer: dict):
    checkout = cart_page.proceed_to_checkout()
    checkout.continue_as_guest(buyer["email"], buyer["first_name"], buyer["last_name"])
    return checkout


@when("ingresa la dirección del comprador")
def enter_address(checkout_page: CheckoutPage, buyer: dict):
    checkout_page.fill_address(buyer["address"])


@when("paga con una tarjeta de prueba")
def pay_with_card(checkout_page: CheckoutPage, buyer: dict, card: dict):
    checkout_page.pay_with_card(card, f"{buyer['first_name']} {buyer['last_name']}")


@then("ve que el pago fue exitoso")
def see_payment_success(checkout_page: CheckoutPage):
    expect(checkout_page.payment_success_message).to_have_text(
        "Payment was successful"
    )


@when("confirma el pedido")
def confirm_order(checkout_page: CheckoutPage):
    checkout_page.confirm_order()


@then("recibe un número de factura")
def see_invoice_number(checkout_page: CheckoutPage):
    expect(checkout_page.order_confirmation).to_contain_text(re.compile(r"INV-\d+"))
