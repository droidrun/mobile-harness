---
name: android-mobile-harness
description: Use for Android phone control through ADB and Mobilerun Portal HTTP. Classifies ADB-only, Hybrid, Portal HTTP-only, and Blocked modes; defines observe-act-verify rules and app-card loading.
---

# Android Mobile Harness

Use this when operating an Android phone with ADB and/or Mobilerun Portal.

## Scope

- Android only.
- Public Portal only: `com.mobilerun.portal`.
- Portal local control is HTTP only.

## Capability Classification

Classify before acting:

1. **Hybrid**: ADB works and Portal HTTP is reachable. Prefer Portal HTTP for state, screenshot, input, and app data; use ADB for setup and recovery.
2. **ADB-only**: ADB works but Portal HTTP is unavailable. Use raw ADB.
3. **Portal HTTP-only**: ADB is unavailable but the user provided a reachable Portal HTTP URL and bearer token. Use HTTP only.
4. **Blocked**: Neither ADB nor reachable authenticated Portal HTTP is available. Stop and ask the user to enable ADB or provide Portal HTTP access.

If ADB works and `pm list packages com.mobilerun.portal` shows Portal installed, but `content://com.mobilerun.portal/version` fails or says provider not found, treat that as a Portal setup failure and read `platforms/android/recovery/SKILL.md`; do not silently downgrade to generic ADB-only mode.

An installed Portal app is not enough for Portal HTTP-only mode. The agent needs both:

- `MOBILE_HARNESS_PORTAL_URL`, for example `http://127.0.0.1:18080`
- `MOBILE_HARNESS_PORTAL_TOKEN`, sent as `Authorization: Bearer <token>`

## ADB Checks

Use ADB when available:

```bash
adb devices -l
adb -s <serial> shell pm list packages com.mobilerun.portal
adb -s <serial> shell content query --uri content://com.mobilerun.portal/version
adb -s <serial> shell content query --uri content://com.mobilerun.portal/auth_token
```

If Portal is installed and ADB is available, enable HTTP on the device and forward it locally:

```bash
adb -s <serial> shell content insert --uri content://com.mobilerun.portal/toggle_socket_server --bind enabled:b:true --bind port:i:8080
adb -s <serial> forward tcp:18080 tcp:8080
```

Then use `http://127.0.0.1:18080` as the Portal URL.

## Portal HTTP Contract

Default device port is `8080`.

- `GET /ping` does not require auth and should return `pong`.
- Every other endpoint requires `Authorization: Bearer <token>`.
- Verify the token with `GET /version` before performing actions.

Examples:

```bash
curl -sS "$MOBILE_HARNESS_PORTAL_URL/ping"
curl -sS -H "Authorization: Bearer $MOBILE_HARNESS_PORTAL_TOKEN" "$MOBILE_HARNESS_PORTAL_URL/version"
curl -sS -H "Authorization: Bearer $MOBILE_HARNESS_PORTAL_TOKEN" "$MOBILE_HARNESS_PORTAL_URL/state"
curl -sS -H "Authorization: Bearer $MOBILE_HARNESS_PORTAL_TOKEN" "$MOBILE_HARNESS_PORTAL_URL/screenshot" -o screenshot.png
```

Common POST actions:

```bash
curl -sS -X POST -H "Authorization: Bearer $MOBILE_HARNESS_PORTAL_TOKEN" -H "Content-Type: application/json" \
  -d '{"x":540,"y":1200}' "$MOBILE_HARNESS_PORTAL_URL/action/tap"

curl -sS -X POST -H "Authorization: Bearer $MOBILE_HARNESS_PORTAL_TOKEN" -H "Content-Type: application/json" \
  -d '{"startX":540,"startY":1800,"endX":540,"endY":600,"duration":400}' "$MOBILE_HARNESS_PORTAL_URL/action/swipe"

curl -sS -X POST -H "Authorization: Bearer $MOBILE_HARNESS_PORTAL_TOKEN" -H "Content-Type: application/json" \
  -d '{"package":"com.android.settings"}' "$MOBILE_HARNESS_PORTAL_URL/action/app"
```

For text input through Portal, send base64 text:

```bash
curl -sS -X POST -H "Authorization: Bearer $MOBILE_HARNESS_PORTAL_TOKEN" -H "Content-Type: application/json" \
  -d '{"base64_text":"aGVsbG8=","clear":true}' "$MOBILE_HARNESS_PORTAL_URL/action/keyboard/input"
```

## ADB-Only Fallback

```bash
adb -s <serial> exec-out screencap -p > screenshot.png
adb -s <serial> exec-out uiautomator dump /dev/tty
adb -s <serial> shell input tap <x> <y>
adb -s <serial> shell input swipe <x1> <y1> <x2> <y2> <duration_ms>
adb -s <serial> shell input keyevent 4
adb -s <serial> shell monkey -p <package> 1
adb -s <serial> shell pm list packages
```

Prefer UI-tree coordinates over guessed screenshot coordinates when possible. But if UI tree is not available 
or is not suitable for some reasons, use the screenshots.

## Observe-Act-Verify Loop

1. Observe current state before acting.
2. Identify foreground package and activity.
3. Load `apps/android/<package>/CARD.md` if present and not already loaded this turn.
4. Act once.
5. Observe again and verify the expected change.
6. If the expected change did not happen, read `platforms/android/recovery/SKILL.md`.

Do not chain many actions blindly.

## Credential Gate

If the screen asks for a username, password, API key, OTP, 2FA, payment detail, recovery code, or other secret, stop. Read `core/credentials/SKILL.md` and ask the user how to proceed before entering or reading secrets.

## App Cards

App cards are not auto-loaded. When the foreground package is known:

```bash
test -f apps/android/<package>/CARD.md && sed -n '1,220p' apps/android/<package>/CARD.md
```

Read only the current package card. Do not scan every app card.

## Memory

Read or write `memory/` only when operational facts would help future runs. Read `core/memory/SKILL.md` first. Never store secrets or private screen content.
