# Run 4 — Wi-Fi vs mobile data status

- **Task ID:** df2628dd-bf5e-4468-95ec-af1face37e4e
- **Prompt:** "Check whether Wi-Fi or mobile data is currently active in Settings, and tell me which."
- **Queue item:** #4
- **Run via:** mobilerun Task Runner, `mobilerun/mobile-agent-fast`, Reasoning off, Vision off, VPN none, Apps none, Credentials none
- **Time:** 10 Jul 2026, 01:43 · **Duration:** 22s · **Status:** Completed

## Result (verbatim)
> Wi-Fi is currently active (connected to "mywifi").

## Execution timeline (38 events, condensed)
6. FastAgentResponse — "The current Settings screen doesn't show "Network & Internet" or "Connections" at the top level. I n[eed to scroll]"
7-9. `swipe([500,2000]→[500,500])` — scroll down, no luck
12. FastAgentResponse — "Still not seeing it. I'll swipe up again to reach the top of the settings menu, where network settin[gs usually live]"
13-15. `swipe([500,500]→[500,2000])` — scrolled back up (reversed direction, self-corrected instead of repeating the same failed swipe)
18. FastAgentResponse — "I still don't see "Network & Internet" in the list. I'll use the search bar to find it directly."
19-21. `type(10, 'Réseau')` → **"Text typed successfully"** — this time the search actually worked (results populated, unlike Run 3)
24. FastAgentResponse — "I'll tap on "Réseau et Internet" (index 31) to check the status of Wi-Fi and mobile data."
25-27. `click(31)` → Clicked 'Réseau et Internet'
30. FastAgentResponse — "The "Internet" setting (index 20) shows "mywifi" as the summary (index 21), which confirms that Wi-F[i is active]"
31-38. `complete('true', ...)` → FastAgentEnd ×2 → Finalize → Screenshot → RecordUIState → Result

## Read against the framework
- **Confirms, doesn't newly discover:** the search-field focus race is genuinely intermittent, not deterministic — the *identical* `type()` action into the *same* Settings search field that failed silently in Run 3 worked cleanly here. This matches the existing memory note ("the gotcha isn't universal, it's intermittent/context-dependent") rather than contradicting it. Good corroborating data point, no skill edit needed from this run alone.
- **Good self-correction, no skill gap:** when the first scroll-down didn't surface the target, the agent reversed direction (scrolled up) instead of repeating the same failed action — reasonable, undocumented-but-sensible behavior; not worth codifying as a rule yet since it's a single instance of ordinary judgment, not a gotcha.
- No new gap folded back. This run mainly reinforces existing framework content rather than extending it.
