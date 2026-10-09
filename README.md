# Claude Code Demos: Your First Prompt

A small, hands on demo for learning Claude Code. It pairs a realistic sample project with a short lesson and a set of step by step exercises, so you can practice writing your first prompts and stay in control of every change Claude Code makes.

## Project Overview

This repository is a teaching resource for Claude Code. It brings three things together.

* **A sample project.** FlowState is a modern landing page for a fictional project management product. It is built with HTML, CSS, and Python. The page's interactive behavior lives in `main.py`, which runs directly in the browser through [PyScript](https://pyscript.net). There are no frameworks and no build step. It is small enough to read in one sitting and realistic enough to show meaningful changes.
* **A lesson.** `Your First Prompt.docx` explains how to talk to Claude Code, how to choose between approval and auto accept modes, and how to use Plan Mode to plan a change before any code is touched.
* **A set of exercises.** The `exercises` folder turns the lesson into guided practice you can follow one step at a time.

The FlowState page is the starting point. It currently ships as a light theme only page, and the exercises walk you through extending it with Claude Code.

The page itself includes a sticky header with a logo, navigation, and a call to action, a hero section with a headline and a pure CSS product preview, a strip of placeholder customer logos, three feature cards, three testimonials, a pricing section with a monthly and annual switch and a highlighted plan, a closing call to action band, and a multi column footer. On narrow screens the navigation collapses into a menu behind a button.

## Important Note on Intentional Flaws

Some parts of this project are intentionally left incomplete or imperfect for learning. They are deliberate, and they should not be treated as bugs to fix.

The clearest example is the comment at the very top of `styles.css`, which states that dark mode is intentionally not implemented yet. That line is a marker, not an oversight. It signals the exact feature you are meant to build during the exercises, and it is left in place on purpose.

As you work through the guides, you may be asked to notice details like this and understand them rather than change them. Please leave intentional markers as they are. The goal is to practice reading and reviewing code, which is one of the most valuable skills when you work alongside an AI assistant.

## How It Works

FlowState has three layers, each in its own file.

| Layer | File | What it does |
| --- | --- | --- |
| Content | `index.html` | The markup and copy for every section of the page. |
| Presentation | `styles.css` | Design tokens as CSS variables, layout, and responsive rules. |
| Behavior | `main.py` | Python that makes the page interactive. |

`index.html` loads the PyScript runtime and then runs `main.py` with `<script type="mpy" src="main.py">`. The `mpy` type selects MicroPython, a lean Python interpreter that starts in a fraction of a second, so the page becomes interactive almost immediately. Inside `main.py`, `js.document` and `js.window` give Python direct access to the page and the browser, and `create_proxy` lets an ordinary Python function act as an event handler.

`main.py` wires up five small features, one function each.

* `init_mobile_nav` opens and closes the menu on narrow screens, closes it after a link is tapped or Escape is pressed, and resets it when the window grows back to desktop width.
* `init_header_scroll_state` adds a shadow to the sticky header once the page scrolls.
* `init_scroll_reveal` fades each section in as it scrolls into view.
* `init_billing_toggle` switches the pricing between monthly and annual, by mouse or keyboard.
* `init_footer_year` keeps the copyright year current.

`serve.py` is a small local web server built on the Python standard library. The page must be served over HTTP so the browser can fetch `main.py`. Browsers do not allow a page opened straight from disk to load another file, so if you double-click `index.html` the content still appears, but the interactive features stay off and a notice at the bottom of the page explains how to start the server. When `main.py` starts, it adds a `py-ready` class to the page, which switches that fallback off.

## Prerequisites

To view the demo you need the following.

* A modern web browser such as Chrome, Firefox, Safari, or Edge.
* Python 3.10 or newer, to run the local server.
* An internet connection the first time you open the page, so the browser can download the PyScript runtime. Your browser caches it afterwards.

To run the test suite you also need the packages in `requirements.txt`, which the installation steps below cover.

To work through the exercises you also need the following.

* The Claude Code command line tool, installed and ready to run.
* Access to your Claude account.
* A terminal open in the root folder of this repository.

## Installation

There is no build step. The page runs straight from the files.

1. Get the project onto your machine by cloning this repository or downloading it.

   ```bash
   git clone https://github.com/ANI-IN/claude-code-first-prompt-python.git
   cd claude-code-first-prompt-python
   ```

