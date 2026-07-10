# Run 10 — Clock app default tab (likely leftover state, not a true default)

- **Task ID:** 96f5537c-44e9-42f0-9e7c-df9417e335b8
- **Prompt:** "Open the Clock app and tell me which tab it opens to by default (alarm, clock, timer, or stopwatch)."
- **Queue item:** #26
- **Run via:** mobilerun Task Runner, `mobilerun/mobile-agent-fast`
- **Time:** 10 Jul 2026, 01:57 · **Duration:** 8s (20 events) · **Status:** Completed

## Result (verbatim)
> The Clock app opens to the Timer (Minuteur) tab by default.

## Execution timeline (20 events — very short, single observation)
7-9. `open_app('Clock')` → started `com.android.deskclock`
12. FastAgentResponse — "The Clock app is open. Looking at the UI elements, the "Minuteur" (Timer) tab is currently active..." — no navigation needed, answered immediately from the first screen.
13-20. `complete('true', ...)` → FastAgentEnd ×2 → Finalize → Screenshot → RecordUIState → Result

## Read against the framework — a methodology gap, not really an agent gap
- **This is almost certainly leftover state, not the app's real default.** Run 1 (task #28, this same campaign, this same device session) explicitly navigated into and used the Minuteur/Timer tab of this exact Clock app. Stock Android clock apps commonly reopen to whatever tab was last viewed rather than a fixed factory tab. The agent had no way to know this and answered as if it had observed a true default — which is a reasonable-looking answer that's likely wrong for the reason actually asked about.
- **This is a campaign-methodology gap more than an agent gap:** the task queue phrased several items as "what does X open to by default," but never forced a fresh app state (force-stop, or first-ever launch) before asking. Once any earlier task has touched the same app, "default" becomes unverifiable from later observations alone.
- **Folded back:** added a "'Default' screen claims can actually be persisted last-used state" note to `system-surfaces.md`, generalizing beyond just Clock — the same caution applies to Calendar (task #21, this campaign) and likely other tabbed apps in the remaining queue (Camera mode, Music's default screen, etc.). Recommends treating single-observation "default" claims as "opened to X on this launch" unless the app was demonstrably fresh.
- **Practical implication for the rest of the queue:** future default-view questions should either run first (before any other task touches that app), or the phrasing should shift to "what tab/view is currently shown" rather than implying a factory default. Noting this for whoever curates `task-queue.md` next, rather than editing the queue file mid-run.
