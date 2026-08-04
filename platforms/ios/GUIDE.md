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
- The local backend `local-ios-http` speaks the `ios-portal` Portal app
  contract only. It cannot drive the `mobilerun-ios --local` server; see
  "Two Local iOS Portals" below.
- Local iOS requires `mobilerun-core` installed with the `local` extra, or `mobilerun-core-local` installed alongside it.
- No bearer token is required for the local iOS Portal app.

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

`device.execute_script("<js>")` runs JavaScript in the device's foreground
Chrome tab and returns its JSON result (`None` when the script returns
`undefined`). Cloud devices only; local backends raise `UnsupportedOperation`.
Gate it with `device.supports("execute_script")`. On cloud connections this
check fetches device capabilities over the network once per connection, a
fetch failure raises instead of returning `False`, and it reports the device
type rather than the current browser state. On local backends it returns
`False` without any network call. `DEVICE_NO_BROWSER_TARGET` means
no debuggable foreground Chrome tab right now; `DEVICE_TOOL_UNSUPPORTED`
(HTTP 400) means the device type has no browser tooling. Neither error is a
connection failure.

## Common Helpers

Use the `device` returned by `Mobilerun.connect(...)`:

- `device.find_nodes(...)` searches the accessibility tree. `any_contains=`
  matches case-insensitive substrings across text, content description,
  resource id, and accessibility identifier. Nodes may carry `offscreen: True`
  or `hidden: True` when the tree source reports visibility. A missing flag is
  not proof of visibility; iOS Portal tree sources may not emit them.
- `device.tap_node(node)` taps the center of a node and fails clearly if bounds
  are missing or unusable. It may also reject a node flagged hidden.
- `device.tap_text("label")` taps the first on-screen match across text,
  description, resource id, and accessibility identifier. It raises a distinct
  error when matches exist but none are tappable on-screen.
- `device.scroll(direction, distance=0.5, ms=..., verify=False)` scrolls
  content-relative: `"down"` reveals rows below. `distance` is a fraction of
  half the screen. `verify=True` returns whether the viewport actually moved,
  at the cost of two extra UI reads; otherwise the call returns `None`.
- `device.scroll_until(text_contains=..., direction="down", max_swipes=10)`
  scrolls until a match is on-screen, returning the node or `None`. On a
  viewport stall it retries once with a stronger swipe, then returns `None`
  early instead of using the whole swipe budget. Do not re-call it blindly.
- `device.type("text", clear=True)` clears the focused field before typing
  when text input is supported.
- `device.clear_input()` is supported by local iOS Portal HTTP.

## Two Local iOS Portals

Two local iOS servers exist and speak incompatible HTTP contracts:

- **iOS Portal app** (`ios-portal`): default `http://127.0.0.1:6643`, one
  port per device (probe 6643-6652), no token. Contract: `GET /device/date`,
  `GET /state`, `GET /vision/screenshot`. This is the only contract
  `backend="local-ios-http"` can drive.
- **`mobilerun-ios --local <udid>`**: a host-side server, default
  `http://127.0.0.1:8080`, one port per attached device (probe 8080-8089). It
  speaks the Android-Portal-style contract (`/ping`, `/version`,
  `/state_full`, `/screenshot`) and serves none of the Portal app endpoints.
  Tokenless unless started with `--local-token` (mandatory for non-loopback
  binds); then `Authorization: Bearer <--local-token value>`. Setup guide:
  https://docs.mobilerun.ai/guides/connect-iphone

To tell them apart, probe both port ranges:

```bash
for p in $(seq 8080 8089); do curl -sS --max-time 3 -w " [%{http_code}] <- $p\n" "http://127.0.0.1:$p/version"; done
for p in $(seq 6643 6652); do curl -sS --max-time 3 -w " [%{http_code}] <- $p\n" "http://127.0.0.1:$p/device/date"; done
```

Each line prints the response body followed by the HTTP status; `[000]` means
no HTTP response at all.

Interpret the responses:

- A 200 body like `{"status":"success","result":"iosportal(..."}` on
  `/version` identifies the `mobilerun-ios --local` server. Only the
  `iosportal(` prefix inside the JSON `result` field is decisive.
- A 200 JSON body with a `date` field on `/device/date` identifies the Portal
  app. If it serves the target device, connect there:
  `backend="local-ios-http"` with that base URL (set
  `MOBILERUN_IOS_PORTAL_URL` or pass `url=`).
- A 401/403 on `/version` counts as a portal only if the same port answers
  `GET /ping` with the unauthenticated `pong` envelope; both portals exempt
  `/ping` from auth. With the `pong` it is either a `mobilerun-ios --local`
  server started with `--local-token` or a forwarded Android Portal without a
  bearer token; ask the user which server owns the port. Without the `pong`
  it is an unrelated authenticated service.
- A `pong` from `/ping` is ambiguous; the Android Portal answers the same.
- Anything else (404, HTML, connection refused) means an unrelated server or
  no server.

Neither `/version` nor `/device/date` says which device a server serves. On a
host with several attached devices, correlate first:

```bash
ps ax -o pid,command | grep -E "mobilerun-ios|iproxy|xcodebuild" | grep -v grep
```

A `--local` server's arguments show the UDIDs it was started with (none when
it auto-discovered devices; its startup log prints the device behind each
URL). An `iproxy` process shows the UDID behind each forwarded Portal app
port. A Portal app's `xcodebuild` process shows the simulator name or device
id in its `-destination` argument. If ownership stays unclear, ask the user.

If the `mobilerun-ios --local` server serves the target device, do not point
`backend="local-ios-http"` at it and do not start a second portal next to it.
Report that `mobilerun_core` cannot drive it and ask the user whether to start
the Portal app instead. A server that serves only other devices does not
block Portal app setup for the target device.

## Capability Classification

Classify before acting:

1. **Cloud**: the user provided a Mobilerun Cloud device id. Use `backend="cloud"`.
2. **iOS Portal HTTP**: `MOBILERUN_IOS_PORTAL_URL` is reachable and `GET /device/date`, `GET /state`, and `GET /vision/screenshot` work.
3. **Blocked**: no cloud device id or reachable iOS Portal is available. Run the port probe in "Two Local iOS Portals" before concluding this; a running `mobilerun-ios --local` server is not "no portal". Then stop and ask the user to provide a cloud device or start `ios-portal`.

Cloud requires `MOBILERUN_CLOUD_API_KEY`, `MOBILERUN_API_BASE_URL`, and
`MOBILERUN_CLOUD_DEVICE_ID`. Use
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
6. If the expected change did not happen, read `platforms/ios/recovery/GUIDE.md`.

Do not chain many actions blindly.

## Credential Gate

If the screen asks for Apple ID, username, password, OTP, 2FA, passcode,
payment detail, or recovery code, stop. Read the credentials guide under
`core/credentials` and ask the user how to proceed before entering or reading
secrets if the credentials are absent.

## App Cards

App cards are not auto-loaded. When the foreground bundle id is known:

```bash
test -f apps/ios/<bundle-id>/CARD.md && sed -n '1,220p' apps/ios/<bundle-id>/CARD.md
```

Read only the current bundle card. Do not scan every app card.

## Memory

Read or write `memory/` only when operational facts would help future runs. Read `core/memory/GUIDE.md` first.
