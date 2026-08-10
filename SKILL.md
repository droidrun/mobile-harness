---
name: mobile-harness
description: Portable Android and iOS device-control harness for agents using mobilerun-core.
---

# mobile-harness

Use this harness when an agent needs to control Android or iOS devices through
Mobilerun.

Start by reading `AGENTS.md`. It routes you to the smallest platform file for
the current task.

## Primary Control Model

Normal device control always uses:

```python
from mobilerun_core import Mobilerun
```

Use `Mobilerun()` to connect to cloud devices, local Android ADB with optional
Portal, local Android Portal HTTP-only, or local iOS Portal HTTP. Do not import
or call `mobilerun_core_local` directly for normal agent work. `mobilerun-core-local` is the
local-driver dependency used internally by `mobilerun-core` for Android and iOS
local backends.

## Load Order

1. Read `AGENTS.md`.
2. Read `core/mobile-ux-primitives/GUIDE.md` before observing an unfamiliar screen — cross-platform, load it before the platform split below.
3. Read `platforms/android/GUIDE.md` for Android work.
4. Read `platforms/ios/GUIDE.md` for iOS work.
5. Read recovery, credentials, memory, and app-card files only when routed
   there by `AGENTS.md` or the platform guide. For an in-app action failure or
   a dialog/permission prompt (not a connectivity failure), that means
   `core/debugging/GUIDE.md` or `core/blockers/GUIDE.md`.
6. After any tracked file you load, read the same path under `local/` if it
   exists. That is the user's own copy and it wins on conflict. See
   `local/README.md`.

For setup and runtime registration, read `install.md`.
