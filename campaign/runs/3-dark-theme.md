# Run 3 — Dark theme toggle (FAILED — genuine gap, not a logging artifact)

- **Task ID:** 92a35c1e-4cea-419e-a871-4b65d743354a
- **Prompt:** "Turn dark theme on in Settings, confirm it's on, then turn it back off."
- **Queue item:** #2
- **Run via:** mobilerun Task Runner, `mobilerun/mobile-agent-fast`, Reasoning off, Vision off, VPN none, Apps none, Credentials none
- **Time:** 10 Jul 2026, 01:40 · **Duration:** 29s · **Status:** Failed

## Result (verbatim)
> Could not locate 'Display' (Affichage) settings menu after scrolling and searching.

## Execution timeline (62 events — condensed to the decision points, verbatim text where quoted)
1-5. Created / Start / FastAgentExecute / Screenshot / RecordUIState
6. FastAgentResponse — "I am currently in the Clock app. I need to navigate to the Settings app to toggle the dark theme..."
7-9. `system_button('home')` → Pressed HOME
12. FastAgentResponse — "I'm on the home screen. I see "Paramètres" (Settings) at index 17. I'll open it."
13-15. `click(17)` → Clicked 'Paramètres'
18. FastAgentResponse — "I'm in Settings, but I don't see "Display" (Affichage) immediately. I'll search for it using the sea[rch field]"
19-21. `type(10, 'Thème sombre')` → **"Text typed successfully (clear=False)"** (tool reports success, but see analysis)
24. FastAgentResponse — "The search results didn't populate as expected. I'll try pressing the "Enter" key..."
25-27. `system_button('enter')` → Pressed ENTER — still nothing
30. FastAgentResponse — "The search results are still not appearing. I'll try navigating to "Display" manually by going back [and scrolling]"
31-33. `system_button('back')` → Pressed BACK
36. FastAgentResponse — "I don't see "Display" (Affichage) in the current view. I'll swipe up to scroll down the settings lis[t]"
37-39. `swipe([500,2000]→[500,500])`
42. FastAgentResponse — "The swipe didn't reveal "Display" (Affichage). I'll try swiping again, but with a larger movement..."
43-45. `swipe([500,2300]→[500,100])`
48. FastAgentResponse — "It seems I'm having trouble finding "Display" (Affichage) in the main list. I'll try one more swipe..."
49-51. `swipe([500,2000]→[500,500])` — third swipe, same range as the first
54. FastAgentResponse — "I've scrolled through the settings menu, but "Display" (Affichage) is not visible. It's possible it'[s further down or named differently]"
55-56. `complete('false', ...)` → gave up
57-62. FastAgentEnd / FastAgentEnd / Finalize / Screenshot / RecordUIState / Result

## Read against the framework — this is the useful failure of the campaign so far
- **Root cause, high confidence:** the `type(10, 'Thème sombre')` call almost certainly hit the exact search-field focus race already documented in `core/mobile-ux-primitives/navigation-patterns.md` (first tap opens the keyboard but the field isn't focused yet, so typed text silently doesn't land) — this is the same Settings app, same search affordance, same symptom (zero results after typing) already seen twice before in this campaign (manual session, and reproduced during Play Store search).
- **What went wrong in the agent's own recovery, not the phone's UI:** the tool call reported "Text typed successfully" (a false positive at the tool layer — it confirms the type action executed, not that the field received it), so the agent had no signal to doubt its own typing. When results didn't populate, it tried Enter (reasonable), but when that also failed it abandoned search entirely rather than re-tapping the field and retyping — the actual fix that has worked twice before in this campaign.
- **Compounding issue:** it then searched by blind scrolling for "Affichage," using 3 swipes of similar/smaller magnitude in the same direction, plausibly not covering the full list or overshooting past the target without re-checking each screen carefully — a less efficient fallback than the search it gave up on.
- **Skill update made:** strengthened `core/mobile-ux-primitives/navigation-patterns.md`'s search-field note with an explicit corrective rule — if a search returns zero results immediately after typing, re-tap and retype once before trusting "no matches" or falling back to manual navigation. This directly targets the failure mode seen here.
- **Not yet fixed:** the underlying `type()` tool reporting success without confirming the target field actually received the text is a mobilerun_core/tool-layer issue, not something `core/` skill content can patch — flagging it here as a real product finding rather than trying to work around it in prose.
