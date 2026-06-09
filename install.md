# mobile-harness installation

Use this file for installing the Python dependency and registering this
Markdown harness with an agent runtime. For day-to-day device work, start with
`AGENTS.md` or `SKILL.md`.

## Python Dependency

Install the full `mobilerun-core` surface:

```bash
python -m pip install "mobilerun-core[local]"
```

Base `mobilerun-core` includes cloud support through `mobilerun-sdk`. The
`local` extra installs `mobilerun-core-cli>=0.2.0`, which `mobilerun-core` uses
internally for:

- local Android ADB+Portal: `backend="local-android-adb"`
- local Android Portal HTTP-only: `backend="local-android-http"`
- local iOS Portal HTTP: `backend="local-ios-http"`

Agents should still import only `mobilerun_core`:

```python
from mobilerun_core import Mobilerun
```

Do not teach agents to use `mobilerun_core_cli` directly for normal control.

## Environment

Cloud devices require:

```bash
export MOBILERUN_CLOUD_API_KEY="..."
export MOBILERUN_API_BASE_URL="https://api.mobilerun.ai/v1"
```

Local Android Portal HTTP-only requires:

```bash
export MOBILERUN_ANDROID_PORTAL_URL="http://127.0.0.1:18080"
export MOBILERUN_ANDROID_PORTAL_TOKEN="..."
```

Local iOS Portal can use:

```bash
export MOBILERUN_IOS_PORTAL_URL="http://127.0.0.1:6643"
```

Do not print tokens or API keys in logs, chat, screenshots, or summaries. If an
existing runtime exposes a differently named Mobilerun key, map it into
`MOBILERUN_CLOUD_API_KEY` before running `mobilerun-core` code.

## Runtime Registration

Keep the repository together when registering it. The root `SKILL.md` and
`AGENTS.md` depend on files under `platforms/`, `core/`, `apps/`, `memory/`,
and `credentials/`.

### Codex

Register the full repository as a Codex skill directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn "$PWD" "${CODEX_HOME:-$HOME/.codex}/skills/mobile-harness"
```

New Codex sessions can then load `mobile-harness` as a skill while preserving
relative file paths.

### Claude Code

Add an import to `~/.claude/CLAUDE.md` that points at this repository's
`AGENTS.md`, for example:

```markdown
@~/Developer/mobile-harness/AGENTS.md
```

Keep the repository at that path so relative references such as
`platforms/android/SKILL.md` remain readable.

### OpenClaw

This repository is a Python `mobilerun-core` harness, separate from the
existing curl-first OpenClaw Mobilerun skill. If packaging it for OpenClaw,
package the repository as a skill directory with the root `SKILL.md` as the
entrypoint and make the whole directory available to the agent.

Before running device-control code in OpenClaw, install:

```bash
python -m pip install "mobilerun-core[local]"
```

Provide the same environment variables listed above. If the host already
provides `MOBILERUN_API_KEY`, set `MOBILERUN_CLOUD_API_KEY` to that value for
`mobilerun-core`.
