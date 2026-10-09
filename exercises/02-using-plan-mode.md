# Exercise 2: Using Plan Mode

## Goal

Learn how Plan Mode works and when to reach for it. By the end you will be able to enter Plan Mode, ask Claude to study your project, and review a clear plan before any code is touched.

## Background

Plan Mode lives inside the same `Shift + Tab` menu you used in the previous exercise. When you turn it on, Claude takes your prompt and uses read only tools to analyze your codebase and research the implementation you asked for. It reads and reasons, but it does not write.

While it works, Claude asks clarifying questions when it needs them. When it is finished, it returns a detailed plan that it is ready to carry out on your approval.

Plan Mode is a good fit in two situations. The first is a complex change that spans several files or several steps, where a plan up front saves you from surprises. The second is a safe review of your code, where you want Claude to look and explain without changing a single line.

## Steps

1. Open your terminal in the root folder of this repository and start Claude Code.

   ```bash
   claude
   ```

2. Press `Shift + Tab` a couple of times until the footer reads `plan mode on`. That footer message is your confirmation that Plan Mode is active.

3. Type a prompt that describes what you want. For a gentle first try, ask for a read only review, for example a request to explain how the FlowState landing page is structured and how its styling is organized.

4. Send the prompt and watch what happens. Claude reads through the project, may ask you a clarifying question or two, and then presents a plan. Notice that your files stay untouched during this stage.

5. Read the plan from top to bottom. If it matches what you wanted, you can accept it and let Claude begin. If something is missing or off, refine your prompt and let Claude plan again.

## What to observe

* The `plan mode on` footer tells you that you are in a safe, read only stage. Nothing is being written yet.
* The plan is specific. It names the files and the steps Claude intends to follow, which gives you a real chance to catch problems before they exist.
* Clarifying questions are a feature, not a delay. Answering them sharpens the plan.

## Intended learning outcome

Planning first turns a vague request into a concrete, reviewable set of steps. You get to approve the approach before any code changes, which keeps you in control and reduces rework. For anything larger than a one line tweak, plan first and execute second.

## Next

Continue to `03-add-a-dark-mode-toggle.md`, the main exercise, where you combine a descriptive prompt with Plan Mode to build a real feature.
