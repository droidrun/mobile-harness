# Run 6 — About phone model name

- **Task ID:** 8fbb20ee-db52-441f-9a58-311fcf3beae3
- **Prompt:** "Open Settings, go to About phone, and tell me the device model name."
- **Queue item:** #11
- **Run via:** mobilerun Task Runner, `mobilerun/mobile-agent-fast`
- **Time:** 10 Jul 2026, 01:49 · **Duration:** 10s (26 events) · **Status:** Completed

## Result (verbatim)
> The device model name is PJZ110.

## Summary
Clean, uneventful pass this time: `open_app('Settings')` from a system UI starting state → one scroll down → "À propos du téléphone" (About phone) visible with model name already in its summary line, no need to even tap in. Fastest task of the campaign so far (10s, 26 events, single scroll). No gaps, no skill update.
