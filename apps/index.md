# App Cards

Read only the card for the foreground app id:

```text
apps/android/<package>/CARD.md
apps/ios/<bundle-id>/CARD.md
```

Cards are plain Markdown, not `SKILL.md`, so generic agents do not auto-load every app. Each card should stay focused on stable app-specific facts: package or bundle id, useful selectors, common flows, navigation structure and traps.

Cards here are tracked and shared. A user's own card goes at the same path under `local/`, which is gitignored:

```text
local/apps/android/<package>/CARD.md
local/apps/ios/<bundle-id>/CARD.md
```

Read the tracked card first, then the `local/` one; the `local/` one wins where they disagree, and may be the only one that exists. There is nothing to add to this file for either — cards are discovered by path, which is what keeps a local card from ever conflicting with a `git pull`. See `local/README.md`.
