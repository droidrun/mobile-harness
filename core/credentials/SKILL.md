---
name: credentials
description: What to do when a screen asks for a password, OTP/2FA code, payment/purchase confirmation, biometric unlock, or any other secret or authorization the agent wasn't explicitly given. Load this on every run, alongside core/mobile-ux-primitives. Referenced by the mandatory Traps line in every app's CARD.md.
homepage: https://github.com/droidrun/mobile-harness
metadata:
  tier: core
  scope: cross-app
  updated: "2026-07-09"
---

# Credentials Card

This is a stop condition, not a workflow. Every other core/app skill defers to this one the moment a screen touches a secret.

## 1. What triggers this

Any of: a password field, an OTP/2FA/verification-code prompt, a payment or purchase confirmation (card entry, "Buy now", a subscription paywall), a passcode/biometric device-unlock prompt, an "add account" or "sign in" screen, or any screen asking to confirm identity (security questions, recovery email/phone).

## 2. What to do

- **Do not type, tap, or guess anything into the gated field.** Not a placeholder, not a value from `task.md`, not something inferred from context.
- **Stop the current step.** Don't chain further actions past the gate hoping it resolves itself.
- **Report it, don't hide it.** If this is an `autotap` run, finish with the task's JSON output: `success: false`, `error_reasoning` naming the specific gate (e.g. `"credential gate: app asked for OTP"`). If this is an ad-hoc session, say so plainly rather than silently stopping.
- **Only proceed if the user has explicitly pre-authorized this exact action** (e.g. a task that explicitly says "log in with the following test account: ..." with credentials supplied in the task itself, not inferred). Even then, the credential value itself is never written to `strategy.md`, `CARD.md`, or `memory/` — see §3.

## 3. What never gets written down

Passwords, OTPs, security codes, payment details (card numbers, CVVs, billing info), session tokens, and any personal account data go in **none** of: `strategy.md`, `CARD.md`, `memory/`, trace files, or a curator report. The *fact that a gate exists* on a given screen is fine to record (e.g. a CARD's Traps line: "checkout requires a saved card on file"); the *value* behind it is never fine to record.

If a task genuinely requires supplying credentials, the value should come from the environment (e.g. an `.env`-style secret the user controls outside of any file this harness reads back into a trace) — never typed into `task.md`, `strategy.md`, or committed anywhere.

## 4. Relationship to CARD.md

Every app's `CARD.md` carries a mandatory Traps line pointing back here (see `references/example-card.md`). That line should name *what* gates the app (login wall, OTP on first launch, paywall before search) without ever describing *how* to get past it beyond "stop and defer to `core/credentials/SKILL.md`."
