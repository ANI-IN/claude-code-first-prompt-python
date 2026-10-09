# Exercise 3: Add a Dark Mode Toggle

## Goal

Use everything from the first two exercises to build a real feature. You will add a dark mode toggle to the FlowState landing page, driven by a descriptive prompt and planned out before any code changes. By the end you will have seen how a well written prompt, Plan Mode, and step by step approval combine into a controlled, high quality change, and you will have practiced reviewing that change with a careful eye.

## The starting point

The FlowState landing page in this repository is intentionally a light theme only page. It has a header, a hero section, social proof, features, testimonials, pricing with a monthly and annual switch, a closing call to action, and a footer. What it does not yet have is a dark theme or a way to switch to one. That missing feature is the exercise.

Before you type anything, open `styles.css` and read the comment at the very top of the file.

```css
/* =================================================================
   FlowState — Landing page styles
   Light theme only (dark mode intentionally not implemented yet).
   ================================================================= */
```

That marker is deliberate. It tells you plainly that dark mode is the feature you are about to build, and it is left in place on purpose. Keep it in mind. You will come back to it at the end of this exercise.

## Steps

### 1. Open the project and start Claude Code

Open your terminal in the root folder of this repository, the folder that contains `index.html`, then start Claude Code.

```bash
claude
```

### 2. Enter Plan Mode

Press `Shift + Tab` a couple of times until the footer reads `plan mode on`. You want a plan before any file changes, because a theme touches many parts of the page at once.

### 3. Write a descriptive prompt

The more context you give up front, the closer the result will be to what you want. You can start with a short prompt like this one.

```text
My app needs a dark mode implemented across the entire app. Can you create a toggle switch on the header that allows a user to toggle between light mode and dark mode? I need you to find a good contrast color that works based on my existing light theme.
```

A more descriptive prompt gives Claude far more to work with. The version below spells out each requirement and asks for a plan first. This is the recommended prompt for the exercise.

```text
My app needs a dark mode implemented across the entire application.

Requirements:
- Add a dark mode toggle switch in the header.
- The toggle should persist the user's preference using localStorage.
- Use CSS variables instead of duplicating styles.
- Find accessible contrast colors that work well with the existing light theme.
- Ensure all sections (hero, features, testimonials, pricing, footer, buttons, cards, navigation, and links) support dark mode.
- Add smooth transitions between themes.
- Update the README with a brief explanation of how the dark mode implementation works.

Before making changes, analyze the existing styling approach and provide a short implementation plan.
```

Because `main.py` runs in the browser, it can use the browser's `localStorage` directly through `js.window.localStorage`, so the prompt works exactly as written.

### 4. Review the plan

Let Claude study the project and return its plan. Read it carefully and check it against the requirements you gave. A good plan for this task will mention the existing design tokens in `styles.css`, a set of dark values for those tokens, a toggle control in the header, a new function in `main.py` that saves the choice so it survives a reload, smooth transitions, and an update to the documentation.

If the plan looks right, accept it. If anything is missing, refine your prompt and let Claude plan again.

### 5. Approve the work step by step

When you accept the plan, let Claude ask for your approval at each step. This is approval mode from Exercise 1, and it is the safest way to watch a multi part change unfold. Read each proposed edit before you say yes. You will typically see changes flow through these files.

* `styles.css` gains a set of dark values for the existing color tokens, so the whole page can re theme from one place.
* `index.html` gains a toggle control in the header.
* `main.py` gains a Python function that flips the theme and saves the choice.
* `README.md` gains a short explanation of how the dark mode works.

### 6. Test the result in the browser

Start the local server from the root folder of this repository, then open `http://localhost:8000` in your browser. Do not open `index.html` by double-clicking it: the page's Python cannot start from a file on disk, so the toggle would do nothing.

```bash
python3 serve.py
```

Try the feature.

* Click the new toggle and confirm the whole page changes theme, not just part of it.
* Reload the page and confirm your choice is remembered.
* Move through every section and confirm the text stays readable and the contrast holds up.

Then run the test suite to confirm nothing else broke.

```bash
pytest
```

The existing tests cover the navigation, header, scroll reveal, pricing toggle, and footer, so a passing run tells you the new feature did not disturb them. If Claude also added tests for the theme toggle, read them as part of your review.

Two tests guard project conventions rather than features, and a change can trip them even when the page works.

* `test_intentional_dark_mode_marker_is_kept` fails if the comment at the top of `styles.css` was edited. That comment is an intentional marker, covered in the last section of this guide.
* `test_page_has_no_inline_or_local_browser_scripts` fails if the change added a script that is not Python. All behavior in this project lives in `main.py`.

If either one fails, read its message, then ask Claude to put things back. Catching this is exactly the kind of review the exercise is about.

## What to look for in the code

This exercise is as much about reading code as writing prompts. As you review Claude's work, look for these things.

* **Reuse over duplication.** The light theme already stores every color as a CSS variable in the `:root` block at the top of `styles.css`. A strong solution redefines those same variables for the dark theme rather than rewriting each component. That is what the requirement to use CSS variables instead of duplicating styles is asking for.
* **A single source of truth.** When the tokens are the only thing that changes, every section updates on its own because each section reads from the tokens.
* **Persistence.** Look for the Python in `main.py` that reads and writes the saved preference, so the theme survives a page reload.
* **Accessible contrast.** Check that the dark values keep text and icons legible, not just recolored.

## Notice the intentional marker

Now return to the comment at the top of `styles.css` that you read at the start.

```css
   Light theme only (dark mode intentionally not implemented yet).
```

Before this exercise, that line was accurate. After you add dark mode, it no longer matches what the code actually does. This is left in the project on purpose, and it is a small but important lesson. An assistant can carry out a large change flawlessly and still leave a stale note behind that no longer tells the truth. The habit worth building is to notice details like this while you review, understand why they matter, and treat every change as something to read, not just accept.

For this exercise, simply notice the marker and understand what it teaches. It is here to sharpen your review, not to send you chasing a fix.

## Compare with the reference solution

When you have finished your own review, compare your result with the reference implementation on the `solution/dark-mode` branch. Commit or stash your work first, then switch branches.

```bash
git switch solution/dark-mode
python3 serve.py
pytest
```

Look at how the reference handles each requirement from the prompt, then switch back with `git switch main`. Your version does not need to match line for line. The aim is to recognize a sound approach when you see one.

## Intended learning outcome

You have now seen the full loop the lesson is built around. A descriptive prompt gives Claude the context it needs. Plan Mode turns that prompt into a reviewable plan before any code changes. Approval mode lets you watch and confirm each step. A careful review at the end catches the details that automation can miss.

Be descriptive, stay in control, and let Plan Mode do the thinking first.
