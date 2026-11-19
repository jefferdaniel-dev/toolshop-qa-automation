from urllib.parse import urlparse

from playwright.sync_api import Page, Response

from tests.pages.home_page import HomePage


def expect_status(response: Response, expected: int):
    # Comparing plain values keeps pytest from printing the Response, whose URL
    # carries the host and the query string.
    status = response.status
    call = f"{response.request.method} {urlparse(response.url).path}"
    assert status == expected, f"{call} returned {status}, expected {expected}"


def open_store(page: Page) -> HomePage:
    home = HomePage(page)
    expect_status(home.open(), 200)
    return home
