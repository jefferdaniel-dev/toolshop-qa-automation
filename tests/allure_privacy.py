import allure_commons

from tests.redaction import redact_paths, redact_secrets

HIDDEN_LABELS = {"host", "thread"}


def _clear_parameters(steps):
    for step in steps:
        step.parameters = []
        _clear_parameters(step.steps)


def _redact_details(item):
    details = item.statusDetails
    if details is None:
        return
    for field in ("message", "trace"):
        text = getattr(details, field)
        if text:
            setattr(details, field, redact_paths(redact_secrets(text)))


def _redact_steps(steps):
    for step in steps:
        _redact_details(step)
        _redact_steps(step.steps)


class AllurePrivacy:
    """Strip step arguments, machine labels, the test credentials and the project
    path before Allure writes a result.

    The plugin stores the value of every fixture a step receives (a password
    would end up in the JSON) and the host name of the machine. Playwright also
    writes typed values in its error messages (call log of `fill`, aria
    snapshot of `expect`), so the messages and traces are redacted here; the
    console and the text attachments are redacted earlier, in the report.
    """

    @allure_commons.hookimpl(tryfirst=True)
    def report_result(self, result):
        _clear_parameters(result.steps)
        result.labels = [l for l in result.labels if l.name not in HIDDEN_LABELS]
        _redact_details(result)
        _redact_steps(result.steps)

    @allure_commons.hookimpl(tryfirst=True)
    def report_container(self, container):
        for fixture in [*container.befores, *container.afters]:
            fixture.parameters = []
            _clear_parameters(fixture.steps)
