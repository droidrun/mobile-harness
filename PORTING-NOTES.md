# Porting notes — autotap → droidrun/mobile-harness

This branch (`port-to-real-mobile-harness`) adapts autotap's two validated
`core/` additions into the shape and conventions of the real, public
`github.com/droidrun/mobile-harness` repo, so they can be dropped in directly.
This local checkout has no relationship to that repo (no shared git history,
different file layout — it predates `AGENTS.md`/`install.md`/`platforms/`),
so this is staged content to apply by hand, not a mergeable branch.

## What changed and why

- `core/mobile-ux-primitives/SKILL.md` → `GUIDE.md`. Content is unchanged in
  substance; frontmatter trimmed to just `name`/`description` to match
  `core/credentials/GUIDE.md` and `core/memory/GUIDE.md`'s style (dropped
  `homepage`/`metadata.tier/scope/updated`, which aren't part of that
  convention). Internal references updated: `core/credentials/SKILL.md` →
  "the credentials guide under `core/credentials`" (matches `AGENTS.md`'s own
  phrasing), `core/learn-from-tutorial/SKILL.md` → `GUIDE.md`,
  `apps/<platform>/<app-id>/CARD.md` → the real repo's actual two paths
  (`apps/android/<package>/CARD.md`, `apps/ios/<bundle-id>/CARD.md`).
