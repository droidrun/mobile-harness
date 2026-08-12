<p align="center">
  <img src="assets/mobile-harness-logo.png" alt="Mobile Harness" width="900" />
</p>

> Portable operating instructions for AI agents controlling Android and iOS devices—locally or in the cloud.

Mobile Harness is a compact Markdown harness, not an agent runtime. Its primary
control path is Python's `mobilerun_core`, with optional client apps where
needed.

## Agent Setup Prompt

Copy paste it into your agent:

```text
Set up https://github.com/droidrun/mobile-harness for me.

Read `install.md` and follow the steps to install `mobile-harness`.
```

## Scope

- Android through `mobilerun-core` using local ADB with optional Portal, Portal HTTP-only, or cloud.
- iOS through `mobilerun-core` using `ios-portal` HTTP or cloud.

## Manual Install

Install the full public control API:

```bash
cd /path/to/mobile-harness
python -m venv .venv
.venv/bin/python -m pip install "mobilerun-core[local]"
.venv/bin/python -c "from mobilerun_core import Mobilerun"
```

Use Python 3.11, 3.12, or 3.13 to create the venv.

Tell agents which Python runtime to use:

```text
Use /path/to/mobile-harness/.venv/bin/python for mobile-harness.
```

Base `mobilerun-core` includes cloud support through `mobilerun-sdk`. The
`local` extra installs `mobilerun-core-local`, which `mobilerun-core` uses
internally for local Android and iOS backends. Agents should still import only
`mobilerun_core`.

## Primary API

```python
from mobilerun_core import Mobilerun

m = Mobilerun()
device = m.connect("<cloud-device-id>", backend="cloud")
device = m.connect("R5CT123456", backend="local-android-adb")
device = m.connect(backend="local-ios-http", url="http://127.0.0.1:6643")
device = m.connect(
    backend="local-android-http",
    url="http://127.0.0.1:18080",
    token="...",
)

device.ui()
device.screenshot()
device.start_app("com.android.settings")
```

After connecting, agents should inspect `device.capabilities` and use
`device.supports(...)` before optional operations.

`device.execute_script("<js>")` runs JavaScript in the device's foreground
Chrome tab and returns its JSON result. Cloud devices only; local backends
raise `UnsupportedOperation`. Gate it with
`device.supports("execute_script")`; the platform guides describe this key's
network-probe behavior and its two server-side errors.

## Common Device Helpers

Use these helpers through the `device` returned by `Mobilerun.connect(...)`:

- `device.find_nodes(...)` searches the accessibility tree. `any_contains=`
  matches case-insensitive substrings across text, content description,
  resource id, and accessibility identifier. Nodes may carry `offscreen: True`
  (outside the viewport; scroll to reach it) and `hidden: True` (reported not
  visible; scrolling alone may not reveal it). A missing flag is not proof of
  visibility.
- `device.tap_node(node)` taps the center of an accessibility node and raises
  if the node has no usable bounds. Before any bounds check, it raises a
  distinct error for a node flagged hidden unless the node is also offscreen.
- `device.tap_text("label")` taps the first on-screen, non-hidden match across
  text, description, resource id, and accessibility identifier. It raises a
  distinct error when matches exist but none are tappable on-screen.
- `device.scroll(direction, distance=0.5, ms=..., verify=False)` scrolls
  content-relative; `verify=True` returns whether the viewport actually moved.
- `device.scroll_until(text_contains=..., direction="down", max_swipes=10)`
  scrolls until a match is on-screen, returning the node or `None`. It stops
  early with `None` when the viewport stops moving; do not re-call it blindly.
- `device.type("text", clear=True)` clears the focused field before typing
  when the backend supports text input. `device.clear_input()` is available on
  local Android ADB and local iOS Portal HTTP.
- `device.list_apps()` excludes system apps by default. Pass
  `include_system_apps=True` when a full inventory is needed and supported.

## Cloud Mode

Cloud devices use the same `Mobilerun` facade:

```bash
export MOBILERUN_CLOUD_API_KEY="..."
export MOBILERUN_API_BASE_URL="https://api.mobilerun.ai/v1"
```

```python
from mobilerun_core import Mobilerun

m = Mobilerun()
device = m.connect("<cloud-device-id>", backend="cloud")
device.ui()
device.screenshot()
device.start_app("com.android.settings")
```

## Loading Model

