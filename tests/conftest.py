import os

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def test_id_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session")
def base_url():
    url = os.environ.get("BASE_URL")
    if not url:
        pytest.fail("BASE_URL is not set; define it in the environment or in .env")
    return url