2. Viewing the page needs nothing beyond Python itself. To run the tests, create a virtual environment and install the test dependencies.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate          # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python -m playwright install chromium   # only needed for the browser tests
   ```

To prepare for the exercises, install the Claude Code command line tool, then open a terminal in this folder and run `claude`.

## Project Structure

```
.
├── index.html                        # Markup and page content for the FlowState landing page
├── styles.css                        # All styling, design tokens as CSS variables, and responsive rules
├── main.py                           # Mobile navigation, header scroll state, scroll reveal, billing toggle, footer year
├── serve.py                          # Local development server (Python standard library only)
├── requirements.txt                  # Test dependencies (pytest and Playwright)
├── pytest.ini                        # Test configuration
├── tests/                            # Automated checks for the page and its Python
│   ├── fake_browser.py               # Lightweight stand-in browser used by the unit tests
│   ├── test_main.py                  # Behavior of every feature in main.py
│   ├── test_page.py                  # Structure of index.html and styles.css
│   ├── test_serve.py                 # The local server
│   └── test_browser.py               # End-to-end tests in a real headless browser
├── README.md                         # This file
├── Your First Prompt.docx            # The lesson this demo supports
└── exercises/                        # Step by step guides derived from the lesson
    ├── README.md                     # How to use the exercises, plus the key takeaways
    ├── 01-choosing-your-approval-mode.md
    ├── 02-using-plan-mode.md
    └── 03-add-a-dark-mode-toggle.md
```

## Running the Demos

Start the local server from the root folder of this repository.

```bash
python3 serve.py
# then visit http://localhost:8000
```

Always open the page through this address rather than by double-clicking `index.html`, otherwise the interactive features stay off. Add `--open` to open the page in your default browser automatically, or `--port 9000` to use another port. The server disables caching, so a plain reload always shows your latest edits. Press `Ctrl + C` to stop it.

Python's built-in static server works too, though your browser may cache older copies of `main.py` while you edit.

```bash
python3 -m http.server 8000
```

Once the page is open, try the interactions so you can see the demo working.

* Toggle the pricing section between monthly and annual to watch the prices update.
* Make the browser window narrow and confirm the navigation collapses into a menu behind a button.
* Scroll down the page and watch each section reveal as it comes into view.

If something does not respond, open your browser's developer console. PyScript reports any Python error there with a full traceback, and also shows it on the page.

## Testing

The test suite checks the page in three ways.

* **Unit tests** in `tests/test_main.py` run `main.py` against the real `index.html` inside a lightweight stand-in browser, so every feature is exercised in plain Python in about a second, with no browser and no network.
* **Structure tests** in `tests/test_page.py` and `tests/test_serve.py` confirm the page wiring, the hooks `main.py` relies on, the intentional marker in `styles.css`, and the local server.
* **End-to-end tests** in `tests/test_browser.py` serve the page, open it in headless Chromium with Playwright, and click, type, scroll, and resize exactly as a visitor would.

Run everything with the command below.

```bash
pytest
```

To run only the fast offline tests, or only the browser tests, use these.

```bash
pytest -m "not browser"
pytest -m browser
```

The browser tests skip themselves, with a message explaining why, when Playwright or Chromium is not installed or when the PyScript runtime cannot be downloaded.

## Exercises

The `exercises` folder contains the guided practice for this demo. Start with `exercises/README.md`, which explains how to use the guides and lists the key takeaways from the lesson.

Work through the guides in order.

1. `exercises/01-choosing-your-approval-mode.md` teaches the difference between approval mode and auto accept mode.
2. `exercises/02-using-plan-mode.md` teaches how Plan Mode studies your project and returns a plan before any code changes.
3. `exercises/03-add-a-dark-mode-toggle.md` is the main worked exercise, where you combine a descriptive prompt with Plan Mode to add a dark mode toggle to FlowState and then review the result.

## Reference Solution

The `main` branch is the starting point for the exercises. The `solution/dark-mode` branch holds a complete reference implementation of Exercise 3, including the dark theme, the header toggle, the saved preference, and tests for all of it. Try the exercise yourself first, then compare.

```bash
git switch solution/dark-mode   # view the reference solution
git switch main                 # return to the starting point
```

Your own result does not need to match it line for line. Many good solutions exist, and the exercise is about the process as much as the outcome.

## Additional Notes

**The lesson.** `Your First Prompt.docx` is the source lesson that these exercises are built from. It is worth reading first if you want the full context.

**Design notes.**

* The color system lives in CSS variables inside the `:root` block at the top of `styles.css`, anchored on an indigo and violet accent.
* Typography uses the Inter and system font stack, so it renders consistently with no web font download.
* Layouts use CSS Grid and Flexbox, with responsive breakpoints that reflow the page for tablets and phones. The pricing grid surfaces the recommended plan first on small screens.
* Accessible touches include a keyboard operable billing toggle, `aria` attributes on interactive controls, and a reduced motion fallback that calms animations for visitors who prefer less movement.
* Apart from the PyScript runtime, the page makes no external requests. Icons are inline SVG, avatars are drawn with CSS, and the hero preview is built from simple page elements.

**Customizing.**

* To change colors, edit the variables in the `:root` block at the top of `styles.css`.
* To change copy and branding, update the text and the `FlowState` wordmark in `index.html`.
* To change pricing, update the `data-monthly` and `data-annual` attributes on each price value in `index.html`, which drive both billing states.
* To change behavior, edit the matching `init_` function in `main.py`, then reload the page.

**License.** Provided as is for demonstration and educational purposes. Use it freely.
