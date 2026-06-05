# mobile-harness

Portable mobile operating instructions for AI agents that control Android and/or iOS devices through `mobilerun-core`.

This repository is a small Markdown harness. The primary control path is the Python `mobilerun_core` API; Android ADB, Android Mobilerun Portal HTTP, and iOS Portal HTTP are backend details or recovery/debugging paths.

## Scope

- Android through `mobilerun-core` using local ADB+Portal, Portal HTTP-only, or cloud.
- iOS through `mobilerun-core` using `ios-portal` HTTP or cloud.

## Primary API

```python
from mobilerun_core import Mobilerun

m = Mobilerun()
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

Use `device.capabilities` or `device.supports("stop_app")` before optional lifecycle verbs.

## Loading Model

Start with `AGENTS.md`. It routes agents to the smallest needed file:

- `platforms/android/SKILL.md` for Android work.
- `platforms/ios/SKILL.md` for iOS work.
- `platforms/<platform>/recovery/SKILL.md` only when control fails.
- `core/credentials/SKILL.md` only when a credential or human-gated screen appears.
- `core/memory/SKILL.md` only when reading or writing local agent-owned memory.
- `apps/android/<package>/CARD.md` or `apps/ios/<bundle-id>/CARD.md` only for the foreground app.

Do not load the whole repository into context.

## Android Modes

| ADB | Android Portal HTTP | Mode |
| --- | --- | --- |
| yes | yes | `backend="local-android-adb"`: core uses ADB+Portal; raw ADB is recovery. |
| yes | no | `backend="local-android-adb"` may still work for ADB-native input/screenshot recovery only. |
| no | yes | `backend="local-android-http"` with the user-provided Portal base URL and bearer token. |
| no | no | Blocked: ask the user to enable ADB or provide reachable Portal HTTP access. |

Android Portal HTTP-only means the agent already has both:

- a base URL such as `http://127.0.0.1:18080`
- a bearer token for `Authorization: Bearer <token>`

Install and enable Portal if ADB is not available: https://github.com/droidrun/mobilerun-portal

## iOS Mode

iOS has one active capability mode:

- `iOS Portal HTTP`: `backend="local-ios-http"` with `MOBILERUN_IOS_PORTAL_URL` or an explicit URL. `GET /device/date`, `GET /state`, and `GET /vision/screenshot` must work.
- `Blocked`: no reachable iOS Portal. Start `ios-portal` check info: https://github.com/droidrun/ios-portal

The default local iOS Portal example is `http://127.0.0.1:6643`.

## Local State

`memory/` and `credentials/` are local, ignored folders. The repository tracks only their rules/templates. Agents may write operational memory after reading `core/memory/SKILL.md`.
