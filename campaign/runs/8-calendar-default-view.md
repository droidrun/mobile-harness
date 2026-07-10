# Run 8 — Calendar app default view (mis-identified — real accuracy gap)

- **Task ID:** 7d2bb29b-1ae5-4471-9482-726fdb5089a6
- **Prompt:** "Open the Calendar app and tell me which view it defaults to (day, week, month, or agenda)."
- **Queue item:** #21
- **Run via:** mobilerun Task Runner, `mobilerun/mobile-agent-fast`
- **Time:** 10 Jul 2026, 01:53 · **Duration:** 11s (27 events) · **Status:** Completed, but the answer looks wrong

## Result (verbatim)
> The Calendar app defaults to the month view.

## What the device stream actually showed
A screenshot captured mid-task (via the Task Runner's own live device view) showed an hourly grid with day-of-week columns across the top ("LUN. 6, MAR. 7, MER. 8, JEU. 9, VEN. 10, SAM. 11, DIM. 12") and hour markers down the left side (01, 02, 03...) — a week/day-style hourly agenda grid, not a month grid of date cells. This directly contradicts the reported result.

## Execution timeline (27 events, condensed)
7-9. `open_app('Calendar')` → started `com.android.calendar`
12. FastAgentResponse — "The Calendar app didn't open as expected; instead, I'm stuck on a Google Pl[ay Services "Checking info..." interstitial]" — self-heal needed already
13-16. `system_button('home')`, `open_app('Calendar')` again → succeeded this time
19. FastAgentResponse — "The Calendar app is open. Looking at the UI elements, there is a `Spinner` at index 6 labeled "juill[et 2026]"" — **this is the only evidence cited for the final answer**
20-27. `complete('true', 'The Calendar app defaults to the month view.')` → FastAgentEnd ×2 → Finalize → Screenshot → RecordUIState → Result

## Read against the framework — genuine accuracy gap, not a navigation failure
- **Root cause:** the agent's only evidence was a header `Spinner` reading "juillet 2026" (July 2026). It inferred "month view" from a month name appearing in a header control, without checking the shape of the content actually below it. The visible grid was hourly (week/day style), not a month calendar grid — the header spinner shows the current month in more calendar apps regardless of which view is active, so it's not diagnostic on its own.
- **This is a more concerning class of gap than the earlier navigation failures**, because the task *reported success* with a confident, specific, wrong answer rather than failing visibly. A failed task is caught by definition; a wrong-but-confident answer isn't caught unless something (or someone) cross-checks it against the actual screen.
- **Folded back:** added a new "Don't infer view/state from a header label alone" note to `content-and-feeds.md` — the generalizable rule is to verify layout/mode/view claims against the actual rendered content structure (grid shape, row/column meaning), not a nearby label that may describe context rather than the specific thing asked about.
- **Also worth registering as a broader methodology point for the campaign:** this is the first case where the *stated* result contradicted the *visual* evidence available in the same trace. Worth spot-checking a fraction of "clean pass" results against their screenshots going forward rather than trusting `Result` text at face value — the Task Stream's live device screenshots (captured separately from the agent's own reasoning) are exactly the check that caught this one.
