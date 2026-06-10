---
name: android-mobile-recovery
description: Use after Android ADB, Portal HTTP, state, screenshot, accessibility, input, or app-control failures while using mobile-harness.
---

# Android Recovery

Use this only after a concrete failure.

## Classify The Failure

- **No ADB**: `adb devices -l` missing, unauthorized, offline, or empty.
- **No Portal package**: `pm list packages com.mobilerun.portal` returns nothing.
- **No Portal provider**: content query says provider not found.
- **No Portal HTTP**: `/ping` fails or port is not reachable.
- **Bad token**: `/ping` works but `/version` returns `401`.
- **No accessibility state**: HTTP/content provider returns accessibility unavailable or empty state.
- **Input failed**: tap/type returns success but the UI did not change.
- **App blocked**: permission dialog, login wall, credential screen, crash, or frozen UI.

## ADB Recovery

If the device is unauthorized, offline, or missing, stop and tell the user what ADB reported. Do not guess a serial.

If Portal is installed but HTTP is off:

```bash
adb -s <serial> shell content insert --uri content://com.mobilerun.portal/toggle_socket_server --bind enabled:b:true --bind port:i:8080
adb -s <serial> forward tcp:18080 tcp:8080
```

If accessibility is disabled:

```bash
adb -s <serial> shell settings put secure enabled_accessibility_services com.mobilerun.portal/.service.MobilerunAccessibilityService
adb -s <serial> shell settings put secure accessibility_enabled 1
```

If Portal keyboard input is needed:

```bash
adb -s <serial> shell ime enable com.mobilerun.portal/.input.MobilerunKeyboardIME
adb -s <serial> shell ime set com.mobilerun.portal/.input.MobilerunKeyboardIME
```

## Portal HTTP Recovery

If `/ping` fails, the URL or network path is wrong. Ask the user for the correct Portal HTTP base URL.

If `/ping` works but `/version` returns `401`, ask the user for the current bearer token. Do not brute force, scrape, or invent tokens.

If `/state_full` fails but `/version` works, Portal HTTP is authenticated but device permissions may be incomplete. Ask the user to enable Accessibility Service or provide ADB so it can be enabled.

## Action Recovery

After a failed tap or input:

1. Observe again.
2. Check whether a permission dialog, login screen, or keyboard changed the target.
3. Use UI-tree bounds if available. If not - use screenshots.
4. Try one alternative action.
5. If still stuck, stop and report the exact blocker.

## Credential Or Human-Gated Screens

If the blocker is login, API key, payment, account recovery, or consent for destructive action, read the credentials guide under `core/credentials` and ask the user.
