import re

from playwright.sync_api import expect
from pytest_bdd import scenarios, then

from tests.pages.home_page import HomePage

scenarios("../features/home.feature")


@then("ve la página principal")
def see_home(home_page: HomePage):
    expect(home_page.page).to_have_title(re.compile("Toolshop"))
    expect(home_page.product_names.first).to_be_visible()
