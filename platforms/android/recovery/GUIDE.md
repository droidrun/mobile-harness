---
name: android-mobile-recovery
description: Use after Android ADB, Portal HTTP, state, screenshot, accessibility, input, or app-control failures while using mobile-harness.
---

# Android Recovery

Use this only after a concrete connectivity, setup, or state-extraction
failure. For an in-app action that didn't produce the expected result, read
`core/debugging/GUIDE.md` instead — this file is about the backend/device
connection, not action-level retry logic.

## Classify The Failure

- **No ADB**: `adb devices -l` missing, unauthorized, offline, or empty.
- **No Portal package**: `pm list packages com.mobilerun.portal` returns nothing.
- **No Portal provider**: content query says provider not found.
- **No Portal HTTP**: `/ping` fails or port is not reachable.
- **Bad token**: `/ping` works but `/version` returns `401`.
- **No accessibility state**: HTTP/content provider returns accessibility unavailable or empty state.
- **Input failed**: tap/type returns success but the UI did not change. If this repeats, treat it as an action failure — read `core/debugging/GUIDE.md`'s retry rules rather than continuing to retry connection-level fixes here.
- **App blocked by a dialog or permission prompt**: read `core/blockers/GUIDE.md` to classify and clear it — this is not a connection problem.
- **App blocked by a login wall or credential screen**: read the credentials guide under `core/credentials`.
- **App blocked by a crash or frozen UI**: this is a genuine app/device problem, not covered by `core/blockers` or `core/debugging`; try relaunching the app once, then stop and report if it recurs.

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

After a failed tap or input that isn't explained by anything above:

1. Observe again.
2. Check whether a permission dialog, login screen, or keyboard changed the target — if so, this is `core/blockers` or `core/credentials`, not a recovery-file matter.
3. Use UI-tree bounds if available. If not - use screenshots.
4. Try one alternative action.
5. If still stuck, stop and report the exact blocker.

This overlaps deliberately with `core/debugging/GUIDE.md`'s retry rules — prefer that file for anything that's clearly an in-app action problem rather than a device/backend one; use this section only when you landed here first and haven't already applied that classification.

## Credential Or Human-Gated Screens

If the blocker is login, API key, payment, account recovery, or consent for destructive action, read the credentials guide under `core/credentials` and ask the user.
