---
name: ios-mobile-recovery
description: Use after mobilerun-ios or ios-portal HTTP, WebDriverAgent or XCTest session, state, screenshot, accessibility, input, or app-control failures while using mobile-harness.
---

# iOS Recovery

Use this only after a concrete iOS control failure.

## Classify The Failure

- **No local server**: `MOBILERUN_IOS_PORTAL_URL` is missing, or the first
  device call raises `ConnectionError: No iOS portal answered at ...`. Run
  Server Triage before Setup Recovery.
- **Token required**: the same `No iOS portal answered` error while the port
  answers `/ping` with `pong` and `/version` with 401/403. The server runs
  with `--local-token`; ask the user for the token and pass `token=` or set
  `MOBILERUN_IOS_PORTAL_TOKEN`.
- **Outdated mobilerun-core**: `ConnectionError: Could not connect to iOS
  portal ... Mobilerun Portal app` against a port whose `/version` result
  starts with `iosportal(`. The installed `mobilerun-core` predates
  `mobilerun-ios` support; read `UPDATE.md`.
- **Server exited**: requests start failing after earlier success, usually
  because the `mobilerun-ios` process or the Simulator's `ios-portal` XCTest
  runner stopped.
- **Device locked**: `mobilerun-ios verify` or `setup` reports the developer
  disk image is not mounted, or the screen shows only the lock screen. Ask the
  user to unlock the device; the harness cannot bypass the passcode.
- **State extraction failure**: `ui()` returns but required state fields are
  missing or repeatedly empty while the UI is stable.
- **Screenshot failure**: `screenshot()` is not a base64 PNG, is empty, or
  times out.
- **Input failed**: tap/type returns success but the UI did not change.
- **App blocked**: Crash or frozen UI.

## Server Triage

A failed probe on one port does not prove that no server is running. Probe
both port ranges and interpret the responses by the rules in "Local iOS
Servers" in `platforms/ios/GUIDE.md`:

```bash
for p in $(seq 8080 8089); do curl -sS --max-time 3 -w " [%{http_code}] <- $p\n" "http://127.0.0.1:$p/version"; done
for p in $(seq 6643 6652); do curl -sS --max-time 3 -w " [%{http_code}] <- $p\n" "http://127.0.0.1:$p/device/date"; done
```

Each line prints the response body followed by the HTTP status; `[000]` means
no HTTP response at all.

A `/version` result starting with `iosportal(` is a running
`mobilerun-ios --local` server. A `/device/date` body with a `date` field is a
running `ios-portal` app. Neither says which device it serves. On a
multi-device host, correlate every hit with the target via
`ps ax -o pid,command | grep -E "mobilerun-ios|xcodebuild"`: a
`mobilerun-ios` process's arguments show the UDIDs it was started with (do
not repeat a `--local-token` value from them), and its startup log prints the
device behind each URL; an `xcodebuild` process
shows an `ios-portal` Simulator in its `-destination` argument. When
ownership stays unclear, ask the user. A 401/403 counts as a server only if
the same port that returned it answers
`curl -sS --max-time 3 "http://127.0.0.1:<port>/ping"` with the
unauthenticated `pong` envelope; both portals exempt `/ping` from auth. With
the `pong` it is a token-protected `mobilerun-ios --local` or a forwarded
Android Portal; ask the user which server owns the port. Without the `pong`
it is an unrelated authenticated service.

A hit that serves the target device means its server is already running; do
not run Setup Recovery. Reconnect through `Mobilerun` with
`backend="local-ios-http"` and that base URL (set `MOBILERUN_IOS_PORTAL_URL`
or pass `url=`).

Continue with Setup Recovery when no port returned a server-shaped response
(no `iosportal(` `/version` result, no 401/403 corroborated by a `/ping`
`pong`, and no `/device/date` body with a `date` field), or when every
server-shaped hit serves a device other than the target. Another device's
healthy server never blocks recovery of the target, but its port stays taken;
follow the port-in-use rule in Setup Recovery. Unrelated HTTP answers (404,
HTML, or 401/403 without the `pong`) do not block Setup Recovery.

## Setup Recovery

If no `mobilerun-ios` server serves a USB-connected iPhone or iPad:

```bash
mobilerun-ios list
mobilerun-ios verify <udid>
mobilerun-ios --local <udid>
curl -fsS http://127.0.0.1:8080/version
```

- `list` does not show the device: it is not connected over USB, not trusted,
  or a Simulator. Ask the user to connect, unlock, and trust it.
- `verify` reports a missing developer disk image or runner app: ask the user
  before running `mobilerun-ios setup <udid>` (see Setup Checks in
  `platforms/ios/GUIDE.md`).
- `--local` exits with `device ... is busy`: another `mobilerun-ios` process
  owns the device. Use its server instead of starting another; if that process
  is stale, stop it and retry after it has exited.
- `--local` exits because the port is in use: pass a free
  `--local-addr 127.0.0.1:<port>` and connect to that URL.

`mobilerun-ios --local` restarts a wedged WebDriverAgent runner itself. When
requests keep failing while the process is still running, stop it and start
it again.

If the Simulator's `ios-portal` app is not running:

```bash
cd /path/to/ios-portal
./simulator.sh "<simulator-name>"
curl -fsS http://127.0.0.1:6643/device/date
```

If a port is already in use by another device's healthy server, ask the user for a clean port setup; do not stop that server. If it is held by a stale process for the target device, stop that process. Do not guess a different device.

## Action Recovery

After a failed tap, swipe, type, launch, or key:

1. Observe again with `device.ui()`.
2. Check whether an app changed the target.
3. Use accessibility bounds when available; they are in points, not
   screenshot pixels.
4. Use screenshot for verification.
5. Try one alternative action. After a silent `key("back")` failure, tap the
   navigation bar's back button.
6. If still stuck, stop and report the exact blocker.

## Credential Or Human-Gated Screens

If the blocker is Apple ID, login, passcode, OTP, API key, payment, account recovery, or consent for destructive action, read the credentials guide under `core/credentials` and ask the user how to proceed, unless the current action is explicitly authorized.
