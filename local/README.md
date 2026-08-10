# Local Overlay

Your own harness content, kept out of git. Mirror any tracked path under
`local/` and the agent reads your version on top of the shipped one.

Everything under `local/` is gitignored except this README, so
`git pull --ff-only` at session start never conflicts with your edits — and an
upstream change to a file you have overridden still fast-forwards cleanly.

## Use It For

App cards, mainly:

```text
local/apps/android/<package>/CARD.md
local/apps/ios/<bundle-id>/CARD.md
```

Two cases:

- **Override a shipped card.** Same path under `local/` as the tracked card.
  Your file is read after it, and your content wins where the two disagree.
- **Add a card for an app the harness does not ship.** Only your file exists,
  so it simply is the card. Internal builds and private apps belong here.

No index to update — cards are found by path.

## Precedence

The agent reads the tracked file first, then yours. On any conflict, yours
wins. State a disagreement outright when you mean to override rather than add:

```markdown
## Overrides

- The shipped card says the account switcher is top-right. On this build it is
  in the drawer header instead.
```

## Not The Same As `memory/`

| Directory | Written by | Weight |
| --- | --- | --- |
| `local/` | you | authoritative — the agent obeys it |
| `memory/` | the agent | provisional — re-verified before use, and `scripts/curate.py` may promote it into shared `core/` knowledge |

Put anything you want obeyed here, not in `memory/`. `scripts/curate.py` does
not read `local/`, so nothing personal leaks into a shared promotion.

## Do Not Store

Credentials, tokens, OTPs, or payment data — `credentials/` is the slot for
those, and only when you explicitly ask for it. `local/` is gitignored, not
encrypted.

## Backing Up

One directory holds all of it, so copying `local/` to another machine moves
every customization at once. Note that `git clean -xdf` deletes ignored
files — it will remove `local/` along with `memory/` and `credentials/`.
