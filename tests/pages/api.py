from urllib.parse import urlparse

from playwright.sync_api import Request


def is_api_call(request: Request, method: str, path: str) -> bool:
    return request.method == method and urlparse(request.url).path == path
