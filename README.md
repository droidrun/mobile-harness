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

- Android through `mobilerun-core` using local ADB+Portal, Portal HTTP-only, or cloud.
- iOS through `mobilerun-core` using `ios-portal` HTTP or cloud.

## Manual Install

Install the full public control API:

```bash
cd /path/to/mobile-harness
python -m venv .venv
.venv/bin/python -m pip install "mobilerun-core[local]"
.venv/bin/python -c "from mobilerun_core import Mobilerun"
```

Use any compatible Python interpreter to create the venv. 

Tell agents which Python runtime to use:

```text
Use /path/to/mobile-harness/.venv/bin/python for mobile-harness.
```

Base `mobilerun-core` includes cloud support through `mobilerun-sdk`. The
`local` extra installs `mobilerun-core-cli>=0.2.0`, which `mobilerun-core` uses
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


## Local Android Modes

| ADB | Android Portal HTTP | Mode |
| --- | --- | --- |
| yes | yes | `backend="local-android-adb"`: core uses ADB+Portal; raw ADB is recovery. |
| yes | no | `backend="local-android-adb"` may still work for ADB-native input/screenshot recovery only. |
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
