---
name: ios-mobile-recovery
description: Use after iOS Portal HTTP, XCTest session, state, screenshot, accessibility, input, or app-control failures while using mobile-harness.
---

# iOS Recovery

Use this only after a concrete connectivity, setup, or state-extraction
failure. For an in-app action that didn't produce the expected result, read
`core/debugging/GUIDE.md` instead — this file is about the Portal/XCTest
connection, not action-level retry logic.

## Classify The Failure

- **No iOS Portal**: `MOBILERUN_IOS_PORTAL_URL` is missing or `/device/date` cannot be reached.
- **Portal server exited**: requests start failing after earlier success, usually because the XCTest runner stopped.
- **State extraction failure**: `/state` returns HTTP 200 but required state fields are missing or repeatedly empty while the UI is stable.
- **Screenshot failure**: `/vision/screenshot` is non-PNG, zero bytes, or times out.
- **Input failed**: tap/type returns success but the UI did not change. If this repeats, treat it as an action failure — read `core/debugging/GUIDE.md`'s retry rules rather than continuing to retry connection-level fixes here.
- **App blocked by a dialog or permission prompt**: read `core/blockers/GUIDE.md` to classify and clear it — this is not a connection problem.
- **App blocked by Crash or frozen UI**: a genuine app/device problem, not covered by `core/blockers` or `core/debugging`; try relaunching the app once, then stop and report if it recurs.

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

After a failed tap, swipe, type, launch, or key that isn't explained by anything above:

1. Observe again with `/state`.
2. Check whether an app changed the target — a permission dialog or login screen belongs to `core/blockers` or `core/credentials`, not here.
3. Use accessibility/state bounds when available.
4. Use screenshot for verification.
5. Try one alternative action.
6. If still stuck, stop and report the exact blocker.

This overlaps deliberately with `core/debugging/GUIDE.md`'s retry rules — prefer that file for anything that's clearly an in-app action problem rather than a device/backend one; use this section only when you landed here first and haven't already applied that classification.

## Credential Or Human-Gated Screens

If the blocker is Apple ID, login, passcode, OTP, API key, payment, account recovery, captcha, or consent for destructive action, read the credentials guide under `core/credentials` and ask the user if the credentials are not present.
