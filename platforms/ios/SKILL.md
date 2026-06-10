---
name: ios-mobile-harness
description: Use for iOS device or Simulator control through mobilerun-core over cloud or ios-portal HTTP. Defines cloud and iOS Portal HTTP modes, observe-act-verify rules, and app-card loading.
---

# iOS Mobile Harness

Use this when operating an iPhone, iPad, or iOS Simulator through Mobilerun
Cloud or `ios-portal`.

## Scope

- iOS only.
- Primary API is `mobilerun_core.Mobilerun`.
- Cloud iOS uses `backend="cloud"`.
- Local backend is `ios-portal` HTTP.
- Local iOS requires `mobilerun-core` installed with the `local` extra, or `mobilerun-core-cli` installed alongside it.
- No bearer token is required for local iOS Portal.

## Primary Control

```python
from mobilerun_core import Mobilerun

m = Mobilerun()

# Cloud iOS.
device = m.connect("<cloud-device-id>", backend="cloud")

# Local iOS Portal.
device = m.connect(backend="local-ios-http", url="http://127.0.0.1:6643")

device.ui()
device.screenshot()
device.start_app("com.apple.Preferences")
device.key("home")
```

Use `MOBILERUN_IOS_PORTAL_URL` to omit `url=`.

After connecting, inspect `device.capabilities` and use `device.supports(...)`
before optional operations.

## Capability Classification

Classify before acting:

1. **Cloud**: the user provided a Mobilerun Cloud device id. Use `backend="cloud"`.
2. **iOS Portal HTTP**: `MOBILERUN_IOS_PORTAL_URL` is reachable and `GET /device/date`, `GET /state`, and `GET /vision/screenshot` work.
3. **Blocked**: no cloud device id or reachable iOS Portal is available. Stop and ask the user to provide a cloud device or start `ios-portal`.

Cloud requires `MOBILERUN_CLOUD_API_KEY` and `MOBILERUN_API_BASE_URL`. Use
`MOBILERUN_API_BASE_URL=https://api.mobilerun.ai/v1` unless the user provides a
different endpoint.

Use `http://127.0.0.1:6643` as the default local example.
For cloud devices, skip local iOS Portal setup checks and recovery unless the
user also provided a local iOS target.

## Setup Checks

For Simulator:

```bash
cd /path/to/ios-portal
./simulator.sh "<simulator-name>"
curl -fsS http://127.0.0.1:6643/device/date
```

For a physical device:

Option A, script:

```bash
cd /path/to/ios-portal
./device.sh <device-udid>
```

Option B, Xcode:

1. Open `droidrun-ios-portal.xcodeproj`.
2. Select the physical iPhone or iPad as the run destination.
3. Check Signing & Capabilities for the app and UI-test targets.
4. Run Product > Test.

For either physical-device option, keep the XCTest session running. In another
terminal, forward the device port:

```bash
iproxy -u <device-udid> -s 127.0.0.1 6643:6643
curl -fsS http://127.0.0.1:6643/device/date
```

## iOS Portal HTTP Contract

Use `MOBILERUN_IOS_PORTAL_URL` as the base URL. Raw curl is for health checks
and diagnostics only.

Required probes:

```bash
IOS_PORTAL_URL="${MOBILERUN_IOS_PORTAL_URL:-http://127.0.0.1:6643}"
curl -fsS "$IOS_PORTAL_URL/device/date"
curl -fsS "$IOS_PORTAL_URL/state"
curl -fsS "$IOS_PORTAL_URL/vision/screenshot" -o screenshot.png
```

Normal actions go through `Mobilerun`:

```python
import os

from mobilerun_core import Mobilerun

url = os.environ.get("MOBILERUN_IOS_PORTAL_URL", "http://127.0.0.1:6643")
m = Mobilerun()
device = m.connect(backend="local-ios-http", url=url)
device.start_app("com.apple.Preferences")
device.tap(100, 200)
device.swipe(200, 700, 200, 250, 500)
device.type("hello")
device.key("home")
```

## Observe-Act-Verify Loop

1. Observe with `device.ui()` before acting.
2. Identify foreground bundle id/current app when available.
3. Load `apps/ios/<bundle-id>/CARD.md` if present and not already loaded this turn.
4. Act once through `Mobilerun`.
5. Observe again with `device.ui()` and/or `device.screenshot()`.
6. If the expected change did not happen, read `platforms/ios/recovery/SKILL.md`.

Do not chain many actions blindly.

## Credential Gate

If the screen asks for Apple ID, username, password, OTP, 2FA, passcode,
payment detail, or recovery code, stop. Read the credentials skill under
`core/credentials` and ask the user how to proceed before entering or reading
secrets if the credentials are absent.

## App Cards

App cards are not auto-loaded. When the foreground bundle id is known:

```bash
test -f apps/ios/<bundle-id>/CARD.md && sed -n '1,220p' apps/ios/<bundle-id>/CARD.md
```

Read only the current bundle card. Do not scan every app card.

## Memory

Read or write `memory/` only when operational facts would help future runs. Read `core/memory/SKILL.md` first.