- `core/learn-from-tutorial/SKILL.md` → `GUIDE.md`. Same frontmatter trim.
  Section 3 ("Where it goes") is rewritten: autotap's version routed findings
  through `strategy.md`/`task.md` and a periodic curator pass, neither of
  which exist in mobile-harness. The ported version routes findings through
  mobile-harness's real mechanism instead — `memory/apps/<app-id>.md`, per
  `core/memory/GUIDE.md`'s dated-fact shape (`- <date>: <finding>. Source:
  .... Confidence: ...`) — and reframes the `<!-- generalizable: tag -->`
  convention as an informal signal for a human maintainer scanning `memory/`
  across apps, since there's no automated curator here to consume it
  otherwise.
- `onboarding-and-forms.md`: fixed a stale cross-reference
  (`skills/meta/learn-from-tutorial` → `core/learn-from-tutorial/GUIDE.md`).
  The other four reference files (`navigation-patterns.md`, `gestures.md`,
  `content-and-feeds.md`, `system-surfaces.md`) are unchanged — they don't
  reference anything autotap-specific.

## What still needs manual edits in the real repo (not in this branch — those files don't exist here)

This checkout predates `AGENTS.md`, `SKILL.md`, `install.md`, and
`platforms/`, so the following can't be diffed from here. Apply these three
small edits directly against a real clone of `droidrun/mobile-harness`:

1. **Root `AGENTS.md`, Load Order section** — add a step so agents actually
   load this file. Something like: "Before observing an unfamiliar screen,
   read `core/mobile-ux-primitives/GUIDE.md`." It currently jumps straight
   from the pip-upgrade step to platform routing; this content is
   cross-platform and belongs before that split, not inside it.
2. **Root `SKILL.md`, Load Order section** — same addition, one line, for
   runtimes that load `SKILL.md` instead of `AGENTS.md`.
3. **`platforms/android/GUIDE.md`, Observe-Act-Verify Loop section** — it
   currently loads the app CARD (step 3) but never mentions
   `core/mobile-ux-primitives`. Add it as a step before the CARD load, e.g.
   "Check `core/mobile-ux-primitives/GUIDE.md` for a matching pattern before
   treating an unfamiliar element as something to explore." `platforms/ios/`
   presumably wants the same addition, unread here.
4. **`platforms/android/GUIDE.md`, Observe-Act-Verify Loop, step 6** —
   currently says "If the expected change did not happen, read
   `platforms/android/recovery/GUIDE.md`." That file handles
   connection/backend recovery well but has nothing for in-app action
   failures or blocked screens. Point step 6 at `core/debugging/GUIDE.md`
   first (it now covers that split explicitly and routes to
   `platforms/android/recovery/GUIDE.md` itself when it's actually a backend
   problem).
5. **`platforms/android/recovery/GUIDE.md`, "App blocked" bullet** — currently
   just names the case ("permission dialog, login wall, credential screen,
   crash, or frozen UI") with no guidance. Point it at `core/blockers/GUIDE.md`
   for the permission/dialog case and `core/credentials` for the
   login/credential case — it already does the latter implicitly via its
   "Credential Or Human-Gated Screens" section, just add the former.

## `scripts/curate.py` — now ported (was "not ported" as of the first commit on this branch)

Adapted from autotap's `curate.py`, with two real changes beyond a path
rewrite:

- **Scans two sources, not one.** Autotap's version only read
  `apps/<platform>/<id>/CARD.md`. This repo's `core/learn-from-tutorial/GUIDE.md`
  tells agents to write fresh findings to `memory/apps/<app-id>.md` *before*
  they're confirmed enough for a CARD — so a `generalizable` tag placed there
  per that guide would never have surfaced anywhere. The ported script scans
  `memory/**/*.md` too, attributing `memory/apps/<app-id>.md` to that app for
  the `--min-apps` count, and still reports (but doesn't count toward the
  threshold) freeform memory files that don't follow that naming.
- **`--apply` flag.** Autotap's version was report-only by design (a human
  reviews `.curator/reports/*.md` and promotes by hand). That gate is kept as
  the default. `--apply` additionally drafts each promoted tag directly into
  the suggested `core/mobile-ux-primitives/<file>.md`, inside a clearly
  marked `<!-- BEGIN curator-candidate -->...<!-- END -->` block — still not
  auto-merged into the real prose, still requires a human to fold it in or
  delete it, but removes the hand-copy step. Smoke-tested against this
  checkout's three example CARDs: correctly caught `infinite-scroll-no-pagination`
  as independently confirmed in all three (eBay, Instagram, Reddit) and
  drafted it into `content-and-feeds.md`.

Report output (`.curator/reports/`) is already gitignored here
(`.curator/` — "curator reports are regenerable"), so it travels with the
script, not as committed output.

## `core/debugging` and `core/blockers` — new, ported from `mobile-harness-skills` (the other, private repo)

Not from autotap this time — from `mobile-harness-skills`, the private
knowledge repo behind the Cloud VA's `kilo` runtime, which already has a
mature action-failure taxonomy that `mobile-harness` (this repo) had nothing
equivalent to. `mobile-harness`'s own `platforms/android/recovery/GUIDE.md`
only covers connection/backend failures (no ADB, bad Portal token, etc.) —
nothing for "the tap/type/expected-screen-change didn't happen" or "a dialog
is covering the screen," which is what these two add.

This was a real adaptation, not a copy — `mobile-harness-skills`' originals
assume infrastructure specific to the Cloud VA runtime that doesn't exist in
the public `mobilerun-core[local]` package this repo uses:

- `core/debugging` (source): written against kilo-specific exception types
  (`HitlDenied`), a `mobilerun_sdk` control-plane error, and methods
  (`current_app_id()`, `wait_for_text`/`wait_for_app`) not confirmed to exist
  in the public `mobilerun_core` API surface documented in this repo's own
  `README.md`/`platforms/android/GUIDE.md` (`find_nodes`, `tap_node`,
  `tap_text`, `type`, `clear_input`, `list_apps`, `ui`, `screenshot`,
  `capabilities`/`supports`). The ported version is written only in terms of
  that confirmed surface, describes failures observationally instead of by
  exception class name I can't verify exists here, and routes backend/
  connection errors to `platforms/android/recovery/GUIDE.md` instead of
  assuming a specific SDK error type.
- `core/blockers` (source): built around `lib.dismiss_blockers`, a helper
  library that lives in the Cloud VA's `/ephemeral/scripts`, and a
  `question`-card UI primitive specific to that product's chat surface.
  Neither exists here. The ported version keeps the actually-portable part —
  the `nag` / `unknown_modal` / `permission_grantable` / `permission_sensitive`
  classification and the never-auto-grant-on-sensitive-scopes rule — but
  reframes detection as reading `device.ui()`/`find_nodes()` directly (no
  helper library to call), and reframes "ask via a question card" as "ask one
  short question and wait, offer concrete options," matching the pattern
  `core/credentials/GUIDE.md` already uses for the same kind of gate.

Both close the gap identified when discussing this: `core/memory/GUIDE.md`
already had the *storage* half (a `failures.md` slot, "prior failure and
verified recovery" as a write-trigger, the dated-fact format) but nothing
told an agent how to *detect and classify* a failure before writing one down,
or how many times to retry before giving up. `core/debugging`'s Memory
section explicitly points back into that existing slot
(`memory/apps/<app-id>.md` for app-specific fixes, `memory/failures.md` for
cross-app/environment ones) rather than inventing a new location.
