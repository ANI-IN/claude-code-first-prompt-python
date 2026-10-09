"""Static checks on the page files: structure, wiring, and the hooks main.py relies on."""

import re
import subprocess

from tests.fake_browser import ROOT, parse_html

PYSCRIPT_VERSION = "2026.7.3"


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def test_page_loads_pyscript_and_main_py():
    html = read("index.html")
    assert f'https://pyscript.net/releases/{PYSCRIPT_VERSION}/core.js' in html
    assert f'https://pyscript.net/releases/{PYSCRIPT_VERSION}/core.css' in html
    assert '<script type="mpy" src="main.py"></script>' in html


PYTHON_ONLY = ("This project keeps all page behavior in Python: put new browser logic in main.py "
               "(or another .py file loaded with <script type=\"mpy\">) instead of a {what}.")


def project_files():
    """Files committed to the repository, or every project file outside git."""
    try:
        listed = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
        return [ROOT / line for line in listed.stdout.splitlines()]
    except (OSError, subprocess.CalledProcessError):
        skip = {".venv", "venv", ".git", "__pycache__", ".pytest_cache"}
        return [p for p in ROOT.rglob("*") if p.is_file() and not skip & set(p.relative_to(ROOT).parts)]


def test_page_has_no_inline_or_local_browser_scripts():
    doc = parse_html(read("index.html"))
    for script in doc.querySelectorAll("script"):
        src = script.getAttribute("src") or ""
        assert script.getAttribute("type") in ("module", "mpy"), PYTHON_ONLY.format(what=f"script tag {script}")
        assert src.startswith("https://pyscript.net/") or src.endswith(".py"), PYTHON_ONLY.format(what=f"script {src!r}")
        assert script.textContent.strip() == "", PYTHON_ONLY.format(what="inline script")


def test_repository_contains_python_source_only():
    browser_scripts = [p.name for p in project_files() if p.suffix in {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}]
    assert browser_scripts == [], PYTHON_ONLY.format(what=f"separate script file ({', '.join(browser_scripts)})")
    assert not (ROOT / "package.json").exists()


def test_every_element_main_py_uses_exists():
    doc = parse_html(read("index.html"))
    for element_id in ("nav-toggle", "primary-nav", "billing-switch", "year"):
        assert doc.getElementById(element_id) is not None, element_id
    assert doc.querySelector(".site-header") is not None
    assert doc.querySelectorAll(".reveal").length > 0
    assert doc.getElementById("primary-nav").querySelectorAll("a").length > 0


def test_every_price_has_monthly_and_annual_values():
    doc = parse_html(read("index.html"))
    values = doc.querySelectorAll(".price__value")
    assert values.length == 3
    for el in values:
        assert el.getAttribute("data-monthly").isdigit()
        assert el.getAttribute("data-annual").isdigit()
        assert el.textContent == el.getAttribute("data-monthly")


def test_controls_have_accessible_state():
    doc = parse_html(read("index.html"))
    toggle = doc.getElementById("nav-toggle")
    assert toggle.getAttribute("aria-controls") == "primary-nav"
    assert toggle.getAttribute("aria-expanded") == "false"
    switch = doc.getElementById("billing-switch")
    assert switch.getAttribute("role") == "switch"
    assert switch.getAttribute("aria-checked") == "false"


def test_css_defines_the_states_main_py_toggles():
    css = read("styles.css")
    for selector in (".site-header.is-scrolled", ".nav.is-open", ".reveal.is-visible",
                     '.switch[aria-checked="true"]', '.nav-toggle[aria-expanded="true"]'):
        assert selector in css, selector


def test_intentional_dark_mode_marker_is_kept():
    first_lines = read("styles.css").splitlines()[:4]
    assert "Light theme only (dark mode intentionally not implemented yet)." in first_lines[2], (
        "The comment at the top of styles.css is an intentional marker for the exercises. "
        "Restore it: Exercise 3 asks you to notice it, not to change it."
    )


def test_design_tokens_live_in_root():
    css = read("styles.css")
    root_block = re.search(r":root\s*{(.*?)}", css, re.S).group(1)
    for token in ("--color-primary", "--color-bg", "--color-text", "--color-surface", "--color-accent-text"):
        assert token + ":" in root_block, token
