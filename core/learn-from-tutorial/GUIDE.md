---
name: learn-from-tutorial
description: Detect when the current screen is the app's own tutorial, coach mark, or onboarding walkthrough, capture what it teaches, and turn it into durable knowledge in memory/ (and, once verified, an app CARD.md) instead of letting it evaporate at the end of the session. Use whenever a screen surfaces instructional text, a spotlight/highlight overlay, a "Skip"/"Got it"/"Next" control, or a step-progress indicator you haven't already accounted for.
---

# Learn From Tutorial

Apps that teach you how to use them are handing you a graduated skill for free — a human product designer already decided which behaviors are non-obvious enough to explain. Treat every tutorial screen as a source to mine, not an obstacle to dismiss.

## 1. Detecting a tutorial

On any observation, suspect a tutorial/onboarding/coach-mark surface when the screen shows two or more of:

- Explicit control text: "Skip", "Next", "Got it", "Continue", "Done", "Let's go".
- Step-progress affordances: a dot row, a fraction ("2/4"), or a progress bar with no other page content around it.
- Instructional language rather than data or actions: "Tap here to...", "Swipe to...", "This is where you'll find...".
- A layout that otherwise looks like a full-screen illustration + short text block, or a small callout/spotlight anchored to a single element while the rest of the screen is dimmed or unreactive.

This is a `core/mobile-ux-primitives` cross-check, not a replacement for it — if `core/mobile-ux-primitives/onboarding-and-forms.md` already told you what a plain intro carousel does, you don't need this file just to skip it. Reach for this specifically to **capture the content**, not merely to get past it.

## 2. Capturing the content

For each tutorial step encountered, before dismissing it, note:

- **The instructional text verbatim** (this is UI chrome, not user data, so it's fine to keep — unlike screen content from inside the app's actual data).
- **The element it points at**, if it's a coach mark anchored to something specific — its label or resource id from the accessibility tree (not just raw pixel coordinates, which won't transfer across screen sizes).
- **What actually happens if you follow the instruction.** Don't just log the text — act on it, observe again, and note the observed before/after. A tutorial that says "swipe left to archive" and one you've verified swipe-left-to-archive against are very different confidence levels.
- **Whether it matches or contradicts an existing default.** If `core/mobile-ux-primitives` already claims a default for this exact primitive and the tutorial confirms it, that's a validation, worth noting but not urgent. If it contradicts a default, or teaches something with no existing entry, that's the valuable case.

## 3. Where it goes

Read `core/memory/GUIDE.md` first if you haven't already this session — this follows that convention, nothing new to invent.

- Write the finding to `memory/apps/<app-id>.md`, using the standard memory shape: `- <ISO-date>: <finding>. Source: in-app tutorial. Confidence: observed|unverified.`
- If you've acted on the instruction and confirmed the result, mark it `observed`. If you only read the text and didn't verify it, mark it `unverified` — don't upgrade it on faith.
- Update `memory/index.md` if this is the first memory file for this app.
- If the finding is a stable, app-general UI fact (not device- or session-specific) and you have a CARD.md for this app open for editing anyway, it can go straight into the CARD instead of (or in addition to) memory. Don't create a CARD just to hold one tutorial finding — memory is the default landing spot.
- Never write anything that touches login, payment, or personal data to either place.

## 4. Flagging cross-app patterns

If a captured finding describes a **generic interaction pattern** rather than an app-specific fact — e.g. "swipe left on a list row reveals delete," "long-press a message opens a reaction menu," "pull down from the top of a feed refreshes it" — tag it explicitly wherever it's recorded:

```
<!-- generalizable: swipe-left-reveal-delete -->
```

This repo has no automated curator; promotion into `core/mobile-ux-primitives/*.md` is a manual, human-reviewed step. The tag exists so a maintainer scanning `memory/apps/*.md` across several apps can spot a pattern that keeps recurring independently and is worth promoting — treat one app confirming a pattern as a data point, not a generalization. Don't edit `core/mobile-ux-primitives/*.md` yourself from a single observation.

## 5. What not to do

- Don't copy screen content that isn't UI chrome (user data, other people's names/messages, account details) into `memory/` or a CARD, tutorial or not — same rule as everywhere else in this harness.
- Don't skip a tutorial without at least one observation of its text — even a fast dismiss is a missed opportunity if the text was on screen.
- Don't treat a tutorial's claim as verified until you've acted on it and observed the result once.
