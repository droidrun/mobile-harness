---
name: ios-mobile-recovery
description: Use after iOS Portal HTTP, XCTest session, state, screenshot, accessibility, input, or app-control failures while using mobile-harness.
---

# iOS Recovery

Use this only after a concrete iOS control failure.

## Classify The Failure

- **No iOS Portal**: `MOBILERUN_IOS_PORTAL_URL` is missing or `/device/date` cannot be reached. Run Portal Triage before Setup Recovery.
- **Portal server exited**: requests start failing after earlier success, usually because the XCTest runner stopped.
- **State extraction failure**: `/state` returns HTTP 200 but required state fields are missing or repeatedly empty while the UI is stable.
- **Screenshot failure**: `/vision/screenshot` is non-PNG, zero bytes, or times out.
- **Input failed**: tap/type returns success but the UI did not change.
- **App blocked**: Crash or frozen UI.

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
connect to it. `/version` does not say which device it serves. On a
multi-device host, correlate first: `pgrep -af mobilerun-ios` shows the UDIDs
the server was started with, and its startup log prints the device behind
each URL. When it serves the target device, do not start a second portal next
to it; report the mismatch and ask the user whether to switch to the Portal
app. When ownership stays unclear, ask the user. A 401/403 is ambiguous
(token-protected `mobilerun-ios --local` or a forwarded Android Portal); ask
the user which server owns the port.

Continue with Setup Recovery when no port returned a portal-shaped response
(no `iosportal(` `/version` result, no 401/403, and no `/device/date` body
with a `date` field), or when every `iosportal(` hit serves a device other
than the target. Unrelated HTTP answers (404, HTML) do not block Setup
Recovery.

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
