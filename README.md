# mobile-harness

Portable mobile operating instructions for AI agents that already have a way to control Android and/or iOS devices.

This repository is a small Markdown harness. It tells agents how to use Android ADB, Android Mobilerun Portal HTTP, and iOS Portal HTTP, while loading only the platform skill and app card needed for the current task.

## Scope

- Android through ADB and Mobilerun Portal HTTP.
- iOS through `ios-portal` HTTP.

## Loading Model

Start with `AGENTS.md`. It routes agents to the smallest needed file:

- `platforms/android/SKILL.md` for Android work.
- `platforms/ios/SKILL.md` for iOS work.
- `platforms/<platform>/recovery/SKILL.md` only when control fails.
- `core/credentials/SKILL.md` only when a credential or human-gated screen appears.
- `core/memory/SKILL.md` only when reading or writing local agent-owned memory.
- `apps/android/<package>/CARD.md` or `apps/ios/<bundle-id>/CARD.md` only for the foreground app.

Do not load the whole repository into context.

## Android Modes

| ADB | Android Portal HTTP | Mode |
| --- | --- | --- |
| yes | yes | Hybrid: prefer Portal HTTP for state/input/screenshot, use ADB for setup and recovery if needed. |
| yes | no | ADB-only: use raw ADB. |
| no | yes | Portal HTTP-only: use the user-provided Portal base URL and bearer token. |
| no | no | Blocked: ask the user to enable ADB or provide reachable Portal HTTP access. |

Android Portal HTTP-only means the agent already has both:

- a base URL such as `http://127.0.0.1:18080`
- a bearer token for `Authorization: Bearer <token>`

Install and enable Portal if ADB is not available: https://github.com/droidrun/mobilerun-portal

## iOS Mode

iOS has one active capability mode:

- `iOS Portal HTTP`: `MOBILE_HARNESS_IOS_PORTAL_URL` is reachable and `GET /device/date`, `GET /state`, and `GET /vision/screenshot` work.
- `Blocked`: no reachable iOS Portal. Start `ios-portal` check info: https://github.com/droidrun/ios-portal

The default local iOS Portal example is `http://127.0.0.1:6643`.

## Local State

`memory/` and `credentials/` are local, ignored folders. The repository tracks only their rules/templates. Agents may write operational memory after reading `core/memory/SKILL.md`.
