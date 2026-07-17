---
name: debugging
description: Diagnose a failed device action or unexpected screen state — a tap or type that didn't land, an app that never reaches the expected screen, a mobilerun_core error, or an operation the current backend doesn't support. Classify the failure, retry at most once with something changed, and escalate to the user on a repeat. Use whenever an action's observed result doesn't match what you expected.
---

# Debugging

When an action doesn't produce the expected result, the first job is to
**observe before reacting**. Don't retry blind. Read `device.ui()` (or take a
screenshot if the tree looks right but the screen still doesn't) and figure
out what's actually different from what you expected before deciding what to
do about it.

## Failure classes and what to do

**A selector matched nothing** (`find_nodes`/`tap_text`/`tap_node` found no
usable element, or `tap_node` raised because the node had no usable bounds).
- Re-fetch `device.ui()` and look for the element under a different selector
  (`text_contains=`/`desc_contains=`/`any_contains=` instead of an exact
  match, or `resource_id` if you were matching on text).
- Check you're still on the screen you expected — an interstitial, dialog,
  or navigation you didn't account for may have changed the foreground
  screen. If so, this is a blocker, not a selector problem: read
  `core/blockers/GUIDE.md`.
- One retry with a broader selector. If it still fails, stop and surface it.

**The expected state never appears** (you acted, observed again, and the
screen still doesn't show what should follow).
- Re-read `device.ui()` first — an unexpected overlay, permission dialog, or
  A/B-tested layout variant usually shows up there. Only fall back to a
  screenshot if the tree looks right but the screen visibly isn't (a
  webview or purely visual gap the tree doesn't capture).
- Don't retry the same action unchanged. Either the app needs more time
  (wait briefly and re-observe) or the approach is wrong (change selector,
  change the action, or reconsider whether this is actually the right
  screen).

**mobilerun_core raises a connection or backend error** (a timeout,
connection error, or similar from the cloud/ADB/Portal HTTP backend, as
opposed to an error about the UI itself).
- Re-issue the failing call once. If it fails again, treat this as a
  connection problem, not a UI problem — read
  `platforms/android/recovery/GUIDE.md` (or the iOS equivalent) rather than
  continuing to retry action logic.

**An operation isn't supported** (`device.supports(...)` is false, or the
call itself says the backend can't do this).
- Don't force it. Check `device.capabilities` for what this backend and
  device actually offer, and use the nearest supported alternative. If
  there isn't one, tell the user this action isn't available on their
  current setup rather than approximating it a different way.

**Auth, captcha, payment, or any other secret/consent screen** — this is
never a debugging problem. Stop immediately and read `core/credentials`.
Don't retry, don't try to work around it.

## Retry rules

- **One retry max** on anything that looks transient (a missed selector, a
  slow-to-render screen).
- **Change something on retry.** Same action against the same screen
  produces the same failure. Change the selector, wait longer, or
  reconsider the approach — not just "try again."
- **Same failure twice: stop and look, don't patch blind.** Read the live
  `device.ui()` tree (unfiltered, if it's ambiguous) and confirm what the
  screen actually shows before trying a third variation. Writing a third
  attempt at something you haven't actually diagnosed is how failures
  compound instead of resolving.
- **Never retry** past a credentials/consent gate (`core/credentials`) or a
  blocker you couldn't confidently classify (`core/blockers`).

## When to stop and escalate to the user

- The same failure happens twice in a row.
- Any credential, payment, OTP, or consent prompt (always — see
  `core/credentials`).
- An unrecognized modal you can't safely dismiss (see
  `core/blockers` — "unknown_modal").
- An error you don't recognize and can't classify against the cases above.

When escalating, say plainly: what you were trying to do, what happened
instead, and what you tried. Don't dump a full trace or stack unless asked —
the useful part is the diagnosis, not the noise.

## Memory

If you hit a failure and found a fix — even one you're not fully sure
generalizes — that's worth recording so a future run doesn't rediscover it
from scratch. Read `core/memory/GUIDE.md`'s format if you haven't already
this session, then write:

- To `memory/apps/<app-id>.md` if it's specific to that app (a screen that's
  slow to render, a selector that intermittently misses).
- To `memory/failures.md` if it's a cross-app or environment-level pattern
  (a backend quirk, a device/emulator peculiarity) rather than one app's
  behavior.

Use the standard shape: `- <date>: <finding>. Source: observed via <backend
or session>. Confidence: observed|unverified.` Mark it `unverified` unless
you've actually confirmed the fix works, not just that it worked once.

## What never to do

- Don't retry without first observing what actually happened.
- Don't loop more than twice on the same failure.
- Don't speculate to the user ("maybe the network is slow") — say what you
  actually observed.
- Don't report a fix as verified if you didn't confirm it.
