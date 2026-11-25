"""PreToolUse guard: blocks or asks before risky actions that permission rules miss.

Permission rules in settings.json only match the start of a command, so
`cd x && git push` or `gh repo create --push` slip past them. This hook looks
at the whole command and at file paths. It stops mistakes, not deliberate
obfuscation (git aliases, variables, quoted command names).
"""

import json
import re
import subprocess
import sys

ENV_FILE = re.compile(r"(?<![\w.=-])\.env(?:\.(?!example\b)[\w.-]+)?(?![\w.-])", re.I)
ENV_NAME = re.compile(r"\.env(\.(?!example$)[\w.-]+)?", re.I)
READERS = re.compile(
    r"(?i)(?<![\w-])(cat|type|more|less|head|tail|nl|gc|get-content|grep|egrep|rg|"
    r"findstr|select-string|sed|awk|strings|od|xxd|base64|cp|copy|copy-item|mv|"
    r"move|move-item|scp|curl|source)(?![\w-])|(?<![<\w])<(?![<&(])|(?<!\S)\.\s"
)
CONFIG_PATH = re.compile(r"\.claude[\\/](settings(\.local)?\.json|hooks[\\/])", re.I)
WRITERS = re.compile(
    r"(?i)(?<![0-9&>])>(?!&)|(?<![\w-])(set-content|add-content|out-file|tee|tee-object|"
    r"cp|copy|copy-item|mv|move|move-item|rm|del|remove-item)(?![\w-])|\bsed\s+-i"
)
EMAIL = re.compile(r"[\w.%+-]+@([\w-]+(?:\.[\w-]+)*\.[a-z]{2,})", re.I)
ALLOWED_EMAIL_DOMAINS = {"example.com"}
PROTECTED_STAGED = re.compile(r"(^|/)(\.env(\.(?!example$)[^/]+)?$)|^(recordings|evidencias)/", re.I)
SEGMENT_END = r"[^;&|\n]*"


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


def check_file_tool(tool: str, tool_input: dict):
    paths = [tool_input.get(key) or "" for key in ("file_path", "notebook_path", "path", "glob")]
    for path in filter(None, paths):
        name = re.split(r"[\\/]", path.rstrip("\\/"))[-1]
        if ENV_NAME.fullmatch(name) or ENV_FILE.search(path):
            decide("deny", f"{tool} on .env is not allowed: secrets stay out of the session.")
    if tool in ("Edit", "Write", "NotebookEdit") and CONFIG_PATH.search(paths[0] or paths[1]):
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

    leaky = r"--showlocals|--tb[= ]+long|--full-?trace|--tracing[= ]+(on|retain)|(?<![^\s=])-[a-zA-Z]*l[a-zA-Z]*(?![^\s;&|])"
    for segment in re.findall(r"(?:\bpytest\b|\btoolshop:)" + SEGMENT_END, joined):
        if re.search(leaky, segment):
            decide("deny", "These pytest options print the test password; use the default traceback.")
    if re.search(r"PYTEST_ADDOPTS\s*=" + SEGMENT_END + "(" + leaky + ")", unquoted):
        decide("deny", "These pytest options print the test password; use the default traceback.")

    password_msg = "This Docker command could print the test password; use the toolshop:docker script."
    for segment in re.findall(r"\bdocker\b" + SEGMENT_END, joined):
        _, image, after_image = segment.partition("toolshop-qa")
        if image and re.search(r"\brun\b", segment) and re.search(leaky, after_image):
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


def main():
    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    if tool in ("Bash", "PowerShell"):
        check_command(tool_input.get("command", ""), payload.get("cwd", ""))
    elif tool in ("Read", "Grep", "Edit", "Write", "NotebookEdit"):
        check_file_tool(tool, tool_input)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:  # a broken guard must not silently allow risky actions
        decide("ask", f"guard.py failed ({type(error).__name__}); confirm this action manually.")
