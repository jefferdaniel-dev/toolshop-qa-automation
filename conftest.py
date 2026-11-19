from datetime import datetime
from pathlib import Path

import pytest

from tests.naming import slug


# Lives at the project root because pytest-html reads --html in its own
# pytest_configure, and tests/conftest.py is not loaded yet when pytest is
# launched from the root without a path; this one is.
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    base = config.option.htmlpath
    if not base:
        return
    filters = (config.option.markexpr, config.option.keyword)
    selection = "_".join(slug(value) for value in filters if value)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    config.option.htmlpath = Path(base).parent / f"{stamp}_{selection or 'all'}.html"
