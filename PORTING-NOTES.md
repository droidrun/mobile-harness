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

## Not ported

Autotap's `curate.py` (the script that scans app CARDs for
`<!-- generalizable: tag --></tag>` bullets repeated across ≥3 apps and
proposes `core/` promotions) was deliberately left out. It's a real,
validated mechanism, but it's an autotap-specific tool (reads autotap's
`examples/skills/*/SKILL.md` layout, not mobile-harness's
`apps/<platform>/<id>/CARD.md` layout) — porting the underlying *idea* (a
periodic script that greps `memory/apps/*.md` + `apps/*/CARD.md` for repeated
`generalizable` tags and drafts a promotion PR) is a reasonable follow-up, but
it's new work, not a straight port, and is out of scope for this branch.
