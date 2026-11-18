import os
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    # Toolshop follows the browser language; locators rely on the English UI.
    return {**browser_context_args, "locale": "en-US"}


@pytest.fixture(scope="session")
def base_url():
    url = os.environ.get("BASE_URL")
    if not url:
        pytest.fail("BASE_URL is not set; define it in the environment or in .env")
    return url


TOOLSHOP_HOST = "practicesoftwaretesting.com"


@pytest.fixture(autouse=True)
def checkout_only_on_toolshop(request, base_url):
    if (
        request.node.get_closest_marker("checkout")
        and urlparse(base_url).hostname != TOOLSHOP_HOST
    ):
        pytest.skip(
            f"@checkout only runs against {TOOLSHOP_HOST}; BASE_URL points elsewhere"
        )
