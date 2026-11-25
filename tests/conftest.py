import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import allure
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page

from tests.naming import slug


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
        request.node.get_closest_marker("compra")
        and urlparse(base_url).hostname != TOOLSHOP_HOST
    ):
        pytest.skip(
            f"@compra only runs against {TOOLSHOP_HOST}; BASE_URL points elsewhere"
        )


EVIDENCE_ROOT = Path(__file__).parent.parent / "evidencias"


SCENARIO_TAGS = ("search", "cart", "compra")


class Evidence:
    def __init__(self, page: Page, folder: Path):
        self.page = page
        self.folder = folder
        self.count = 0

    def capture(self, module: str):
        self.count += 1
        self.folder.mkdir(parents=True, exist_ok=True)
        shot = self.folder / f"{self.count:02d}-{module}.png"
        self.page.screenshot(path=shot, full_page=True)
        allure.attach.file(
            shot,
            name=f"{self.count:02d}-{module}",
            attachment_type=allure.attachment_type.PNG,
        )

    def append_to_folder(self, suffix: str):
        clean = slug(suffix)
        renamed = self.folder.with_name(f"{self.folder.name}_{clean}")
        self.folder.rename(renamed)
        self.folder = renamed


@pytest.fixture
def evidence(request, page: Page, _pytest_bdd_example: dict) -> Evidence:
    # pytest-bdd exposes the current Examples row through this fixture; it is
    # empty for plain scenarios such as home.feature (no tag, no product).
    tag = next(
        (t for t in SCENARIO_TAGS if request.node.get_closest_marker(t)), "home"
    )
    if tag == "compra":
        tag = _pytest_bdd_example["etapa"]
    parts = [tag]
    if "producto" in _pytest_bdd_example:
        parts.append(_pytest_bdd_example["producto"])
    if "acceso" in _pytest_bdd_example:
        # An empty access cell means a guest purchase (D20).
        parts.append(_pytest_bdd_example["acceso"] or "invitado")
    started = datetime.now()
    name = "_".join([started.strftime("%H-%M-%S"), *(slug(p) for p in parts)])
    return Evidence(page, EVIDENCE_ROOT / started.strftime("%Y-%m-%d") / name)


FAILURE_SHOTS = Path(__file__).parent.parent / "test-results"


PAGE_KEY = pytest.StashKey[Page]()


@pytest.fixture
def page(page: Page, request) -> Page:
    # pytest-bdd requests `page` dynamically, so it never reaches item.funcargs;
    # the stash lets the report hook find it.
    request.node.stash[PAGE_KEY] = page
    return page


# A hook is used instead of pytest-playwright's --screenshot only-on-failure:
# that option captures when the context closes, after the report of the call
# phase, so the image could not be attached to the failed step.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    page = item.stash.get(PAGE_KEY, None)
    if report.when != "call" or not report.failed or page is None:
        return
    FAILURE_SHOTS.mkdir(exist_ok=True)
    path = FAILURE_SHOTS / f"{slug(item.name)}.png"
    page.screenshot(path=path, full_page=True)
    allure.attach.file(
        path, name="fallo", attachment_type=allure.attachment_type.PNG
    )
