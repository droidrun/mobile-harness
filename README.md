# mobile-harness

Portable mobile operating instructions for AI agents that control Android and/or iOS devices. Local and in cloud.

The repository is a small Markdown harness. The primary control path is the Python `mobilerun_core` and optional client apps.

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
.venv/bin/python -c "from importlib.metadata import version; from mobilerun_core import Mobilerun; print(version('mobilerun-core'))"
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

## Common Device Helpers

Use these helpers through the `device` returned by `Mobilerun.connect(...)`:

- `device.find_nodes(...)` searches the accessibility tree. `any_contains=`
  matches case-insensitive substrings across text, content description,
  resource id, and accessibility identifier.
- `device.tap_node(node)` taps the center of an accessibility node and raises
  if the node has no usable bounds.
- `device.tap_text("label")` finds and taps the first matching text,
  description, resource id, or accessibility identifier.
- `device.type("text", clear=True)` clears the focused field before typing
  when the backend supports text input. `device.clear_input()` is available on
  local Android ADB and local iOS Portal HTTP.
- `device.list_apps()` excludes system apps by default. Pass
  `include_system_apps=True` when a full inventory is needed and supported.

For runtime version checks, prefer package metadata:

```python
from importlib.metadata import version

print(version("mobilerun-core"))
```

Do not rely on module `__version__` constants when checking installed package
versions.

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

- `platforms/android/GUIDE.md` for Android work.
- `platforms/ios/GUIDE.md` for iOS work.
- `platforms/<platform>/recovery/GUIDE.md` only when control fails.
- the credentials guide under `core/credentials` only when a credential or human-gated screen appears.
- `core/memory/GUIDE.md` only when reading or writing local agent-owned memory.
- `apps/android/<package>/CARD.md` or `apps/ios/<bundle-id>/CARD.md` only for the foreground app.
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

## Local State

`memory/` and `credentials/` are local, ignored folders. The repository tracks only their rules/templates. Agents may write operational memory after reading `core/memory/GUIDE.md`.