Skill-based runtimes can load `SKILL.md`; all runtimes should start with
`AGENTS.md`. It routes agents to the smallest needed file:

- `core/mobile-ux-primitives/GUIDE.md` before observing an unfamiliar screen — cross-platform, read before the platform split.
- `platforms/android/GUIDE.md` for Android work.
- `platforms/ios/GUIDE.md` for iOS work.
- `core/debugging/GUIDE.md` or `core/blockers/GUIDE.md` for an in-app action failure or a dialog covering the screen.
- `platforms/<platform>/recovery/GUIDE.md` only when a connectivity/setup/state-extraction failure occurs.
- the credentials guide under `core/credentials` only when a credential or human-gated screen appears.
- `core/memory/GUIDE.md` only when reading or writing local agent-owned memory.
- `core/learn-from-tutorial/GUIDE.md` when the current screen turns out to be the app's own tutorial or onboarding walkthrough.
- `apps/android/<package>/CARD.md` or `apps/ios/<bundle-id>/CARD.md` only for the foreground app.
- the same path under `local/` after any tracked file it loads — your own copy, which wins on conflict. See [Customising Cards Without Merge Conflicts](#customising-cards-without-merge-conflicts).
- `UPDATE.md` only when the session-start `git pull --ff-only` fails.


## Local Android Modes

| ADB | Android Portal HTTP | Mode |
| --- | --- | --- |
| yes | yes | `backend="local-android-adb"`: core uses ADB and automatically uses Portal features when available. |
| yes | no | `backend="local-android-adb"`: core uses ADB-native control, UI, text input, screenshots, and app lifecycle. |
| no | yes | `backend="local-android-http"` with the user-provided Portal base URL and bearer token. |
| no | no | Blocked: ask the user to enable ADB or provide reachable Portal HTTP access. |

Android Portal HTTP-only means the agent already has both:

- a base URL such as `http://127.0.0.1:18080`
- a bearer token for `Authorization: Bearer <token>`

Without ADB, the harness cannot install, enable, port-forward, or fetch a token
for Portal.
Android Mobilerun Portal: https://github.com/droidrun/mobilerun-portal

## Local iOS Mode

Local iOS has one active capability mode:

- `iOS Portal HTTP`: `backend="local-ios-http"` with `MOBILERUN_IOS_PORTAL_URL` or an explicit URL. `GET /device/date`, `GET /state`, and `GET /vision/screenshot` must work.
- `Blocked`: no reachable iOS Portal. Start `ios-portal` check info: https://github.com/droidrun/ios-portal

The default local iOS Portal example is `http://127.0.0.1:6643`.

A second local iOS server exists: `mobilerun-ios --local <udid>`, default
`http://127.0.0.1:8080`, setup guide:
https://docs.mobilerun.ai/guides/connect-iphone. `backend="local-ios-http"`
speaks only the `ios-portal` contract and cannot connect to that server; do
not point it at port 8080. `platforms/ios/GUIDE.md` explains how to tell the
two apart.

## Local State

`local/`, `memory/`, and `credentials/` are local, ignored folders. The repository tracks only their rules/templates.

| Folder | Written by | Weight |
| --- | --- | --- |
| `local/` | you | authoritative — the agent obeys it and never shares it |
| `memory/` | the agent, after reading `core/memory/GUIDE.md` | provisional — re-verified before use |
| `credentials/` | you, and only if you ask for local credential files | secrets; see the guide under `core/credentials` |

## Customising Cards Without Merge Conflicts

Session start runs `git pull --ff-only`, so editing a tracked file breaks your
next update. Put your version under `local/` at the same path instead:

```text
apps/android/com.google.android.gm/CARD.md         # shipped, tracked
local/apps/android/com.google.android.gm/CARD.md   # yours, wins on conflict
local/apps/android/com.acme.internal/CARD.md       # yours only — private/internal apps
```

The agent reads the shipped card first, then yours, and yours wins where the
two disagree. If only yours exists, it simply is the card — which is where
internal builds and private apps belong.

`local/` is gitignored except its README, so the pull keeps fast-forwarding
even when upstream changes a card you have overridden. Cards are found by path,
so there is no index to update. `scripts/curate.py` does not read `local/`,
so nothing personal leaks into a shared promotion.

Full details in `local/README.md`. Note that `git clean -xdf` deletes ignored
files, `local/` included.
