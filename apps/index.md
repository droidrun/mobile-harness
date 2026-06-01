# App Cards

Read only the card for the foreground app id:

```text
apps/android/<package>/CARD.md
apps/ios/<bundle-id>/CARD.md
```

Cards are plain Markdown, not `SKILL.md`, so generic agents do not auto-load every app. Each card should stay focused on stable app-specific facts: package or bundle id, useful selectors, common flows, navigation structure and traps.
