"""Behavior tests for the dark mode toggle in main.py."""

import re

import pytest

from tests.fake_browser import ROOT, load_page, parse_html

KEY = "flowstate-theme"


def theme(page):
    return page.document.documentElement.getAttribute("data-theme")


def test_defaults_to_light_theme():
    page = load_page()
    toggle = page.by_id("theme-toggle")
    assert theme(page) == "light"
    assert toggle.getAttribute("aria-pressed") == "false"
    assert toggle.getAttribute("aria-label") == "Switch to dark theme"


def test_follows_system_preference_when_nothing_is_saved():
    page = load_page(prefers_dark=True)
    assert theme(page) == "dark"
    assert page.by_id("theme-toggle").getAttribute("aria-pressed") == "true"


@pytest.mark.parametrize("saved, prefers_dark", [("dark", False), ("light", True)])
def test_saved_choice_wins_over_system_preference(saved, prefers_dark):
    page = load_page(local_storage={KEY: saved}, prefers_dark=prefers_dark)
    assert theme(page) == saved


def test_invalid_saved_value_is_ignored():
    page = load_page(local_storage={KEY: "purple"}, prefers_dark=True)
    assert theme(page) == "dark"


def test_toggle_switches_theme_and_saves_choice():
    page = load_page()
    toggle = page.by_id("theme-toggle")

    toggle.click()
    assert theme(page) == "dark"
    assert page.window.localStorage.getItem(KEY) == "dark"
    assert toggle.getAttribute("aria-pressed") == "true"
    assert toggle.getAttribute("aria-label") == "Switch to light theme"

    toggle.click()
    assert theme(page) == "light"
    assert page.window.localStorage.getItem(KEY) == "light"
    assert toggle.getAttribute("aria-pressed") == "false"


def test_saved_choice_survives_a_reload():
    first_visit = load_page()
    first_visit.by_id("theme-toggle").click()

    second_visit = load_page(local_storage=first_visit.window.localStorage.items)
    assert theme(second_visit) == "dark"


def test_tracks_live_system_changes_until_user_chooses():
    page = load_page()
    media = page.window.matchMedia("(prefers-color-scheme: dark)")

    media.change(True)
    assert theme(page) == "dark"
    media.change(False)
    assert theme(page) == "light"

    page.by_id("theme-toggle").click()  # explicit choice: dark
    media.change(False)
    assert theme(page) == "dark"


def test_storage_errors_do_not_break_the_toggle():
    page = load_page()

    def blocked(*args):
        raise RuntimeError("storage disabled")

    page.window.localStorage.getItem = blocked
    page.window.localStorage.setItem = blocked
    page.by_id("theme-toggle").click()
    assert theme(page) == "dark"


def test_blocked_storage_on_load_falls_back_to_system_theme():
    page = load_page(storage_blocked=True, prefers_dark=True)
    assert theme(page) == "dark"

    page.by_id("theme-toggle").click()  # cannot be saved, but still applies
    assert theme(page) == "light"


def test_works_without_match_media():
    page = load_page(match_media=False)
    assert theme(page) == "light"
    page.by_id("theme-toggle").click()
    assert theme(page) == "dark"


def test_uses_older_listener_api_when_needed():
    page = load_page(legacy_media_listeners=True)
    media = page.window.matchMedia("(prefers-color-scheme: dark)")
    assert not hasattr(media, "addEventListener")

    media.change(True)
    assert theme(page) == "dark"


def test_theme_applies_even_without_a_toggle_button():
    page = load_page(html="<main><p>No header here.</p></main>", prefers_dark=True)
    assert theme(page) == "dark"


# ---------- Markup and styles ----------
def test_toggle_lives_in_the_header():
    doc = parse_html((ROOT / "index.html").read_text(encoding="utf-8"))
    header = doc.querySelector(".site-header")
    toggle = header.querySelector("#theme-toggle")
    assert toggle is not None
    assert toggle.getAttribute("type") == "button"
    assert toggle.querySelector(".theme-toggle__icon--sun") is not None
    assert toggle.querySelector(".theme-toggle__icon--moon") is not None


def test_dark_theme_redefines_every_color_token():
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    root_tokens = set(re.findall(r"(--color-[\w-]+):", re.search(r":root\s*{(.*?)}", css, re.S).group(1)))
    dark_tokens = set(re.findall(r"(--color-[\w-]+):", re.search(r'\[data-theme="dark"\]\s*{(.*?)}', css, re.S).group(1)))
    assert root_tokens and root_tokens <= dark_tokens


def test_theme_transitions_respect_reduced_motion():
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    assert "transition: background-color 0.3s ease" in css
    reduced = css[css.index("@media (prefers-reduced-motion: reduce)"):]
    assert "transition-duration: 0.001ms !important" in reduced
