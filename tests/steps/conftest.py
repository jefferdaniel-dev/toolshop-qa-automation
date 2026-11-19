from playwright.sync_api import Page, expect
from pytest_bdd import given

from tests.steps.helpers import open_store


@given("que el usuario está en la tienda", target_fixture="home_page")
def store_with_products(page: Page, evidence):
    home = open_store(page)
    expect(home.product_names.first).to_be_visible()
    evidence.capture("home")
    return home
