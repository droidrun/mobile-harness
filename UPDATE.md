# mobile-harness update

Use this file to keep an installed mobile-harness clone current. For
first-time setup, read `install.md`.

`<harness-root>` below is the directory containing this repository's
`AGENTS.md`. When the harness is loaded through a CLAUDE.md import or a skill
symlink, resolve the real repository path first.

## Soft Update (default)

Run once per session, before platform work:

```bash
git -C <harness-root> pull --ff-only
```

Handle the result:

- Updated or already up to date: continue.
- Offline or network failure: continue with the current version. Do not retry
  in a loop and do not report it as an error.
- `Not possible to fast-forward`, diverged history, or local-changes errors:
  the clone needs repair. See Force Update.

The soft update never overwrites local changes.

## Force Update (repair)

Force update resets the clone to the remote state and discards local
modifications to tracked files:

```bash
git -C <harness-root> fetch origin
git -C <harness-root> reset --hard origin/main
```

Rules:

- Ask the user before running it. Tell them what the soft update refused
  (dirty files, diverged history) and that local edits to tracked harness
  files will be lost.
- Never run `git clean -x`, `git clean -fdx`, or delete untracked files.
  `memory/`, `credentials/`, and `.venv/` live inside this repository as
  ignored directories. `reset --hard` leaves them alone; `git clean -x`
  destroys them.
- Do not repair a development checkout. If the user says the clone is where
  they edit the harness itself, stop and let them resolve it.

## Update Python Dependencies

The git pull only refreshes this Markdown harness. The control libraries
(`mobilerun-core`, and the `local` extra's `mobilerun-core-cli` /
`mobilerun-sdk`) live in `.venv/` and are versioned separately on PyPI — a
clone can be on the latest harness commit while its libraries are months
behind. Upgrade them in the same once-per-session pass, right after the git
pull:

```bash
<harness-root>/.venv/bin/python -m pip install -U "mobilerun-core[local]"
<harness-root>/.venv/bin/python -c "from mobilerun_core import Mobilerun"
```

The `-U` upgrades `mobilerun-core` and its `local`-extra dependencies to the
newest compatible releases. Handle the result like the soft update:

- Upgraded or already current: continue.
- Offline or network failure: continue with the installed version. Do not
  retry in a loop and do not report it as an error.
- Major-version bumps (e.g. `0.x` → `1.x`) can change behavior. If something
  that worked before now fails, note the installed version when reporting.

Skip the upgrade only when the user has pinned a specific library version or
says the clone is a development checkout they manage themselves.

## After Updating

- Files read earlier in this session may be stale. Re-read a guide before
  relying on it.
- If the update changed `AGENTS.md`, re-read it before continuing.
- If `from mobilerun_core import Mobilerun` still fails after the dependency
  upgrade above, read `install.md` and reinstall `mobilerun-core[local]` into
  `.venv/`.
