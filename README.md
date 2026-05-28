# mobile-harness-android

Portable Android operating instructions for AI agents that already have a way to use ADB and/or Mobilerun Portal.

This repository is a small Markdown harness that tells agents how to classify Android control capabilities, use ADB and public Mobilerun Portal HTTP safely, load app cards on demand, handle credential screens, and maintain local operational memory. *** Should we keep memory? Or the codex, open claw, claude etc. already have it and having one more memory layer actually makes it worse?

## Scope

- Android only.
- Public Portal only: `com.mobilerun.portal`.
- HTTP only for Portal local control.

## Loading Model

Start with `AGENTS.md`. It routes agents to the smallest needed file:

- `core/android/SKILL.md` for normal Android work.
- `core/recovery/SKILL.md` only when control fails.
- `core/credentials/SKILL.md` only when a credential screen appears or stored app credentials are explicitly authorized.
- `core/memory/SKILL.md` only when reading or writing local agent-owned memory.
- `apps/<package>/CARD.md` only for the foreground app package.

Do not load the whole repository into context.

## Capability Modes

| ADB | Portal HTTP | Mode |
| --- | --- | --- |
| yes | yes | Hybrid: prefer Portal HTTP for state/input/screenshot, use ADB for setup and recovery if needed. |
| yes | no | ADB-only: use raw ADB. |
| no | yes | Portal HTTP-only: use the user-provided Portal base URL and bearer token. |
| no | no | Blocked: ask the user to enable ADB or provide reachable Portal HTTP access. |

Portal HTTP-only means the agent already has both:

- a base URL such as `http://127.0.0.1:18080`
- a bearer token for `Authorization: Bearer <token>`

An installed Portal APK alone is not enough when ADB is unavailable.

## Local State

`memory/` and `credentials/` are local, ignored folders. The repository tracks only their rules/templates. Agents may write operational memory.
