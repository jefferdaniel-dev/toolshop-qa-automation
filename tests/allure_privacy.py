import json
import os

import allure_commons

HIDDEN_LABELS = {"host", "thread"}


def _clear_parameters(steps):
    for step in steps:
        step.parameters = []
        _clear_parameters(step.steps)


def _secret_forms():
    # Read at call time: the plugin is registered before load_dotenv() runs.
    secret = os.environ.get("TEST_USER_PASSWORD", "")
    if not secret.strip():
        return []
    forms = {
        secret,
        json.dumps(secret, ensure_ascii=False)[1:-1],
        repr(secret)[1:-1],
    }
    return sorted(forms, key=len, reverse=True)


def _redact_details(item, forms):
    details = item.statusDetails
    if details is None:
        return
    for field in ("message", "trace"):
        text = getattr(details, field)
        if not text:
            continue
        for form in forms:
            text = text.replace(form, "***")
        setattr(details, field, text)


def _redact_steps(steps, forms):
    for step in steps:
        _redact_details(step, forms)
        _redact_steps(step.steps, forms)


class AllurePrivacy:
    """Strip step arguments, machine labels and the test password before Allure
    writes a result.

    The plugin stores the value of every fixture a step receives (a password
    would end up in the JSON) and the host name of the machine. Playwright also
    writes typed values in its error messages (call log of `fill`, aria
    snapshot of `expect`); only TEST_USER_PASSWORD is redacted there.
    """

    @allure_commons.hookimpl(tryfirst=True)
    def report_result(self, result):
        _clear_parameters(result.steps)
        result.labels = [l for l in result.labels if l.name not in HIDDEN_LABELS]
        forms = _secret_forms()
        if forms:
            _redact_details(result, forms)
            _redact_steps(result.steps, forms)

    @allure_commons.hookimpl(tryfirst=True)
    def report_container(self, container):
        for fixture in [*container.befores, *container.afters]:
            fixture.parameters = []
            _clear_parameters(fixture.steps)
