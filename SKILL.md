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

Use `Mobilerun()` to connect to cloud devices, local Android ADB+Portal, local
Android Portal HTTP-only, or local iOS Portal HTTP. Do not import or call
`mobilerun_core_cli` directly for normal agent work. `mobilerun-core-cli` is the
local-driver dependency used internally by `mobilerun-core` for Android and iOS
local backends.

## Load Order

1. Read `AGENTS.md`.
2. Read `platforms/android/SKILL.md` for Android work.
3. Read `platforms/ios/SKILL.md` for iOS work.
4. Read recovery, credentials, memory, and app-card files only when routed
   there by `AGENTS.md` or the platform skill.

For setup and runtime registration, read `install.md`.
