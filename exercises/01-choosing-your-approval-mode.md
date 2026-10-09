# Exercise 1: Choosing Your Approval Mode

## Goal

Understand the two ways Claude Code can apply its work, and choose the one you are most comfortable with. By the end you will know how to switch between approval mode and auto accept mode, and you will understand exactly what each mode does.

## Background

You talk to Claude Code the way you would talk to any assistant. The one thing worth deciding early is how much oversight you want over the changes it makes.

There are two modes.

**Approval mode.** Claude asks for your permission each time it wants to edit a file or run a command. Nothing happens to your project until you say yes. This mode keeps you fully in the loop.

**Auto accept mode.** File edits are approved automatically, so they apply as soon as Claude makes them. Commands still require your permission, so a command that could affect your machine or your environment always pauses for a yes.

There is no wrong answer here. Use whichever mode suits the task and your comfort level.

## Steps

1. Open your terminal and move into the root folder of this repository, the folder that contains `index.html`.

2. Start Claude Code by running the command below.

   ```bash
   claude
   ```

3. Press `Shift + Tab` to cycle between the modes. Each press moves you to the next mode.

4. Watch the footer at the bottom of the screen. It always tells you which mode is active.

5. Land on auto accept mode and read the footer. It says `accept edits on`, which confirms that file edits will apply automatically.

6. Keep pressing `Shift + Tab` until the footer no longer shows `accept edits on` or any other mode message. You are back in approval mode, where Claude will pause and ask before each edit. Along the way you will pass through `plan mode on`, which is the subject of the next exercise.

## What to observe

* The footer is your source of truth. It changes as you cycle, so you always know whether edits will apply on their own or wait for your approval.
* In auto accept mode, only file edits are automatic. A command still asks for permission, which is an important safety line.

## Intended learning outcome

You decide how much control you keep. Approval mode trades a little speed for full oversight. Auto accept mode trades a little oversight for speed on file edits while still guarding commands. Neither is better than the other. Pick the one that fits the moment, and remember that you can switch at any time with `Shift + Tab`.

## Next

Continue to `02-using-plan-mode.md` to learn how Claude can study your project and produce a plan before it changes anything.
