---
name: learn-from-tutorial
description: Detect when the current screen is the app's own tutorial, coach mark, or onboarding walkthrough, capture what it teaches, and turn it into durable skill knowledge (strategy.md during an autotap run, or a CARD.md/memory update on graduation) instead of letting it evaporate at the end of the session. Use whenever observe() surfaces instructional text, a spotlight/highlight overlay, a "Skip"/"Got it"/"Next" control, or a step-progress indicator you haven't already accounted for.
homepage: https://github.com/droidrun/mobile-harness
metadata:
  tier: core
  scope: cross-app
  updated: "2026-07-08"
---

# Learn-From-Tutorial Card

Apps that teach you how to use them are handing you a graduated skill for free — a human product designer already decided which behaviors are non-obvious enough to explain. Treat every tutorial screen as a source to mine, not an obstacle to dismiss.

## 1. Detecting a tutorial

On any `observe`, suspect a tutorial/onboarding/coach-mark surface when the node list shows two or more of:

- Explicit control text: "Skip", "Next", "Got it", "Continue", "Done", "Let's go".
- Step-progress affordances: a dot row, a fraction ("2/4"), or a progress bar with no other page content around it.
- Instructional language rather than data or actions: "Tap here to...", "Swipe to...", "This is where you'll find...".
- A layout that otherwise looks like a full-screen illustration + short text block, or a small callout/spotlight anchored to a single element while the rest of the screen is dimmed or unreactive.

This is a `core/mobile-ux-primitives` cross-check, not a replacement for it — if `core/mobile-ux-primitives/onboarding-and-forms.md` already told you what a plain intro carousel does, you don't need this skill just to skip it. Reach for this skill specifically to **capture the content**, not merely to get past it.

## 2. Capturing the content

For each tutorial step encountered, before dismissing it, record:

- **The instructional text verbatim** (from `observe`'s node labels — this is UI chrome, not user data, so it's fine to keep, unlike screen content from inside the app's actual data).
- **The element it points at**, if it's a coach mark anchored to something specific — its label/resource-id from the same `observe` call (not just a raw `(x,y)`, which won't transfer across screen sizes).
- **What actually happens if you follow the instruction.** Don't just log the text — act on it (`tap`/`swipe`/whatever it describes), `observe` again, and note the observed before/after. A tutorial that says "swipe left to archive" and one you've verified swipe-left-to-archive against are very different confidence levels.
- **Whether it matches or contradicts an existing default.** If `core/mobile-ux-primitives` already claims a default for this exact primitive and the tutorial confirms it, that's a validation, worth noting but not urgent. If it contradicts a default, or teaches something with no existing entry, that's the valuable case.

## 3. Where it goes (respects the existing 3-way split — nothing new to invent here)

During an active `autotap` run (a `task.md`/`strategy.md` exist for this app):
- Append findings under a `## Tutorial Findings` section in `strategy.md`, in the same terse style as the rest of the strategy — this is the only file the inner/outer loop edits mid-training, per autotap's rules. Don't write to CARD.md or `core/` directly mid-run.
- At graduation, tutorial findings go through the same three-way split as any other learning: stable, app-general UI facts merge into the app's `CARD.md` (`Useful Labels` if it's a label/selector fact, `Flow Notes` if it's an ordering/behavior fact); anything device- or session-specific goes to `memory/`; anything that touches login, payment, or personal data goes nowhere.

Outside an active `autotap` run (an ad-hoc or exploratory session with no `task.md`):
- Still capture the finding — write it to `<harness>/memory/<app-id>-tutorial-notes.md` (gitignored, per the `memory/` convention) as `- <ISO-date>: <finding>. Source: in-app tutorial. Confidence: observed|unverified.` A later `autotap` run for that app should read this file (alongside the existing CARD) and fold verified entries into the CARD at its own graduation.

## 4. Tagging for cross-app generalization

If a captured finding describes a **generic interaction pattern** rather than an app-specific fact — e.g. "swipe left on a list row reveals delete," "long-press a message opens a reaction menu," "pull down from the top of a feed refreshes it" — tag it explicitly wherever it's recorded:

```
<!-- generalizable: swipe-left-reveal-delete -->
```

This is what lets the skill-curator pass (a separate, periodic, human-reviewed process — not run by `/autotap` itself) find repeated tags across multiple apps' CARDs and propose promoting the pattern into `core/mobile-ux-primitives/*.md`. Don't promote it yourself in the moment — one app confirming a pattern is a data point, not a generalization; the curator's job is to wait for the same tagged pattern to show up independently in several apps before it's trustworthy enough to become a default everyone inherits. See `mobile-harness`'s curator report for the promotion criteria (independent confirmation across 3+ apps, no unresolved app-specific exception).

## 5. What not to do

- Don't copy screen content that isn't UI chrome (user data, other people's names/messages, account details) into any of these files, tutorial or not — same rule as everywhere else in this harness.
- Don't skip a tutorial without at least one `observe` read of its text — even a 1-second dismiss is a missed opportunity if the text was on screen.
- Don't treat a tutorial's claim as verified until you've acted on it and observed the result once. Note unverified claims as such (`Confidence: unverified`) rather than upgrading them to a CARD-worthy fact on faith.
