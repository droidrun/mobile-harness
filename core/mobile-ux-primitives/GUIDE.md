---
name: mobile-ux-primitives
description: The baseline human intuition for navigating any Android or iOS app — standard navigation chrome, gestures, feed/content conventions, system surfaces, and onboarding patterns. Read this before observing an unfamiliar screen, alongside (and before) the app's own CARD.md. Use it to form a first hypothesis about what an unfamiliar icon, gesture, or layout probably does instead of spending turns rediscovering it from scratch.
---

# Mobile UX Primitives

Applies to every app, every task, every platform — read this alongside (and before) any app-specific `apps/android/<package>/CARD.md` or `apps/ios/<bundle-id>/CARD.md`.

This is the knowledge a person already has after using a handful of smartphone apps: what a hamburger icon opens, what a swipe-left on a list row probably does, that a filled heart means "already liked." An agent without this prior re-derives it from zero on every single app. Most of it is genuinely reusable across apps, not app-specific, so it belongs here rather than inside any one app's CARD.

## How to use this

1. Before spending an observe → guess → observe cycle on an unfamiliar element, check whether it matches a pattern in the reference files below. If it does, act on the default rather than exploring first.
2. **The app's CARD.md wins on conflict.** It was validated against that exact app; a default here is a prior, not a guarantee. If a CARD explicitly contradicts a default below, follow the CARD.
3. If neither this file nor the app's CARD covers what's on screen, that's real exploration. If the screen turns out to be the app's own tutorial/onboarding/coach-mark, read `core/learn-from-tutorial/GUIDE.md` — that's the fastest way to turn unfamiliar territory into a durable fact instead of a one-off guess.
4. These are strong priors, not certainties. Confirm a medium-confidence hypothesis with one cheap observation after acting, rather than chaining several guesses before checking — especially before anything hard to undo (a submit, a purchase, a delete).

## Reference files (read on demand)

- `navigation-patterns.md` — bottom nav bars, hamburger/drawer menus, tab bars, back behavior, floating action buttons, breadcrumbs, search entry points.
- `gestures.md` — tap vs. long-press, double-tap, swipe-on-row, swipe-to-dismiss, pull-to-refresh, pinch/zoom, edge-swipe-back, drag-and-drop.
- `content-and-feeds.md` — infinite scroll, vote/like affordances, share sheets, comment threads, cards vs. dense lists, follow vs. friend-request semantics.
- `system-surfaces.md` — permission dialogs, notification shade, keyboard behavior, app switcher, deep links/intents, toasts/snackbars.
- `onboarding-and-forms.md` — intro carousels, coach marks, multi-step progress indicators, inline validation, autofill, OAuth/SSO handoffs.

## Non-negotiable defaults (kept here, not split out — small enough to always hold in context)

- A magnifying-glass icon opens search; tapping it usually reveals a text input, not results directly.
- Three horizontal lines ("hamburger") open a global side drawer; three dots (vertical `⋮` or horizontal `⋯`) open a contextual menu scoped to one item or screen — visually similar, functionally different.
- A numbered badge on a nav icon, app icon, or bell means unread/pending count, not a label.
- Back (system gesture, button, or in-app chevron) returns to the previous screen; it does not undo a submitted action.
- A pencil or "+" icon is almost always "create new."
- If a tap gets no response and the element looks interactive, wait briefly and re-observe before concluding it's non-interactive — many elements are momentarily unresponsive mid-animation, not actually dead.

## Traps (mirrors CARD.md house style, applies everywhere)

- Never enter credentials, OTPs, or payment info based on a "this looks like the flow demands it" inference — read the credentials guide under `core/credentials` regardless of which app you're in.
- Don't treat a pending/requested state ("Following requested", "Invite sent") as a failure — see `content-and-feeds.md`.
- Don't assume a feed has fully loaded from one observation — infinite-scroll feeds only reveal the next page after a scroll near the bottom.
