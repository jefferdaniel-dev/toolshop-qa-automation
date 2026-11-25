"""Build the single-file Allure report of the latest run in reports/."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
# Allure only offers light, dark and auto: the report is forced to dark and the
# Tokyo Night palette overrides the dark variables.
FORCE_DARK = "<script>localStorage.setItem('theme','dark')</script>"
# Allure embeds Google Analytics in every report; the report must not call out.
ANALYTICS = [
    re.compile(r"<script[^>]*googletagmanager[^>]*></script>"),
    re.compile(r"<script>(?:(?!</script>).)*?gtag\((?:(?!</script>).)*?</script>", re.DOTALL),
]


def latest_run() -> Path:
    runs = sorted(
        p for p in REPORTS.glob("*") if any((p / "resultados").glob("*-result.json"))
    )
    if not runs:
        sys.exit("No hay resultados en reports/. Corre primero una prueba.")
    return runs[-1]


def main():
    run = latest_run()
    node = shutil.which("node")
    if not node:
        sys.exit("Node no está en el PATH.")
    # Relative paths and no shell: the project path has spaces and a tilde.
    results = (run / "resultados").relative_to(ROOT)
    output = (run / "informe").relative_to(ROOT)
    subprocess.run(
        [
            node, "node_modules/allure/cli.js", "awesome", str(results),
            "--single-file", "-o", str(output),
            "--name", "Toolshop QA", "--lang", "es",
        ],
        cwd=ROOT,
        check=True,
    )
    index = ROOT / output / "index.html"
    css = (Path(__file__).parent / "tokyo-night.css").read_text(encoding="utf-8")
    html = index.read_text(encoding="utf-8")
    for pattern in ANALYTICS:
        html = pattern.sub("", html)
    if "googletagmanager" in html:
        index.unlink()
        sys.exit("El HTML conserva analítica de Google; se borró index.html.")
    html = html.replace("<head>", f"<head>{FORCE_DARK}", 1)
    html = html.replace("</head>", f"<style>{css}</style></head>", 1)
    index.write_text(html, encoding="utf-8")
    print(index)


main()
