# Run 2 — Files app top-level folders

- **Task ID:** 3f541889-cf25-4644-921f-e6fd72945867
- **Prompt:** "Open the Files app and list what top-level folders are shown."
- **Queue item:** #16
- **Run via:** mobilerun Task Runner, `mobilerun/mobile-agent-fast`, Reasoning off, Vision off, VPN none, Apps none, Credentials none
- **Time:** 10 Jul 2026, 01:04 · **Duration:** 12s · **Status:** Completed

## Result (verbatim)
> The top-level folders are: Alarms, Android, Audiobooks, DCIM, Documents, Download, Movies, Music, No[tifications...] (truncated in the dashboard's result preview; folder set matches the Android standard set seen in the earlier live-device session)

## Execution timeline (27 events, verbatim from Activity → task detail)
1. Created
2. Start
3. FastAgentExecute — "Open the Files app and list what top-level folders are shown."
4. Screenshot
5. RecordUIState
6. FastAgentResponse — "I need to open the Files app to list the top-level folders. I'll start by going to the home screen t[runcated]"
7. FastAgentToolCall — `system_button('home')`, `open_app('Files')`
8. System Button — Pressed HOME button
9. Open App — App started: `com.android.documentsui`
10. FastAgentOutput — system_button: Pressed HOME button | open_app: App started: com.android.documentsui
11. Screenshot
12. RecordUIState
13. FastAgentResponse — "The Files app is open, but it seems to be in a search view or empty state. I need to access the navi[gation drawer/back to get to the real listing]"
14. FastAgentToolCall — `click(25)`
15. Click — Clicked on Text: 'Retour' (Back) | Class: ImageButton | Coordinates: (56, 117)
16. FastAgentOutput — click: Clicked on Text: 'Retour' | Class: ImageButton...
17. Screenshot
18. RecordUIState
19. FastAgentResponse — "The Files app is now displaying the contents of the root directory. The top[-level folders visible are...]"
20. FastAgentToolCall — `complete('true', 'The top-level fol...')`
21. Complete — full folder list (see Result)
22. FastAgentEnd
23. FastAgentEnd
24. Finalize
25. Screenshot
26. RecordUIState
27. Result

## Read against the framework
- **Self-heal observed:** launching `com.android.documentsui` landed the agent in what it read as "a search view or empty state" rather than the root folder grid — not the expected first screen. Rather than getting stuck, it tapped the back ("Retour") control and arrived at the actual root listing on the next turn. This is exactly the kind of one-step recovery the framework is meant to produce, and it happened without any CARD/core content telling it to do this specifically.
- **Discrepancy worth flagging, not yet resolved:** the earlier manual live-device session (`memory/android-live-validation-session.md`, task queue #16 run by hand) recorded the Files app opening straight to a **hamburger-drawer** flow (Récents/Images/Vidéos/.../device root). This Task Runner run instead hit a search/empty-looking state and recovered via **back**, landing on the same eventual root listing. Two different entry paths reaching the same destination — could be non-determinism in `com.android.documentsui`'s cold-start state, or a genuine "sometimes it opens to last-used view" behavior. Not promoted to CARD/core yet since it's a single occurrence; flagged here for the repeat-round comparison (queue #16 vs a rerun) rather than guessed at.
- Folder set (Alarms, Android, Audiobooks, DCIM, Documents, Download, Movies, Music, No...) matches the standard Android layout already seen in the manual session — consistent, no correction needed there.
