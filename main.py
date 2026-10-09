# =================================================================
# FlowState — Landing page interactions (Python in the browser via PyScript)
# =================================================================
# PyScript runs this file after the page's HTML has loaded, so every element
# below already exists when main() wires it up.
import js
from pyscript.ffi import create_proxy, to_js

document = js.document
window = js.window


def main():
    # Tell the stylesheet that Python is running (turns off the no-Python fallback).
    document.documentElement.classList.add("py-ready")
    init_mobile_nav()
    init_header_scroll_state()
    init_scroll_reveal()
    init_billing_toggle()
    init_footer_year()


def js_bool(value):
    """Format a Python bool the way HTML attributes expect ("true"/"false")."""
    return "true" if value else "false"


def on(target, event_name, handler, options=None):
    """Attach a Python function as a browser event listener."""
    if options is None:
        target.addEventListener(event_name, create_proxy(handler))
    else:
        target.addEventListener(event_name, create_proxy(handler), to_js(options))


# ---------- Mobile navigation ----------
def init_mobile_nav():
    toggle = document.getElementById("nav-toggle")
    nav = document.getElementById("primary-nav")
    if toggle is None or nav is None:
        return

    def set_open(is_open):
        nav.classList.toggle("is-open", is_open)
        toggle.setAttribute("aria-expanded", js_bool(is_open))

    def on_toggle_click(event):
        is_open = nav.classList.contains("is-open")
        set_open(not is_open)

    on(toggle, "click", on_toggle_click)

    # Close the menu after tapping a link.
    for link in nav.querySelectorAll("a"):
        on(link, "click", lambda event: set_open(False))

    # Close on Escape for keyboard users.
    def on_keydown(event):
        if event.key == "Escape":
            set_open(False)

    on(document, "keydown", on_keydown)

    # Reset state when resizing back up to desktop.
    def on_resize(event):
        if window.innerWidth > 768:
            set_open(False)

    on(window, "resize", on_resize)


# ---------- Header shadow on scroll ----------
def init_header_scroll_state():
    header = document.querySelector(".site-header")
    if header is None:
        return

    def update(event=None):
        header.classList.toggle("is-scrolled", window.scrollY > 8)

    update()
    on(window, "scroll", update, {"passive": True})


# ---------- Scroll reveal via IntersectionObserver ----------
def init_scroll_reveal():
    items = document.querySelectorAll(".reveal")
    if not items.length:
        return

    # Fallback: if IntersectionObserver is unavailable, just show everything.
    if not hasattr(window, "IntersectionObserver"):
        for el in items:
            el.classList.add("is-visible")
        return

    def on_intersect(entries, observer):
        for entry in entries:
            if entry.isIntersecting:
                entry.target.classList.add("is-visible")
                observer.unobserve(entry.target)

    observer = window.IntersectionObserver.new(
        create_proxy(on_intersect),
        to_js({"threshold": 0.12, "rootMargin": "0px 0px -40px 0px"}),
    )

    for el in items:
        observer.observe(el)


# ---------- Pricing billing toggle (monthly / annual) ----------
def init_billing_toggle():
    switch_el = document.getElementById("billing-switch")
    values = document.querySelectorAll(".price__value")
    if switch_el is None or not values.length:
        return

    def render(is_annual):
        switch_el.setAttribute("aria-checked", js_bool(is_annual))
        for el in values:
            key = "annual" if is_annual else "monthly"
            next_value = getattr(el.dataset, key, None)
            if next_value is not None:
                el.textContent = next_value

    def on_click(event):
        is_annual = switch_el.getAttribute("aria-checked") == "true"
        render(not is_annual)

    on(switch_el, "click", on_click)

    # Allow toggling with keyboard (Space / Enter).
    def on_keydown(event):
        if event.key == " " or event.key == "Enter":
            event.preventDefault()
            switch_el.click()

    on(switch_el, "keydown", on_keydown)


# ---------- Footer year ----------
def init_footer_year():
    year_el = document.getElementById("year")
    if year_el is not None:
        year_el.textContent = str(js.Date.new().getFullYear())


main()
