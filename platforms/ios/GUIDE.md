---
name: ios-mobile-harness
description: Use for iOS device or Simulator control through mobilerun-core over cloud, mobilerun-ios local HTTP, or the deprecated ios-portal app on Simulator. Defines cloud and local iOS modes, observe-act-verify rules, and app-card loading.
---

# iOS Mobile Harness

Use this when operating an iPhone, iPad, or iOS Simulator through Mobilerun
Cloud, `mobilerun-ios`, or the deprecated `ios-portal` app.

## Scope

- iOS only.
- Primary API is `mobilerun_core.Mobilerun`.
- Cloud iOS uses `backend="cloud"`.
- Local iOS uses `backend="local-ios-http"`. It detects which local server
  answers at the URL on the first device call:
  - **`mobilerun-ios --local <udid>`** for a USB-connected iPhone or iPad.
    This is the default local path.
  - **`ios-portal` app** for the iOS Simulator only. `ios-portal` is
    deprecated; `mobilerun-ios` cannot drive Simulators.
- Local iOS requires `mobilerun-core` installed with the `local` extra, or `mobilerun-core-local` installed alongside it.
- Driving `mobilerun-ios` requires a `mobilerun-core` release with
  `mobilerun-ios` support. An older release fails against a running
  `mobilerun-ios` server with `ConnectionError: Could not connect to iOS
  portal ... Mobilerun Portal app`. Treat that as a confirmed version
  incompatibility and read `UPDATE.md`.

## Primary Control

```python
from mobilerun_core import Mobilerun

m = Mobilerun()

# Cloud iOS.
device = m.connect("<cloud-device-id>", backend="cloud")

# Local iPhone through mobilerun-ios --local.
device = m.connect(backend="local-ios-http", url="http://127.0.0.1:8080")

# mobilerun-ios started with --local-token.
device = m.connect(backend="local-ios-http", url="http://127.0.0.1:8080", token="...")

# Simulator through the deprecated ios-portal app.
device = m.connect(backend="local-ios-http", url="http://127.0.0.1:6643")

device.ui()
device.screenshot()
device.start_app("com.apple.Preferences")
device.key("home")
```

Use `MOBILERUN_IOS_PORTAL_URL` to omit `url=` and `MOBILERUN_IOS_PORTAL_TOKEN`
to omit `token=`.

After connecting, observe once with `device.ui()`, then inspect
`device.capabilities` and use `device.supports(...)` before optional
operations. On `local-ios-http`, `capabilities` never touches the network:
before the first device call it lists only what both local servers share, so
`supports("stop_app")` is `False` until `ui()` has run. `supports(...)` takes
action names; check key names against `device.capabilities["buttons"]`.

| Capability | `mobilerun-ios` | `ios-portal` (Simulator) |
| --- | --- | --- |
| `ui`, `screenshot`, `time`, `tap`, `swipe`, `type`, `clear_input`, `start_app` | yes | yes |
| `stop_app`, `list_apps` | yes | no |
| `install_app` | yes; the path or URL is read on the host running `mobilerun-ios` | no |
| `uninstall_app`, `execute_script` | no | no |
| `key` names | `home`, `back`, `enter`, `delete`, `app_switch` | `home` |

Other key names raise `UnsupportedOperation`.

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

Use the `device` returned by `Mobilerun.connect(...)`. The foreground bundle
id is `device.current_app_id()` (also `ui()["phone_state"]["bundle_id"]`).
The raw `ui()["a11y_tree"]` shape differs between `mobilerun-ios` and
`ios-portal`; search it with these helpers instead of walking it directly.

- `device.find_nodes(...)` searches the accessibility tree. `any_contains=`
  matches case-insensitive substrings across text, content description,
  resource id, and accessibility identifier. Nodes may carry `offscreen: True`
  or `hidden: True` when the tree source reports visibility. A missing flag is
  not proof of visibility; local iOS tree sources may not emit them.
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
- `device.clear_input()` is supported by both local iOS servers.
- `device.list_apps()` excludes system apps such as Settings and Safari by
  default. Pass `include_system_apps=True` for a full inventory.
- `device.wait_for_app("com.apple.springboard")` after `key("home")` or
  `stop_app(...)`; the foreground app changes about two seconds later.

Accessibility bounds, `tap`, and `swipe` use iOS points. `device.screenshot()`
is a base64 PNG in device pixels, which is larger (3x on current iPhones).
Derive tap targets from nodes, or scale screenshot pixels to points first.

`key("back")` on `mobilerun-ios` performs the left-edge back swipe and can
fail silently. Verify with `device.ui()`; if the screen did not change, tap
the navigation bar's back button instead.

## Local iOS Servers

Two local iOS servers exist. `backend="local-ios-http"` drives both:

- **`mobilerun-ios --local <udid>`**: a host-side server for USB-connected
  devices, default `http://127.0.0.1:8080`, one port per attached device
  (probe 8080-8089). Contract: `GET /ping`, `GET /version`,
  `GET /state_full`, `GET /screenshot`. Tokenless unless started with
  `--local-token` (mandatory for non-loopback binds); then pass `token=` or
  set `MOBILERUN_IOS_PORTAL_TOKEN`. Setup guide:
  https://docs.mobilerun.ai/guides/connect-iphone
- **`ios-portal` app** (deprecated, Simulator only): default
  `http://127.0.0.1:6643`, one port per device (probe 6643-6652), no token.
  Contract: `GET /device/date`, `GET /state`, `GET /vision/screenshot`.

To find a running server, probe both port ranges:

