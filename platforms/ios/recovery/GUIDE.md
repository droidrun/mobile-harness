---
name: ios-mobile-recovery
description: Use after iOS Portal HTTP, XCTest session, state, screenshot, accessibility, input, or app-control failures while using mobile-harness.
---

# iOS Recovery

Use this only after a concrete iOS control failure.

## Classify The Failure

- **No iOS Portal**: `MOBILERUN_IOS_PORTAL_URL` is missing or `/device/date` cannot be reached.
- **Portal server exited**: requests start failing after earlier success, usually because the XCTest runner stopped.
- **State extraction failure**: `/state` returns HTTP 200 but required state fields are missing or repeatedly empty while the UI is stable.
- **Screenshot failure**: `/vision/screenshot` is non-PNG, zero bytes, or times out.
- **Input failed**: tap/type returns success but the UI did not change.
- **App blocked**: Crash or frozen UI.

## Setup Recovery

If Simulator Portal is not running:

```bash
cd /path/to/ios-portal
./simulator.sh "<simulator-name>"
curl -fsS http://127.0.0.1:6643/device/date
```

If a physical-device Portal is not reachable:

```bash
cd /path/to/ios-portal
./device.sh <device-udid>
iproxy -u <device-udid> -s 127.0.0.1 6643:6643
curl -fsS http://127.0.0.1:6643/device/date
```

If the port is already in use, stop the prior portal process or ask the user for a clean port/device setup. Do not guess a different device.

## Action Recovery

After a failed tap, swipe, type, launch, or key:

1. Observe again with `/state`.
2. Check whether an app changed the target.
3. Use accessibility/state bounds when available.
4. Use screenshot for verification.
5. Try one alternative action.
6. If still stuck, stop and report the exact blocker.

## Credential Or Human-Gated Screens

If the blocker is Apple ID, login, passcode, OTP, API key, payment, account recovery, captcha, or consent for destructive action, read the credentials guide under `core/credentials` and ask the user if the credentials are not present.
