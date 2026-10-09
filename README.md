# FlowState — SaaS Landing Page

A modern, responsive SaaS-style landing page built with **HTML, CSS, and Python** — the page's behavior is plain Python that runs in the browser through [PyScript](https://pyscript.net). No frameworks, no build tools.

It was created as a clean starting point for **demonstrating Claude Code**: small enough to read in one sitting, realistic enough to show meaningful changes.

> This is the `solution/dark-mode` branch: the reference implementation of `exercises/03-add-a-dark-mode-toggle.md`. Switch to `main` for the starting point used by the exercises.

## Preview

FlowState is a fictional project-management product. The page includes:

- **Sticky header** — logo, navigation links, a call-to-action, and a **light/dark theme toggle** (nav collapses into a hamburger menu on mobile)
- **Hero** — headline, subheadline, dual CTA, and a pure-CSS app preview (no image assets)
- **Social proof** — a strip of placeholder customer logos
- **Features** — three icon cards
- **Testimonials** — three quote cards
- **Pricing** — three plans with a **monthly / annual** billing toggle and a highlighted "Most popular" plan
- **Final CTA band** and a multi-column **footer**

## Getting started

No install step. Start the local server (Python 3.10+, standard library only):

```bash
python3 serve.py
# then visit http://localhost:8000

# or open it in your browser automatically
python3 serve.py --open
```

The page loads `main.py` over HTTP, so serve it rather than opening `index.html` as a file. Browsers do not let a page opened from disk load `main.py`, so a double-clicked `index.html` shows its content but the theme toggle and other controls stay off, and a notice at the bottom explains how to start the server. The first visit needs an internet connection to download the PyScript runtime; your browser caches it afterwards.

## Project structure

```
.
├── index.html        # Markup and page content
├── styles.css        # All styling, design tokens (CSS variables), responsive rules
├── main.py           # Theme toggle, mobile nav, scroll reveal, billing toggle, footer year
├── serve.py          # Local dev server with caching disabled
├── requirements.txt  # Test dependencies (pytest, Playwright)
├── pytest.ini        # Test configuration
├── tests/            # Unit, structure, and end-to-end browser tests
├── exercises/        # The step by step Claude Code exercises
├── Your First Prompt.docx  # The lesson the exercises are built from
└── README.md         # You are here
```

## Design notes

- **Light + dark themes.** The color system lives in CSS custom properties at the top of `styles.css` (`:root`), anchored on an indigo/violet accent. Dark mode re-defines those same tokens — see [Dark mode](#dark-mode) below.
- **Typography.** Uses the `Inter`/system-UI font stack — no web-font download required.
- **Responsive.** Layouts use CSS Grid and Flexbox with breakpoints at `900px`, `768px`, and `420px`. The pricing grid surfaces the recommended plan first on small screens.
- **Accessible touches.** Keyboard-operable billing toggle, `aria` attributes on interactive controls, and a `prefers-reduced-motion` fallback that disables animations.
- **Python in the browser.** `index.html` runs `main.py` with `<script type="mpy">`, using the lightweight MicroPython interpreter so the page is interactive almost immediately. Each feature is one `init_` function that reaches the page through `js.document` and `js.window`.
- **No other external requests.** Apart from the PyScript runtime, icons are inline SVG, avatars are CSS, and the hero preview is built from `div`s.

## Dark mode

The page ships with a built-in light/dark theme toggle — the sun/moon button in the header.

How the implementation works:

- **CSS variables do all the work.** Every color is a custom property defined in `:root` (the light theme). A single `[data-theme="dark"]` block near the top of `styles.css` overrides those same tokens with accessible dark values — **no rules are duplicated**. Every section (hero, features, testimonials, pricing, footer, buttons, cards, navigation, links) updates automatically because their colors come from the tokens.
- **One extra token for contrast.** `--color-accent-text` is used for accent-colored text and icons (eyebrows, feature icons, link hovers). It's separate from `--color-primary-dark` (the primary-button hover) so dark mode can *lighten* accent text for legibility without affecting button hovers.
- **The toggle** flips `data-theme` between `light` and `dark` on the `<html>` element (`main.py` → `init_theme_toggle`), and updates its `aria-pressed` / `aria-label` state.
- **Persistence.** The choice is saved to `localStorage` under the key `flowstate-theme` (via `js.window.localStorage`) and restored on the next visit. Unknown saved values are ignored, and if storage is blocked the toggle still works for the current visit.
- **Applied first.** `init_theme_toggle` runs before any other feature is wired up, so the saved (or system) theme is in place the moment the page's Python starts. With the PyScript runtime cached, that is within a frame or two of the first paint. On a very first visit, while the runtime downloads, the page briefly shows the light theme before switching.
- **System aware.** With no saved preference, the page follows the OS `prefers-color-scheme` setting and reacts live if it changes.
- **Smooth transitions.** Background, border, and text colors animate (~0.3s) when switching, and the animation is suppressed for visitors who prefer reduced motion.

To tune the dark palette, edit the values inside the `[data-theme="dark"]` block in `styles.css`.

## Testing

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium   # for the browser tests

pytest                  # everything
pytest -m "not browser" # fast offline tests only
pytest -m browser       # end-to-end browser tests only
```

- `tests/test_theme.py` covers the dark mode toggle: default and system themes, saving and restoring the choice, live system changes, blocked storage, the header markup, and that the dark block redefines every color token.
- `tests/test_main.py` covers the navigation, header, scroll reveal, billing toggle, and footer year, running `main.py` against the real `index.html` in a lightweight stand-in browser.
- `tests/test_page.py` and `tests/test_serve.py` check the page wiring, the hooks `main.py` relies on, the intentional marker in `styles.css`, and the local server.
- `tests/test_browser.py` serves the page and drives it in headless Chromium, including toggling the theme, reloading, and switching the emulated OS color scheme. These tests skip themselves when Playwright, Chromium, or internet access is unavailable.

## Customizing

- **Colors:** edit the variables in `:root` at the top of `styles.css`.
- **Copy & brand:** update the text and the `FlowState` wordmark in `index.html`.
- **Pricing:** change the `data-monthly` / `data-annual` attributes on each `.price__value` to update both billing states.
- **Behavior:** edit the matching `init_` function in `main.py`.

## License

Provided as-is for demonstration and educational purposes. Use it freely.
