"""Behavior tests for main.py, run against the real index.html markup."""

import datetime

import pytest

from tests.fake_browser import IntersectionObserver, load_page


@pytest.fixture
def page():
    return load_page()


# ---------- Mobile navigation ----------
def test_nav_toggle_opens_and_closes_menu(page):
    nav, toggle = page.by_id("primary-nav"), page.by_id("nav-toggle")
    assert not nav.classList.contains("is-open")

    toggle.click()
    assert nav.classList.contains("is-open")
    assert toggle.getAttribute("aria-expanded") == "true"

    toggle.click()
    assert not nav.classList.contains("is-open")
    assert toggle.getAttribute("aria-expanded") == "false"


def test_tapping_a_nav_link_closes_menu(page):
    nav, toggle = page.by_id("primary-nav"), page.by_id("nav-toggle")
    links = nav.querySelectorAll("a")
    assert links.length >= 1

    for link in links:
        toggle.click()
        link.click()
        assert not nav.classList.contains("is-open")
        assert toggle.getAttribute("aria-expanded") == "false"


def test_escape_closes_menu_but_other_keys_do_not(page):
    nav, toggle = page.by_id("primary-nav"), page.by_id("nav-toggle")
    toggle.click()

    page.press(page.document, "a")
    assert nav.classList.contains("is-open")

    page.press(page.document, "Escape")
    assert not nav.classList.contains("is-open")


@pytest.mark.parametrize("width, stays_open", [(1024, False), (769, False), (768, True), (400, True)])
def test_resizing_to_desktop_resets_menu(page, width, stays_open):
    nav = page.by_id("primary-nav")
    page.by_id("nav-toggle").click()

    page.window.innerWidth = width
    page.window.dispatch("resize")
    assert nav.classList.contains("is-open") is stays_open


# ---------- Header shadow on scroll ----------
def test_header_state_follows_scroll_position(page):
    header = page.document.querySelector(".site-header")
    assert not header.classList.contains("is-scrolled")

    page.window.scrollY = 8
    page.window.dispatch("scroll")
    assert not header.classList.contains("is-scrolled")

    page.window.scrollY = 9
    page.window.dispatch("scroll")
    assert header.classList.contains("is-scrolled")

    page.window.scrollY = 0
    page.window.dispatch("scroll")
    assert not header.classList.contains("is-scrolled")


def test_header_state_is_correct_on_load_when_already_scrolled():
    page = load_page(scroll_y=500)
    assert page.document.querySelector(".site-header").classList.contains("is-scrolled")


def test_scroll_listener_is_passive(page):
    assert page.window.listener_options["scroll"] == [{"passive": True}]


# ---------- Scroll reveal ----------
def test_reveal_observes_every_reveal_element(page):
    (observer,) = IntersectionObserver.instances
    reveal = page.all(".reveal")
    assert reveal.length > 0
    assert observer.observed == list(reveal)
    assert observer.options == {"threshold": 0.12, "rootMargin": "0px 0px -40px 0px"}
    assert not any(el.classList.contains("is-visible") for el in reveal)


def test_reveal_shows_element_once_it_intersects(page):
    (observer,) = IntersectionObserver.instances
    first, second = page.all(".reveal")[:2]

    observer.trigger(second, is_intersecting=False)
    assert not second.classList.contains("is-visible")
    assert second in observer.observed

    observer.trigger(first)
    assert first.classList.contains("is-visible")
    assert first not in observer.observed


def test_reveal_falls_back_to_showing_everything_without_observer():
    page = load_page(intersection_observer=False)
    assert IntersectionObserver.instances == []
    assert all(el.classList.contains("is-visible") for el in page.all(".reveal"))


# ---------- Pricing billing toggle ----------
def prices(page):
    return [el.textContent for el in page.all(".price__value")]


def test_prices_start_monthly(page):
    assert page.by_id("billing-switch").getAttribute("aria-checked") == "false"
    assert prices(page) == ["0", "12", "24"]


def test_billing_switch_flips_between_monthly_and_annual(page):
    switch = page.by_id("billing-switch")

    switch.click()
    assert switch.getAttribute("aria-checked") == "true"
    assert prices(page) == ["0", "10", "20"]

    switch.click()
    assert switch.getAttribute("aria-checked") == "false"
    assert prices(page) == ["0", "12", "24"]


@pytest.mark.parametrize("key", [" ", "Enter"])
def test_billing_switch_is_keyboard_operable(page, key):
    switch = page.by_id("billing-switch")
    event = page.press(switch, key)
    assert event.default_prevented
    assert switch.getAttribute("aria-checked") == "true"
    assert prices(page) == ["0", "10", "20"]


def test_other_keys_do_not_toggle_billing(page):
    switch = page.by_id("billing-switch")
    event = page.press(switch, "Tab")
    assert not event.default_prevented
    assert switch.getAttribute("aria-checked") == "false"


def test_price_without_data_values_is_left_alone():
    html = """
    <button id="billing-switch" aria-checked="false"></button>
    <span class="price__value" data-monthly="5" data-annual="4">5</span>
    <span class="price__value">Custom</span>
    """
    page = load_page(html=html)
    page.by_id("billing-switch").click()
    assert prices(page) == ["4", "Custom"]


# ---------- Footer year ----------
def test_footer_shows_current_year():
    html = '<footer><p>&copy; <span id="year">1999</span> FlowState</p></footer>'
    page = load_page(html=html)
    assert page.by_id("year").textContent == str(datetime.date.today().year)


# ---------- Python-running marker ----------
def test_marks_page_as_python_ready(page):
    assert page.document.documentElement.classList.contains("py-ready")


# ---------- Robustness ----------
def test_script_runs_on_a_page_without_any_widgets():
    page = load_page(html="<main><p>Nothing interactive here.</p></main>")
    assert page.window.listeners == {}
