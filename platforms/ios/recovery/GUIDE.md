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

- **No iOS Portal**: `MOBILERUN_IOS_PORTAL_URL` is missing or `/device/date` cannot be reached. Run Portal Triage before Setup Recovery.
- **Portal server exited**: requests start failing after earlier success, usually because the XCTest runner stopped.
- **State extraction failure**: `/state` returns HTTP 200 but required state fields are missing or repeatedly empty while the UI is stable.
- **Screenshot failure**: `/vision/screenshot` is non-PNG, zero bytes, or times out.
- **Input failed**: tap/type returns success but the UI did not change. If this repeats, treat it as an action failure — read `core/debugging/GUIDE.md`'s retry rules rather than continuing to retry connection-level fixes here.
- **App blocked by a dialog or permission prompt**: read `core/blockers/GUIDE.md` to classify and clear it — this is not a connection problem.
- **App blocked by Crash or frozen UI**: a genuine app/device problem, not covered by `core/blockers` or `core/debugging`; try relaunching the app once, then stop and report if it recurs.

## Portal Triage

A failed `/device/date` probe does not prove that no portal is running. The
`mobilerun-ios --local <udid>` server takes one port per attached device
starting at 8080 and serves none of `/device/date`, `/state`, or
`/vision/screenshot`. Probe both port ranges and interpret the responses by
the rules in "Two Local iOS Portals" in `platforms/ios/GUIDE.md`:

```bash
for p in $(seq 8080 8089); do curl -sS --max-time 3 -w " [%{http_code}] <- $p\n" "http://127.0.0.1:$p/version"; done
for p in $(seq 6643 6652); do curl -sS --max-time 3 -w " [%{http_code}] <- $p\n" "http://127.0.0.1:$p/device/date"; done
```

Each line prints the response body followed by the HTTP status; `[000]` means
no HTTP response at all.

If a `/version` body's `result` field starts with `iosportal(`, a
`mobilerun-ios --local` server is running; `backend="local-ios-http"` cannot
connect to it. Neither `/version` nor `/device/date` says which device a
server serves. On a multi-device host, correlate every hit with the target
via `ps ax -o pid,command | grep -E "mobilerun-ios|iproxy|xcodebuild"`: a
`--local` server's arguments show the UDIDs it was started with, and its
startup log prints the device behind each URL; an `iproxy` process shows the
UDID behind each forwarded Portal app port; an `xcodebuild` process shows a
Portal app's simulator name or device id in its `-destination` argument.
When a `--local` server serves the target device, do not start a
second portal next to it; report the mismatch and ask the user whether to
switch to the Portal app. When ownership stays unclear, ask the user. A 401/403 counts as a
portal only if the same port that returned it answers
`curl -sS --max-time 3 "http://127.0.0.1:<port>/ping"` with the
unauthenticated `pong` envelope; both portals exempt `/ping` from auth. With the `pong` it is
a token-protected `mobilerun-ios --local` or a forwarded Android Portal; ask
the user which server owns the port. Without the `pong` it is an unrelated
authenticated service.

A `/device/date` hit that serves the target device means its Portal app is
already running on that port; do not run Setup Recovery. Verify the port with
the probes in "iOS Portal HTTP Contract" in `platforms/ios/GUIDE.md`, then
reconnect through `Mobilerun` with `backend="local-ios-http"` and that base
URL (set `MOBILERUN_IOS_PORTAL_URL` or pass `url=`).

Continue with Setup Recovery when no port returned a portal-shaped response
(no `iosportal(` `/version` result, no 401/403 corroborated by a `/ping`
`pong`, and no `/device/date` body with a `date` field), or when every
portal-shaped hit serves a device other than the target. Another device's
healthy portal never blocks recovery of the target, but its port stays taken;
follow the port-in-use rule in Setup Recovery. Unrelated HTTP answers (404,
HTML, or 401/403 without the `pong`) do not block Setup Recovery.

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

If the port is already in use by another device's healthy portal, ask the user for a clean port setup; do not stop that portal. If it is held by a stale process for the target device, stop that process. Do not guess a different device.

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
