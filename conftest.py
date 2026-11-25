import os
from datetime import datetime
from pathlib import Path

import allure_commons
import pytest

from tests.allure_privacy import AllurePrivacy
from tests.naming import slug


# Lives at the project root because tests/conftest.py is not loaded yet when
# pytest is launched from the root without a path; this one is. It runs before
# the Allure plugin reads --alluredir.
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    allure_commons.plugin_manager.register(AllurePrivacy())
    base = config.option.allure_report_dir
    if not base:
        return
    filters = (config.option.markexpr, config.option.keyword)
    selection = "_".join(slug(value) for value in filters if value)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    config.option.allure_report_dir = str(
        Path(base) / f"{stamp}_{selection or 'all'}" / "resultados"
    )


# In the container the whole suite must never start by accident, e.g. when only
# `-v` is passed; a bare run (`--markers`) does not collect, so it is unaffected.
def pytest_collection(session):
    options = session.config.option
    if os.environ.get("RUNNING_IN_DOCKER") and not (options.markexpr or options.keyword):
        raise pytest.UsageError(
            'Elige qué correr con -m <tag> o -k "<texto>", '
            'por ejemplo: -m search -k "Combination and Pliers".'
        )
