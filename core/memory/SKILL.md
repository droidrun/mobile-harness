---
name: memory
description: The format and rules for <harness>/memory/ — volatile, gitignored, run-to-run observations that aren't stable enough for a CARD.md yet (or are inherently device/session-specific). Load alongside core/mobile-ux-primitives. Referenced by autotap's SKILL.md graduation step.
homepage: https://github.com/droidrun/mobile-harness
metadata:
  tier: core
  scope: cross-app
  updated: "2026-07-09"
---

# Memory Card

`memory/` is the second half of the three-way graduation split (`autotap/SKILL.md` §"After all iterations"): `CARD.md` is durable and git-tracked, `memory/` is volatile and gitignored, secrets go nowhere. Use `memory/` for anything true right now that you wouldn't bet on staying true, or that's specific to one device/session rather than the app in general.

## What belongs here vs. a CARD

Goes in `memory/`:
- Device quirks observed on one specific run ("on the 1440×3088 cloud device, the FAB sits at y=2818 — don't hardcode, but noting it saved a re-derivation").
- A recovery that worked once but hasn't been confirmed as the *general* fix ("closing and reopening the app cleared a stuck loading spinner — untested whether this generalizes").
- Environment/account-state notes that will go stale ("as of this run, the test account has zero saved items — an empty-state screen isn't a bug").
- Tutorial findings not yet promoted (see `core/learn-from-tutorial/SKILL.md` §3) when there's no active `autotap` task/strategy to attach them to yet.

Goes in a `CARD.md` instead: anything you'd bet holds for the app in general, worth hedging ("often", "may") rather than caveating as one-off.

## Format

One file per app, `memory/<platform>-<app-id>.md` (e.g. `memory/android-com.ebay.mobile.md`). Each entry is a single bullet line, oldest first or newest first (pick one and stay consistent within a file):

```
- 2026-07-09: Sort sheet options take ~600ms to render after tap; poll rather than tap-once. Source: run-004 trace. Confidence: observed.
- 2026-07-09: Search landing sometimes shows a "Recently viewed" carousel instead of results on first launch. Source: run-002 trace. Confidence: unverified (seen once).
```

Required fields inline: the fact, `Source:` (a run id, trace path, or "in-app tutorial"), `Confidence:` (`observed` = you verified the before/after yourself; `unverified` = seen but not confirmed by acting on it).

## Rules

- Never a secret, ever — same boundary as `core/credentials/SKILL.md`, no exceptions for "it's just gitignored."
- Never copied user/app content (messages, personal data, page text) — only operational facts about how the UI behaves.
- `memory/` is read at the start of a run alongside the CARD (prior knowledge), but a fact living only in `memory/` is a candidate for promotion to the CARD once it's been re-confirmed on a couple of runs — don't let it sit in `memory/` indefinitely once it's clearly stable.
