"""PreToolUse guard rules: block or ask before risky actions that permission rules miss.

guard.py loads this file and calls run(); settings.json only knows guard.py.

Permission rules in settings.json only match the start of a command, so
`cd x && git push` or `gh repo create --push` slip past them. This hook looks
at the whole command and at file paths. It stops mistakes, not deliberate
obfuscation (git aliases, variables, quoted command names).
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ENV_FILE = re.compile(r"(?<![\w.=-])\.env(?:\.(?!example\b)[\w.-]+)?(?![\w.-])", re.I)
ENV_NAME = re.compile(r"\.env(\.(?!example$)[\w.-]+)?", re.I)
READERS = re.compile(
    r"(?i)(?<![\w-])(cat|type|more|less|head|tail|nl|gc|get-content|grep|egrep|rg|"
    r"findstr|select-string|sed|awk|strings|od|xxd|base64|cp|copy|copy-item|mv|"
    r"move|move-item|scp|curl|source)(?![\w-])|(?<![<\w])<(?![<&(])|(?<!\S)\.\s"
)
CONFIG_PATH = re.compile(r"\.claude[\\/](settings(\.local)?\.json|hooks[\\/])", re.I)
HOOK_SOURCE = re.compile(r"\.claude[\\/]hooks[\\/]guard(_rules)?\.py$", re.I)
WRITERS = re.compile(
    r"(?i)(?<![0-9&>])>(?!&)|(?<![\w-])(set-content|add-content|out-file|tee|tee-object|"
    r"cp|copy|copy-item|mv|move|move-item|rm|del|remove-item)(?![\w-])|\bsed\s+-i"
)
EMAIL = re.compile(r"[\w.%+-]+@([\w-]+(?:\.[\w-]+)*\.[a-z]{2,})", re.I)
ALLOWED_EMAIL_DOMAINS = {"example.com"}
PROTECTED_STAGED = re.compile(r"(^|/)(\.env(\.(?!example$)[^/]+)?$)|^(recordings|evidencias)/", re.I)
SEGMENT_END = r"[^;&|\n]*"

# Options that make pytest print the test password or that change what it loads.
# Safe `--tb` styles were checked with a probe (an invented password as a function
# argument and as a local variable): `auto` and `long` print the arguments; `short`,
# `line`, `native` and `no` do not. Short flags that take no value can be bundled
# before `-o` and `-c` (`-vc`).
NO_VALUE_FLAGS = "vqxslhV"
LEAKY = "|".join(
    [
        r"--showlocals",
        r"(?<![\w-])--tb(?![\w-])(?!(?:=|\s+)(?:short|line|native|no)(?![\w-]))",
        r"--full-?trace",
        r"--tracing[= ]+(on|retain)",
        r"(?<![^\s=])-[a-zA-Z]*l[a-zA-Z]*(?![^\s;&|])",
        rf"(?<![^\s=])-[{NO_VALUE_FLAGS}]*o(?:\s+|(?=\S))\S*addopts",
        r"--over[\w-]*[=\s]\s*\S*addopts",
        rf"(?<![^\s=])-[{NO_VALUE_FLAGS}]*c",
        r"--conf[\w-]*",
        r"--noc[\w-]*",
    ]
)
DEBUG_ASSIGNMENT = re.compile(r"(?i)(?:(?<![\w.-])|(?<=\s-e))DEBUG\s*=\s*\S*(?:pw:|\*)")
PYTEST_MENTION = re.compile(r"\bpytest\b|\btoolshop[:-]")


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
        )
    )
    sys.exit(0)


def drop_heredocs(command: str) -> str:
    command = re.sub(
        r"<<-?\s*(['\"]?)(\w+)\1.*?^\s*\2\s*$", "", command, flags=re.S | re.M
    )
    return re.sub(r"@'.*?^'@", "", command, flags=re.S | re.M)


def resulting_source(tool: str, tool_input: dict, path: str):
    """Text the file would hold after the edit, or None when it cannot be known.

    When Edit cannot apply (text missing or ambiguous) the tool itself fails, so
    there is nothing to check.
    """
    if tool == "Write":
        return tool_input.get("content")
    old = (tool_input.get("old_string") or "").replace("\r\n", "\n")
    new = (tool_input.get("new_string") or "").replace("\r\n", "\n")
    try:
        current = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    occurrences = current.count(old) if old else 0
    if occurrences == 0 or (occurrences > 1 and not tool_input.get("replace_all")):
        return None
    return current.replace(old, new)


def check_hook_edit(tool: str, tool_input: dict, path: str):
    source = resulting_source(tool, tool_input, path)
    if source is None:
        return
    try:
        compile(source, path, "exec")
    except (SyntaxError, ValueError) as error:
        where = f" at line {error.lineno}" if getattr(error, "lineno", None) else ""
        decide(
            "deny",
            f"This {tool} would leave {Path(path).name} with a {type(error).__name__}{where}; "
            "the file stays unchanged. Fix the new text and try again.",
        )


def check_file_tool(tool: str, tool_input: dict):
    paths = [tool_input.get(key) or "" for key in ("file_path", "notebook_path", "path", "glob")]
    for path in filter(None, paths):
        name = re.split(r"[\\/]", path.rstrip("\\/"))[-1]
        if ENV_NAME.fullmatch(name) or ENV_FILE.search(path):
            decide("deny", f"{tool} on .env is not allowed: secrets stay out of the session.")
    if tool in ("Edit", "Write", "NotebookEdit") and CONFIG_PATH.search(paths[0] or paths[1]):
        if tool in ("Edit", "Write") and HOOK_SOURCE.search(paths[0]):
            check_hook_edit(tool, tool_input, paths[0])
        decide("ask", "Changing permissions or hooks needs the user's approval.")


def git(cwd: str, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=cwd or None, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        decide("ask", f"Could not inspect the commit (git {args[0]} failed); review it manually.")
    return result.stdout


def check_commit(code: str, cwd: str):
    if re.search(r"(^|[;&|(\s])cd\s|\bgit\s+-C\b", code):
        decide("ask", "Commit runs in another folder; the guard cannot inspect it.")
    stages_all = re.search(
        r"\bgit\b" + SEGMENT_END + r"\b(add|stage)\b|\bcommit\b" + SEGMENT_END + r"((?<!\S)-\w*a\w*|--all\b)",
        code,
    )
    diff = ["diff", "--no-ext-diff", "--no-color"]
    if stages_all:
        names = git(cwd, *diff, "HEAD", "--name-only").splitlines()
        untracked = git(cwd, "ls-files", "--others", "--exclude-standard").splitlines()
        names += untracked
        added = git(cwd, *diff, "HEAD", "-U0")
        for path in untracked:
            try:
                with open(f"{cwd}/{path}" if cwd else path, encoding="utf-8") as fh:
                    added += "\n+" + fh.read().replace("\n", "\n+")
            except (OSError, UnicodeDecodeError):
                pass
    else:
        names = git(cwd, *diff, "--cached", "--name-only").splitlines()
        added = git(cwd, *diff, "--cached", "-U0")

    blocked = [n for n in names if PROTECTED_STAGED.search(n)]
    if blocked:
        decide("deny", f"Commit would include protected files: {', '.join(blocked)}.")

    added_lines = [l[1:] for l in added.splitlines() if l.startswith("+") and not l.startswith("+++")]
    domains = {m.lower() for line in added_lines for m in EMAIL.findall(line)}
    if domains - ALLOWED_EMAIL_DOMAINS:
        decide("deny", "Commit adds a real-looking email address; test data must use @example.com.")


def check_command(command: str, cwd: str):
    bodyless = drop_heredocs(command)
    unquoted = bodyless.replace('"', "").replace("'", "")
    code = re.sub(r"\"(?:\\.|[^\"\\])*\"|'[^']*'", "''", bodyless)

    if ENV_FILE.search(unquoted) and READERS.search(unquoted):
        decide("deny", "Reading or copying .env is not allowed: secrets stay out of the session.")

    if CONFIG_PATH.search(unquoted) and WRITERS.search(unquoted):
        decide("ask", "Changing permissions or hooks needs the user's approval.")

    joined = re.sub(r"[\\`]\r?\n\s*", " ", bodyless)
    # A separator inside quotes would cut the segment before the leaky option, so it is
    # flattened to a space; after a shell -c the quoted text is a script, so newlines too.
    joined = re.sub(
        r"((?<!\S)-\w*c\s+)?(\"(?:\\.|[^\"\\])*\"|'[^']*')",
        lambda m: (m.group(1) or "") + re.sub(r"[;&|\r\n]" if m.group(1) else r"[;&|]", " ", m.group(2)),
        joined,
    )
    joined = joined.replace('"', "").replace("'", "")

    pytest_msg = "These pytest options can print the test password or skip its protections; use the default traceback and config."
    for segment in re.findall(r"(?:\bpytest\b|\btoolshop:)" + SEGMENT_END, joined):
        if re.search(LEAKY, segment):
            decide("deny", pytest_msg)
    if re.search(r"PYTEST_ADDOPTS\s*=" + SEGMENT_END + "(" + LEAKY + ")", unquoted):
        decide("deny", pytest_msg)
    if DEBUG_ASSIGNMENT.search(joined) and PYTEST_MENTION.search(joined):
        decide("deny", "DEBUG=pw:* makes Playwright log the typed values; leave DEBUG unset.")

    password_msg = "This Docker command could print the test password; use the toolshop:docker script."
    for segment in re.findall(r"\bdocker\b" + SEGMENT_END, joined):
        _, image, after_image = segment.partition("toolshop-qa")
        if image and re.search(r"\brun\b", segment) and re.search(LEAKY, after_image):
            decide("deny", password_msg)
        if re.search(r"--entrypoint[= ]\s*(\S*/)?(env|printenv)(?![\w.-])", segment):
            decide("deny", password_msg)
        if re.search(r"\bdocker(\.exe)?\s+(-\S+\s+((?!-|network\b|volume\b)\S+\s+)?)*((container|image)\s+)?inspect\b", segment):
            decide("deny", password_msg)
        if re.search(r"\bexec\b" + SEGMENT_END + r"(?<![\w.-])(env|printenv)(?![\w.-])", segment):
            decide("deny", password_msg)

    if re.search(r"\bgit\b" + SEGMENT_END + r"\bpush\b" + SEGMENT_END + r"(--force\b|--force-with-lease|(?<!\S)-f\b|(?<!\S)\+\S)", code):
        decide("deny", "Force push rewrites remote history.")
    if re.search(
        r"\bgit\b" + SEGMENT_END + r"(\breset\s+--hard|(?<![.\w-])rebase\b|filter-branch|\bcommit\b"
        + SEGMENT_END + r"--amend|\bclean\b" + SEGMENT_END + r"((?<!\S)-\w*f|--force))",
        code,
    ):
        decide("deny", "This rewrites history or discards work; ask the user to do it.")
    if re.search(
        r"(?i)(?<![\w-])(rm|rmdir|rd|ri|del|erase|remove-item)\b" + SEGMENT_END
        + r"((?<!\S)-(r[fv]*|[fv]+r[fv]*|rec\w*)(?!\S)|--recursive)",
        code,
    ):
        decide("deny", "Recursive delete is not allowed.")
    if re.search(r"\bgit\b" + SEGMENT_END + r"\b(add|stage)\b" + SEGMENT_END + r"((?<!\S)-\w*f\w*|--force\b)", code):
        decide("deny", "Forcing git add would stage ignored files such as .env.")

    if re.search(r"\bgit\b" + SEGMENT_END + r"\bcommit\b", code):
        check_commit(code, cwd)

    if re.search(r"\bgit\b" + SEGMENT_END + r"\bpush\b", code) or re.search(
        r"\bgh\b" + SEGMENT_END + r"(--push\b|\bpr\s+(create|merge)\b|\brelease\b|"
        r"\brepo\s+(create|delete|edit|rename)\b|\bapi\b" + SEGMENT_END
        + r"((?<!\S)-[XfF]\b|--method|--field|--raw-field|--input))",
        code,
    ):
        decide("ask", "Publishing to GitHub needs the user's approval.")


def main(payload: dict):
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    if tool in ("Bash", "PowerShell"):
        check_command(tool_input.get("command", ""), payload.get("cwd", ""))
    elif tool in ("Read", "Grep", "Edit", "Write", "NotebookEdit"):
        check_file_tool(tool, tool_input)


def run(raw: str):
    try:
        main(json.loads(raw))
    except SystemExit:
        raise
    except Exception as error:  # a broken guard must not silently allow risky actions
        decide("ask", f"guard_rules.py failed ({type(error).__name__}); confirm this action manually.")
