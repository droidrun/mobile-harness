# Local

One ignored root for everything the user or the agent owns. Nothing here is
tracked except this file and the stubs one level down, so the
`git pull --ff-only` in step 1 of `AGENTS.md` never conflicts with your own
content.

```text
local/
  memory/        agent-written operational memory (core/memory/GUIDE.md)
  credentials/   optional user-provided credential notes (core/credentials/GUIDE.md)
  apps/          your own app cards, and overrides for shipped ones
```

## App Cards

A card under `local/apps/` is read after the shipped card at the same path and
wins wherever the two disagree. It may also be the only card that exists —
private and internal apps live here.

```text
apps/android/com.google.android.gm/CARD.md         shipped
local/apps/android/com.google.android.gm/CARD.md   yours, wins on conflict
local/apps/android/com.acme.internal/CARD.md       yours only
```

Cards are found by path, not through a registry, so a local card needs no
`apps/index.md` entry.

## Migrating

Earlier versions kept `memory/` and `credentials/` at the repository root. Copy
anything you have there across, check it landed, then delete the originals:

```bash
cp -an memory/. local/memory/
cp -an credentials/. local/credentials/
```

Both root paths stay git-ignored until you remove them, so an upgrade cannot
expose content you have not moved yet.

## Do Not Store

Credentials, tokens, OTPs, and payment data belong in `local/credentials/`, and
only when you explicitly ask for them. `local/` is ignored by git, not encrypted.
