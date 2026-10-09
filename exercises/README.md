# Exercises

This folder contains step by step guides that turn the "Your First Prompt" lesson into hands on practice. Each guide is self contained and walks you through one part of the lesson from start to finish. Together they teach you how to talk to Claude Code with confidence and how to stay in control of every change it makes.

The guides are built directly from the lesson document at the root of this repository, `Your First Prompt.docx`. Nothing here invents new material. Everything maps back to that lesson and to the FlowState demo project that ships alongside it.

## How to use these guides

Work through the guides in order. The first two build the two habits that make Claude Code safe and pleasant to use. The third brings both habits together in a single, complete exercise.

1. Keep this repository open in one window and a terminal open in another.
2. Read one guide fully before you begin, then follow it one step at a time.
3. After each step, pause and observe what changed on screen and in the files. Observing is part of the exercise, not a detour from it.

## The guides

1. `01-choosing-your-approval-mode.md`
   Learn the difference between approval mode and auto accept mode, and choose the level of oversight you are comfortable with.

2. `02-using-plan-mode.md`
   Learn how Plan Mode studies your project with read only tools and returns a clear plan before it touches any code.

3. `03-add-a-dark-mode-toggle.md`
   The main worked exercise. Use a descriptive prompt and Plan Mode to add a dark mode toggle to the FlowState landing page, then review the result carefully. A reference solution lives on the `solution/dark-mode` branch for you to compare against afterwards.

## Before you begin

You will need the following. The root `README.md` explains each item in more detail.

* The Claude Code command line tool, installed and ready to run.
* Access to your Claude account.
* A terminal open in the root folder of this repository.
* A modern web browser so you can view the FlowState demo as you work.
* Python 3.10 or newer, so you can serve the demo with `python3 serve.py` and run the tests with `pytest`.

## Key takeaways

These are the ideas the lesson wants you to carry away. Each guide reinforces them in practice.

* Be as descriptive as possible with your prompt. A little extra context up front gives Claude a much better chance at the result you want.
* If you want to stay in the loop at every step, you can. Approval mode keeps you in control.
* Use Plan Mode to let Claude study the details of what you want before it executes any code.

In short, be descriptive, stay in control, and let Plan Mode do the thinking first.
