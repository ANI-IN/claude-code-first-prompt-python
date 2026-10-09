"""End-to-end tests: serve the page, open it in headless Chromium, and use it.

These run main.py for real through PyScript. They are skipped automatically
when Playwright or its Chromium build is not installed, or when the PyScript
runtime cannot be downloaded (for example, when you are offline).

    pip install -r requirements.txt
    python -m playwright install chromium
    pytest -m browser
"""

import datetime
import re
import threading
import urllib.request

import pytest

from serve import make_server
from tests.fake_browser import ROOT
from tests.test_page import PYSCRIPT_VERSION

sync_api = pytest.importorskip("playwright.sync_api", reason="Playwright is not installed")

expect = sync_api.expect

pytestmark = pytest.mark.browser

PYTHON_READY_TIMEOUT_MS = 30_000


@pytest.fixture(scope="module")
def base_url():
    try:
        probe = urllib.request.Request(f"https://pyscript.net/releases/{PYSCRIPT_VERSION}/core.js",
                                       method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        urllib.request.urlopen(probe, timeout=10).close()
    except OSError as exc:
        pytest.skip(f"PyScript runtime unreachable ({exc}); browser tests need internet access")
    server = make_server(port=0, quiet=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()
    server.server_close()


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except sync_api.Error as exc:
            pytest.skip(f"Chromium is not available ({exc.message.splitlines()[0]}); "
                        "run: python -m playwright install chromium")
        yield browser
        browser.close()


@pytest.fixture
def open_page(browser, base_url):
    """Open the page in a fresh browser context and wait until main.py has run."""
    contexts = []

    def _open(**context_options):
        context = browser.new_context(**context_options)
        contexts.append(context)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: msg.type == "error" and errors.append(msg.text))
        page.errors = errors
        page.goto(base_url)
        wait_for_python(page)
        return page

    yield _open
    for context in contexts:
        context.close()


def wait_for_python(page):
    # The first .reveal element is in view on load, so main.py marks it visible.
    page.wait_for_selector(".reveal.is-visible", state="attached", timeout=PYTHON_READY_TIMEOUT_MS)


def prices(page):
    return page.locator(".price__value").all_text_contents()


def test_page_runs_python_without_errors(open_page):
    page = open_page()
    assert page.title() == "FlowState — Project management that flows"
    assert page.text_content("#year") == str(datetime.date.today().year)
    assert page.errors == []


def test_served_page_hides_the_no_python_notice(open_page):
    page = open_page()
    expect(page.locator("html")).to_have_class(re.compile(r"\bpy-ready\b"))
    page.wait_for_timeout(4_500)  # past the moment the notice would appear
    expect(page.locator(".py-notice")).to_be_hidden()


def test_page_opened_as_a_file_still_shows_content_and_explains_why(browser, base_url):
    # Browsers do not let a page opened from disk fetch main.py, so Python cannot start.
    page = browser.new_page()
    page.goto((ROOT / "index.html").as_uri())
    notice = page.locator(".py-notice")
    expect(notice).to_be_visible(timeout=10_000)
    expect(notice).to_contain_text("python3 serve.py")
    expect(page.locator(".hero__copy")).to_have_css("opacity", "1")
    expect(page.locator("html")).not_to_have_class(re.compile(r"\bpy-ready\b"))
    page.close()


def test_billing_toggle_by_mouse_and_keyboard(open_page):
    page = open_page()
    switch = page.locator("#billing-switch")
    assert prices(page) == ["0", "12", "24"]

    switch.click()
    assert switch.get_attribute("aria-checked") == "true"
    assert prices(page) == ["0", "10", "20"]

    switch.focus()
    page.keyboard.press("Enter")
    assert prices(page) == ["0", "12", "24"]

    page.keyboard.press("Space")
    assert prices(page) == ["0", "10", "20"]


def test_mobile_menu(open_page):
    page = open_page(viewport={"width": 400, "height": 800})
    nav, toggle = page.locator("#primary-nav"), page.locator("#nav-toggle")
    # The closed menu slides out of view and fades to transparent.
    expect(toggle).to_be_visible()
    expect(nav).to_have_css("opacity", "0")

    toggle.click()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(nav).to_have_class(re.compile(r"\bis-open\b"))
    expect(nav).to_have_css("opacity", "1")

    page.keyboard.press("Escape")
    expect(toggle).to_have_attribute("aria-expanded", "false")
    expect(nav).to_have_css("opacity", "0")

    toggle.click()
    nav.locator("a", has_text="Pricing").click()
    expect(nav).not_to_have_class(re.compile(r"\bis-open\b"))

    toggle.click()
    page.set_viewport_size({"width": 1200, "height": 800})
    expect(nav).not_to_have_class(re.compile(r"\bis-open\b"))
    expect(toggle).to_have_attribute("aria-expanded", "false")


def test_header_shadow_and_scroll_reveal(open_page):
    page = open_page()
    header = page.locator(".site-header")
    last_card = page.locator("#pricing .price").last
    expect(header).not_to_have_class(re.compile(r"\bis-scrolled\b"))
    expect(last_card).not_to_have_class(re.compile(r"\bis-visible\b"))

    last_card.scroll_into_view_if_needed()
    expect(header).to_have_class(re.compile(r"\bis-scrolled\b"))
    expect(last_card).to_have_class(re.compile(r"\bis-visible\b"))

    page.locator("#top .brand").focus()
    page.keyboard.press("Home")
    page.mouse.wheel(0, -100_000)
    expect(header).not_to_have_class(re.compile(r"\bis-scrolled\b"))
