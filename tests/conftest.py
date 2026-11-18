import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page

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


EVIDENCE_ROOT = Path(__file__).parent.parent / "evidencias"


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class Evidence:
    def __init__(self, page: Page, folder: Path):
        self.page = page
        self.folder = folder
        self.count = 0

    def capture(self, module: str):
        self.count += 1
        self.folder.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(
            path=self.folder / f"{self.count:02d}-{module}-{timestamp()}.png",
            full_page=True,
        )

    def append_to_folder(self, suffix: str):
        clean = re.sub(r"[^\w-]+", "-", suffix).strip("-")
        renamed = self.folder.with_name(f"{self.folder.name}_{clean}")
        self.folder.rename(renamed)
        self.folder = renamed


@pytest.fixture
def evidence(page: Page, _pytest_bdd_example: dict) -> Evidence:
    # pytest-bdd exposes the current Examples row through this fixture; it is
    # empty for plain scenarios such as home.feature.
    product = _pytest_bdd_example.get("producto", "home")
    folder_name = re.sub(r"[^\w-]+", "-", product).strip("-")
    started = datetime.now()
    folder = (
        EVIDENCE_ROOT
        / started.strftime("%Y-%m-%d")
        / f"{folder_name}_{started.strftime('%Y-%m-%d_%H-%M-%S')}"
    )
    return Evidence(page, folder)
