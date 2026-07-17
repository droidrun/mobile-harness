---
name: blockers
description: Something is covering the screen and blocking progress — an OS runtime-permission prompt, an app-not-responding or update/rating nag, or an unrecognized modal. Classify what's actually there before treating a stalled task as a dead end, grant only a permission the task explicitly needs, and always ask the user before anything privacy-sensitive. Never scroll through or blind-back() out of a dialog you haven't identified.
---

# Blockers — clear the safe ones, never guess the rest

A task stalling — a tap landing nowhere, an expected element missing, a
scroll doing nothing — is usually **not** a dead end. It's often a dialog on
top of the screen you're not accounting for. Before treating it as a
selector or navigation failure (see `core/debugging`), check whether
something is actually blocking the view.

## When to check

Check the moment a step stops making progress, and proactively right after
launching an app or taking an action that commonly triggers a system prompt
(camera, location, first post or send, notifications). Don't keep tapping
into something you haven't identified — that's how a permission dialog
turns into several wasted, silently-failing actions.

Read `device.ui()` (or `find_nodes`) and look at what's actually on screen
before deciding what kind of blocker this is.

## Classifying what's there

| Kind | What it looks like | What you do |
|---|---|---|
| `nag` | "App isn't responding" (ANR), an in-app review prompt, an update nag | Dismiss it (the safe default action — usually "Not now"/"Later"/close) and re-check the screen; this isn't a real obstacle. |
| `unknown_modal` | A modal you don't recognize and can't confidently classify | Tap an explicit **Close/X** if one is visibly present. If there isn't one, **stop and tell the user** what's on screen — never scroll it or blind-`back()` out of it. |
| `permission_grantable` | Camera / microphone / storage / media / notifications / calendar, etc. | Grant it **only if the user's actual task explicitly needs it** (a scan task justifies camera). Tap "While using the app"/"Allow". If the need isn't obvious from the task, treat it like a sensitive scope below — ask instead of guessing. |
| `permission_sensitive` | **Contacts / SMS / call log / location** | **Always ask the user first — never auto-grant, regardless of the task.** This is a hard floor, not a judgment call. |

## The one judgment call: `permission_grantable`

Decide only against what the user actually asked for, not what would be
convenient. "Scan the QR code" justifies camera; it does not justify
location. If the link between the permission and the stated task isn't
obvious, treat it as sensitive: ask one short question and wait — offer
concrete options (grant / deny / let the user handle it on the device) —
the same pattern `core/credentials` uses for anything gated. Granting a
permission is consent on the user's device; when in doubt, ask rather than
assume.

## Never

- Never scroll a modal (it typically won't respond the way a normal screen
  does) or `back()` out of one you haven't identified — you can dismiss the
  wrong thing or leave the flow entirely without realizing it.
- Never tap "Allow" on a sensitive scope, or on a permission the task didn't
  actually call for.
- Never treat a permission prompt or ANR as a task failure in itself — clear
  it (or surface it to the user) and continue; report failure only if the
  underlying task still can't proceed afterward.

Related: `core/credentials` (anything beyond a runtime permission — login,
payment, OTP, consent), `core/debugging` (what to do when the *cause* of a
stall turns out not to be a blocker after all).