```bash
for p in $(seq 8080 8089); do curl -sS --max-time 3 -w " [%{http_code}] <- $p\n" "http://127.0.0.1:$p/version"; done
for p in $(seq 6643 6652); do curl -sS --max-time 3 -w " [%{http_code}] <- $p\n" "http://127.0.0.1:$p/device/date"; done
```

Each line prints the response body followed by the HTTP status; `[000]` means
no HTTP response at all.

Interpret the responses:

- A 200 body like `{"status":"success","result":"iosportal(..."}` on
  `/version` identifies a `mobilerun-ios --local` server. Only the
  `iosportal(` prefix inside the JSON `result` field is decisive.
- A 200 JSON body with a `date` field on `/device/date` identifies the
  `ios-portal` app.
- A 401/403 on `/version` counts as a server only if the same port answers
  `GET /ping` with the unauthenticated `pong` envelope; both portals exempt
  `/ping` from auth. With the `pong` it is either a `mobilerun-ios --local`
  server started with `--local-token` or a forwarded Android Portal without a
  bearer token; ask the user which server owns the port and for its token.
  Without the `pong` it is an unrelated authenticated service.
- A `pong` from `/ping` is ambiguous; the Android Portal answers the same.
- Anything else (404, HTML, connection refused) means an unrelated server or
  no server.

Connect to an identified server with `backend="local-ios-http"` and its base
URL (set `MOBILERUN_IOS_PORTAL_URL` or pass `url=`).

Neither `/version` nor `/device/date` says which device a server serves. On a
host with several attached devices, correlate first:

```bash
ps ax -o pid,command | grep -E "mobilerun-ios|xcodebuild" | grep -v grep
```

A `mobilerun-ios --local` process's arguments show the UDIDs it was started
with and may include a `--local-token` value; never repeat that value in
output or chat (none when it auto-discovered devices; its startup log prints the device
behind each URL in a `serving local droidrun portal` line). An `ios-portal`
`xcodebuild` process shows the simulator name or id in its `-destination`
argument. If ownership stays unclear, ask the user.

Do not start a second server for a device that already has one; one
`mobilerun-ios` process owns a device at a time and a second one exits with
`device ... is busy`.

## Capability Classification

Classify before acting:

1. **Cloud**: the user provided a Mobilerun Cloud device id. Use `backend="cloud"`.
2. **Local `mobilerun-ios`**: a port in 8080-8089 answers `/version` with an
   `iosportal(` result, or with 401/403 plus a `/ping` `pong` and the user
   supplied the `--local-token` value.
3. **Local `ios-portal`** (Simulator): a port in 6643-6652 answers
   `/device/date` with a `date` field.
4. **Blocked**: no cloud device id and no local server. Run the port probe in
   "Local iOS Servers" before concluding this. Then stop and ask the user to
   provide a cloud device, start `mobilerun-ios --local <udid>` for an
   iPhone or iPad, or start `ios-portal` for a Simulator.

Cloud requires `MOBILERUN_CLOUD_API_KEY`, `MOBILERUN_API_BASE_URL`, and
`MOBILERUN_CLOUD_DEVICE_ID`. Use
`MOBILERUN_API_BASE_URL=https://api.mobilerun.ai/v1` unless the user provides a
different endpoint.

Use `http://127.0.0.1:8080` as the default local example.
For cloud devices, skip local iOS setup checks and recovery unless the user
also provided a local iOS target.

## Setup Checks

For a USB-connected iPhone or iPad, with the device unlocked, trusted, and in
Developer Mode:

```bash
mobilerun-ios --version
mobilerun-ios list
mobilerun-ios verify <udid>
mobilerun-ios --local <udid>
```

Install the CLI with `brew install droidrun/tap/mobilerun-ios` when it is
missing. Keep `mobilerun-ios --local` running, then confirm in another
terminal:

```bash
curl -fsS http://127.0.0.1:8080/ping
curl -fsS http://127.0.0.1:8080/version
```

`list` shows only USB devices; Simulators never appear. Local mode needs no
`mobilerun-ios login`.

When `verify` reports a missing developer disk image or runner app,
`mobilerun-ios setup <udid>` mounts the image and signs and installs the
WebDriverAgent runner with the user's Apple signing identity. Ask the user
before running `setup`; it prompts for signing choices unless given
`--backend`, `--identity`, and `--non-interactive`. The device must stay
unlocked while the image mounts.

For a Simulator (deprecated `ios-portal`):

```bash
cd /path/to/ios-portal
./simulator.sh "<simulator-name>"
curl -fsS http://127.0.0.1:6643/device/date
```

## Local HTTP Probes

Raw curl is for health checks and diagnostics only.

`mobilerun-ios`:

```bash
IOS_URL="${MOBILERUN_IOS_PORTAL_URL:-http://127.0.0.1:8080}"
curl -fsS "$IOS_URL/version"
curl -fsS "$IOS_URL/state_full" -o state.json
```

Add `-H "Authorization: Bearer $MOBILERUN_IOS_PORTAL_TOKEN"` when the server
uses `--local-token`.

`ios-portal`:

```bash
curl -fsS http://127.0.0.1:6643/device/date
curl -fsS http://127.0.0.1:6643/state
curl -fsS http://127.0.0.1:6643/vision/screenshot -o screenshot.png
```

Normal actions go through `Mobilerun`:

```python
import os

from mobilerun_core import Mobilerun

url = os.environ.get("MOBILERUN_IOS_PORTAL_URL", "http://127.0.0.1:8080")
m = Mobilerun()
device = m.connect(backend="local-ios-http", url=url)
device.ui()
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

Read or write `local/memory/` only when operational facts would help future runs. Read `core/memory/GUIDE.md` first.
