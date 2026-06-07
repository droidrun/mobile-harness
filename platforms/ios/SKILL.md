---
name: ios-mobile-harness
description: Use for iOS device or Simulator control through mobilerun-core over ios-portal HTTP. Defines iOS Portal HTTP mode, observe-act-verify rules, and app-card loading.
---

# iOS Mobile Harness

Use this when operating an iPhone, iPad, or iOS Simulator through `ios-portal`.

## Scope

- iOS only.
- Primary API is `mobilerun_core.Mobilerun`.
- Local backend is `ios-portal` HTTP.
- No bearer token is required for the iOS.

## Primary Control

```python
from mobilerun_core import Mobilerun

m = Mobilerun()
device = m.connect(backend="local-ios-http", url="http://127.0.0.1:6643")

device.ui()
device.screenshot()
device.start_app("com.apple.Preferences")
device.key("home")
```

Use `MOBILERUN_IOS_PORTAL_URL` to omit `url=`.

## Capability Classification

Classify before acting:

1. **iOS Portal HTTP**: `MOBILERUN_IOS_PORTAL_URL` or `MOBILE_HARNESS_IOS_PORTAL_URL` is reachable and `GET /device/date`, `GET /state`, and `GET /vision/screenshot` work.
2. **Blocked**: iOS Portal is not reachable. Stop and tell the user to start `ios-portal`.

Use `http://127.0.0.1:6643` as the default local example.

## Setup Checks

For Simulator:

```bash
cd /path/to/ios-portal
./simulator.sh "<simulator-name>"
curl -fsS http://127.0.0.1:6643/device/date
```

For a physical device:

```bash
cd /path/to/ios-portal
./device.sh <device-udid>
iproxy -u <device-udid> 6643 6643
curl -fsS http://127.0.0.1:6643/device/date
```

## iOS Portal HTTP Contract

Use `MOBILERUN_IOS_PORTAL_URL` as the base URL. `MOBILE_HARNESS_IOS_PORTAL_URL`
is a legacy fallback.

Required probes:

```bash
IOS_PORTAL_URL="${MOBILERUN_IOS_PORTAL_URL:-${MOBILE_HARNESS_IOS_PORTAL_URL:-http://127.0.0.1:6643}}"
curl -fsS "$IOS_PORTAL_URL/device/date"
curl -fsS "$IOS_PORTAL_URL/state"
curl -fsS "$IOS_PORTAL_URL/vision/screenshot" -o screenshot.png
```

Common actions:

```bash
IOS_PORTAL_URL="${MOBILERUN_IOS_PORTAL_URL:-${MOBILE_HARNESS_IOS_PORTAL_URL:-http://127.0.0.1:6643}}"

curl -fsS -X POST -H "Content-Type: application/json" \
  -d '{"bundleIdentifier":"com.apple.Preferences"}' "$IOS_PORTAL_URL/inputs/launch"

curl -fsS -X POST -H "Content-Type: application/json" \
  -d '{"rect":"{{100,200},{1,1}}","count":1,"longPress":false}' "$IOS_PORTAL_URL/gestures/tap"

curl -fsS -X POST -H "Content-Type: application/json" \
  -d '{"x1":200,"y1":700,"x2":200,"y2":250,"durationMs":500}' "$IOS_PORTAL_URL/gestures/swipe"

curl -fsS -X POST -H "Content-Type: application/json" \
  -d '{"rect":"{{100,200},{1,1}}","text":"hello"}' "$IOS_PORTAL_URL/inputs/type"

curl -fsS -X POST -H "Content-Type: application/json" \
  -d '{"key":1}' "$IOS_PORTAL_URL/inputs/key"
```

## Observe-Act-Verify Loop

1. Observe with `/state` before acting.
2. Identify foreground bundle id/current app when available.
3. Load `apps/ios/<bundle-id>/CARD.md` if present and not already loaded this turn.
4. Act once through iOS Portal.
5. Observe again with `/state` and/or `/vision/screenshot`.
6. If the expected change did not happen, read `platforms/ios/recovery/SKILL.md`.

Do not chain many actions blindly.

## Credential Gate

If the screen asks for Apple ID, username, password, OTP, 2FA, passcode, payment detail, recovery code stop. Read `core/credentials/SKILL.md` and ask the user how to proceed before entering or reading secrets if the credentials are absent.

## App Cards

App cards are not auto-loaded. When the foreground bundle id is known:

```bash
test -f apps/ios/<bundle-id>/CARD.md && sed -n '1,220p' apps/ios/<bundle-id>/CARD.md
```

Read only the current bundle card. Do not scan every app card.

## Memory

Read or write `memory/` only when operational facts would help future runs. Read `core/memory/SKILL.md` first.
