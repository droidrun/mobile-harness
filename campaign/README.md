# Overnight validation campaign — methodology

Driven via mobilerun's own **Task Runner** (natural-language tasks against mobilerun's real "Mobile Agent Fast", at `https://cloud.mobilerun.ai/task-runner`), not manual browser clicking and not a local `droidrun`/`mobilerun_core` terminal call — the sandbox's outbound network is allowlisted and cannot reach `api.mobilerun.ai` (confirmed with curl and plain Python `urllib`, both hit the proxy's `blocked-by-allowlist` 403 before any auth is even checked, so no package or API key changes that). Task Runner traffic goes through the browser's own network via Claude in Chrome, which is why it's the one thing that actually works from here.

## Logging structure (per-task, not just a one-line summary)

For every task submitted:

1. **Full trace capture** — `campaign/runs/<n>-<slug>.md`: the complete Task Stream text (Created → Execution Started → Executing Instruction → Task Analysis reasoning → Executing Actions/function calls → Result), captured verbatim via the page's own text, not a screenshot description. This is the actual evidence, not a paraphrase.
2. **Scoreboard row** — `campaign/log.md`: one line per attempt (task, app, result, notes, skill update), linking to the matching `runs/` file for detail.
3. **Skill fold-back** — any gap the trace reveals gets written into the relevant `core/mobile-ux-primitives/*.md` file or the app's `CARD.md` immediately, in the same commit-sized edits as the earlier live-device session, not batched up for later.
4. **Repeat-task deltas** — tasks that get re-run later (same or similar goal) get their result compared against the first attempt in the scoreboard, since that comparison — not the raw pass count — is the actual evidence for "getting better."

## Boundaries (unchanged, apply to every task, unattended)

Never: enter credentials/OTP/payment, send a message/email/DM, accept a ToS/consent screen, make a purchase, create an account, submit a form with real personal data, or use a login Shrey didn't perform himself. Any task that needs one of these gets logged as **blocked** and skipped.

## Session continuity note

Shrey has kept this chat session active and his computer awake specifically so this can keep running after he goes to sleep. Progress lives entirely in this `campaign/` folder plus `core/`/`apps/` edits — anyone (including Shrey in the morning) can reconstruct exactly what happened and why from these files without needing the live chat.
