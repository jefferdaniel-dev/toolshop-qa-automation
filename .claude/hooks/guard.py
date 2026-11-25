"""PreToolUse launcher: runs the rules in guard_rules.py.

If the rules cannot be loaded (syntax error, import failure, missing file) the
launcher falls back to a degraded mode so the session is not locked out: reading
and searching stay allowed (except secret files), editing guard_rules.py asks the
user, and everything else is denied. Keep this file minimal and dependency-free.
"""

import contextlib
import io
import json
import os
import re
import sys

OUT = sys.stdout
RULES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard_rules.py")
SECRET_FILE = re.compile(r"(?<![\w.=-])\.env(?:\.(?!example\b)[\w.-]+)?(?![\w.-])", re.I)
SECRET_NAME = re.compile(r"\.env(\.(?!example$)[\w.-]+)?", re.I)
PATH_KEYS = ("file_path", "notebook_path", "path", "glob")


def decide(decision: str, reason: str):
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        ),
        file=OUT,
    )
    sys.exit(0)


def load_run():
    with open(RULES, encoding="utf-8") as source:
        code = compile(source.read(), RULES, "exec")
    namespace = {"__name__": "guard_rules", "__file__": RULES}
    # Anything the rules print or do to the streams while loading is discarded, so
    # the only output is the decision.
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        exec(code, namespace)
    return namespace["run"]


def cause_of(error: BaseException) -> str:
    try:
        line = getattr(error, "lineno", None)
        return type(error).__name__ + (f" at line {line}" if isinstance(line, int) else "")
    except Exception:
        return "unreadable error"


def same_file(path: str, other: str) -> bool:
    return os.path.normcase(os.path.realpath(path)) == os.path.normcase(os.path.realpath(other))


def judge_degraded(raw: str, cause: str, repair: str):
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        return "deny", f"The guard rules failed to load ({cause}) and the request is not an object. {repair}"
    tool, tool_input = payload.get("tool_name"), payload.get("tool_input")
    if not isinstance(tool, str) or not isinstance(tool_input, dict):
        return "deny", f"The guard rules failed to load ({cause}) and the request has unexpected types. {repair}"
    paths = [tool_input.get(key) for key in PATH_KEYS]
    if any(value is not None and not isinstance(value, str) for value in paths):
        return "deny", f"The guard rules failed to load ({cause}) and a path is not text. {repair}"
    if tool in ("Read", "Grep"):
        for value in filter(None, paths):
            name = re.split(r"[\\/]", value.rstrip("\\/"))[-1]
            if SECRET_NAME.fullmatch(name) or SECRET_FILE.search(value):
                return "deny", f"{tool} on .env is not allowed: secrets stay out of the session."
        return "allow", ""
    if tool in ("Edit", "Write") and paths[0] and same_file(paths[0], RULES):
        return "ask", f"The guard rules failed to load ({cause}); approve only an edit that repairs guard_rules.py."
    return (
        "deny",
        f"The guard rules failed to load ({cause}), so only reads, searches and edits of "
        f"guard_rules.py are allowed. {repair}",
    )


def degraded(raw: str, cause: str):
    repair = "Ask the user to run `git restore .claude/hooks/guard_rules.py` in their own terminal."
    try:
        decision, reason = judge_degraded(raw, cause, repair)
    except Exception:
        decision, reason = "deny", f"The guard rules failed to load ({cause}) and the request could not be read. {repair}"
    if decision == "allow":
        sys.exit(0)
    decide(decision, reason)


def main():
    raw = sys.stdin.read()
    try:
        run = load_run()
    except BaseException as error:
        degraded(raw, cause_of(error))
    try:
        run(raw)
    except SystemExit:
        raise
    except Exception as error:
        decide("ask", f"guard.py failed ({type(error).__name__}); confirm this action manually.")


main()
