# mobile-harness-android Plan

## Goal

Create a local Android-only Markdown harness that helps external agents operate phones through ADB and public Mobilerun Portal HTTP without becoming an agent runtime.

## Decisions

- Keep one repository: `mobile-harness-android`.
- Use public Portal only: `com.mobilerun.portal`.
- Use HTTP only for Portal local control.
- Keep default context small with `AGENTS.md` as a router.
- Store app cards as `CARD.md`, not `SKILL.md`, to avoid broad auto-loading.
- Treat `memory/` as an agent-owned local wiki.
- Treat `credentials/` as local ignored user-provided secret notes, gated by explicit user approval.

## Deliverables

- Root router instructions.
- Android core skill with capability modes.
- Recovery, memory, and credentials skills.
- Sample app cards.
- Validation script for Markdown structure.
- Emulator smoke script for ADB/Portal HTTP assumptions.

## Verification

- Run `python3 scripts/validate_docs.py`.
- Run `python3 scripts/emulator_smoke.py --serial <serial>` against a running emulator when ADB is available.
- Inspect git status and commit with a conventional commit message.
