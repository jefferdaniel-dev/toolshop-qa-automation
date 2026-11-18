import re

from playwright.sync_api import Page, expect
from pytest_bdd import given, scenarios, then

from tests.pages.home_page import HomePage

scenarios("../features/home.feature")


@given("que el usuario abre la tienda", target_fixture="home_page")
def open_store(page: Page):
    home = HomePage(page)
    home.open()
    return home


@then("ve la página principal")
def see_home(home_page: HomePage):
    expect(home_page.page).to_have_title(re.compile("Toolshop"))
    expect(home_page.product_names.first).to_be_visible()
