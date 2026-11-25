import json
import os
import re
import types
from pathlib import Path

MASK = "***"
SECRET_VARIABLES = ("TEST_USER_PASSWORD", "TEST_USER_EMAIL")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _escaped_forms(value: str) -> set[str]:
    # Prefixing a double quote makes repr() and ascii() pick single quotes, which
    # escapes a single quote inside the value (`\'`) as it appears in some messages.
    return {
        value,
        json.dumps(value, ensure_ascii=False)[1:-1],
        json.dumps(value)[1:-1],
        repr(value)[1:-1],
        repr('"' + value)[2:-1],
        ascii(value)[1:-1],
        ascii('"' + value)[2:-1],
    }


def _secret_forms() -> list[str]:
    # Read at call time: the plugins are registered before load_dotenv() runs.
    forms: set[str] = set()
    for name in SECRET_VARIABLES:
        value = os.environ.get(name, "")
        if not value.strip():
            continue
        # Playwright's aria snapshot collapses runs of whitespace.
        for variant in (value, " ".join(value.split())):
            forms |= _escaped_forms(variant)
    return sorted(forms, key=len, reverse=True)


def redact_secrets(text: str) -> str:
    for form in _secret_forms():
        text = text.replace(form, MASK)
    return text


def _root_patterns() -> list[re.Pattern]:
    roots = {str(PROJECT_ROOT), os.path.abspath(Path(__file__).parent.parent)}
    forms = set()
    for root in roots:
        forms |= {root, root.replace("\\", "/"), root.replace("\\", "\\\\")}
    # The drive letter may come in either case, so the match ignores case.
    return [
        re.compile(re.escape(form) + r"(\\\\|[\\/])?", re.IGNORECASE)
        for form in sorted(forms, key=len, reverse=True)
    ]


def redact_paths(text: str) -> str:
    """Make the project path relative: `C:\\proj\\tests\\a.py` becomes `tests\\a.py`."""
    for pattern in _root_patterns():
        text = pattern.sub(lambda m: "" if m.group(1) else ".", text)
    return text


def _map_strings(value, fn, seen: set[int]):
    if isinstance(value, str):
        return fn(value)
    if isinstance(value, list):
        value[:] = [_map_strings(item, fn, seen) for item in value]
        return value
    if isinstance(value, tuple):
        items = [_map_strings(item, fn, seen) for item in value]
        return type(value)(*items) if hasattr(value, "_fields") else tuple(items)
    skip = (type, types.ModuleType, types.FunctionType)
    if hasattr(value, "__dict__") and not isinstance(value, skip) and id(value) not in seen:
        seen.add(id(value))
        for name, attribute in list(vars(value).items()):
            object.__setattr__(value, name, _map_strings(attribute, fn, seen))
    return value


def redact_report(report) -> None:
    """Redact the secrets in what pytest prints and Allure reads from a report.

    `longrepr` is text, a tuple or a tree of repr objects (one per exception of a
    chain); only the strings inside change, so the traceback keeps its shape.
    """
    report.longrepr = _map_strings(report.longrepr, redact_secrets, set())
    report.sections = _map_strings(report.sections, redact_secrets, set())
