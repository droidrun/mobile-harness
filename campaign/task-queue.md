# Task queue

Pull tasks top to bottom; append new ones at the end if the queue runs dry before the session does. `[install]` tasks need Play Store (available once Shrey signs in himself). Everything else works on the device as-is.

## Settings (no install needed)

1. Find and open the battery percentage toggle.
2. Turn dark theme on, then off again.
3. Find which Android version the device is running.
4. Check whether Wi-Fi or mobile data is currently active.
5. Find the display brightness control and note whether it's a slider or a stepped control.
6. Locate the app permissions screen for the Camera app.
7. Find how much storage is free.
8. Locate the "Recent notifications" or notification history screen.
9. Check the current date/time and time zone setting.
10. Find the option to change the keyboard/input language.
11. Locate "About phone" and note the model name.
12. Find the screen timeout setting and note its current value (don't change it).
13. Search settings for "accessibility" and open the first result.
14. Find Bluetooth settings and note whether it's on or off.
15. Locate the app that's using the most battery, if such a screen exists.

## Files / Fichiers (no install needed)

16. Open the Files app and list the top-level folders shown.
17. Find whether there's a "Downloads" folder and what's in it (if anything).
18. Check if there's a search function in Files and use it to search for "img".
19. Sort the file list by name vs. by date if a sort control exists, and note the difference.
20. Find whether Files has a grid view / list view toggle and switch it.

## Calendar (no install needed)

21. Open Calendar and note which view it defaults to (day/week/month/agenda).
22. Switch to month view if not already there.
23. Find today's date highlighted on the calendar.
24. Check if there's a way to add a new event (open the compose flow, do not save/create anything).
25. Switch back to the default view.

## Clock (no install needed)

26. Open Clock and note which tab it opens to (alarm/clock/timer/stopwatch).
27. Switch to the World Clock / additional-cities tab if present.
28. Open the Timer tab and note the default duration options shown (don't start one).
29. Open the Stopwatch tab and note the Start button's position.
30. Check whether there are any alarms currently set (don't add or remove any).

## Contacts (no install needed)

31. Open Contacts and note whether the list is empty or has entries.
32. Check for a search bar and try searching a common letter (e.g. "a").
33. Find whether there's a way to add a new contact (open the flow, don't save).
34. Check for a favorites/starred section.
35. Note whether contacts are grouped alphabetically with section headers.

## Gallery / Music / Voice recorder / Camera (no install needed)

36. Open Gallery and note whether there are any photos, and how they're organized (grid/albums).
37. Open Camera and note which mode it opens to (photo/video) and where the shutter button is.
38. Switch Camera to video mode if a mode switcher exists, then back to photo.
39. Open Music and note the default screen (library/for-you/search).
40. Open Voice Recorder (Magnétophone) and note the record button's position and any visible past recordings.

## Messaging / SMS (no install needed, no sending)

41. Open Messaging and confirm the inbox state (empty or has threads).
42. Open the compose (FAB) screen and check the "Frequent" vs "All contacts" tabs.
43. Type a contact name into the compose search field and observe filtering (don't send anything).
44. Back out of compose without sending.
45. Check the overflow menu options available from the inbox screen.

## Chrome (no install needed)

46. Open Chrome and note the default new-tab layout (shortcuts/frequently visited).
47. Open the tab switcher and note how many tabs are open.
48. Search for "wikipedia mobile ux" in the omnibox and open the top result.
49. Use Chrome's menu (⋮) to find the "Find in page" feature and search for a word on the loaded page.
50. Go back to the new-tab page using the back gesture/button.

## [install] Reddit — compare against existing CARD.md

51. Install Reddit via Play Store.
52. Open Reddit and capture any onboarding/tutorial screens shown (per core/learn-from-tutorial) before reaching the feed.
53. Confirm or correct the existing CARD claim: feeds auto-load near the bottom with no pagination control.
54. Confirm or correct: tapping an active vote arrow returns it to neutral rather than flipping directly.
55. Find a subreddit via search without logging in.
56. Open a post's comment thread and check the nesting/indentation convention.
57. Find the "N more replies" collapsed-thread affordance if one appears.
58. Check whether browsing without an account hits a login wall, and where.
59. Locate the app's own search icon vs. any top-nav menu icon and compare to core/mobile-ux-primitives' hamburger-vs-search prediction.
60. Update Reddit's CARD.md with anything the above turned up that wasn't already there.

## [install] Instagram — compare against existing CARD.md

61. Install Instagram via Play Store.
62. Capture any onboarding/tutorial screens before the first real screen.
63. Check whether basic browsing (not the whole app) requires login, and log exactly where the wall appears.
64. If browsing is possible, confirm or correct: home feed auto-loads more posts near the bottom.
65. Confirm or correct: double-tap on a post is equivalent to the heart icon from an unliked state.
66. Check whether Stories appear as a horizontally-scrollable row above the feed.
67. Update Instagram's CARD.md with anything new.

## [install] eBay — compare against existing CARD.md (has a real graduated precedent)

68. Install eBay via Play Store.
69. Search for "mac mini" without logging in.
70. Confirm or correct: results use infinite scroll with no next-page button.
71. Open the Sort control and confirm or correct the "active sort option omitted from the list" behavior.
72. Confirm resource-id-style stable labels are still a better bet than coordinates (note qualitatively, we can't read raw resource ids through the Chrome view — note what's visually stable instead).
73. Update eBay's CARD.md with anything new (from the visual/behavioral level, flagged as a lower-confidence source than a real accessibility-tree read).

## [install] Wikipedia — likely no login needed at all, good general-nav test

74. Install Wikipedia.
75. Search for "mobile user interface" and open the article.
76. Find the article's table of contents / jump-to-section control.
77. Use the app's own text search-within-article feature if present.
78. Switch the app's language if a language picker exists (check, don't necessarily change).
79. Check whether there's a "read later"/save feature and try it once.

## [install] Google Maps — permission dialogs, search patterns

80. Install Maps.
81. Handle the location-permission dialog per core/mobile-ux-primitives' Permission Dialogs pattern — note exactly which options are offered.
82. Search for a public landmark (e.g. "Eiffel Tower") and open its info card.
83. Check for a bottom-sheet-style info panel and note its drag-to-expand behavior (matches Flow Notes prediction for bottom sheets?).
84. Switch between map/satellite view if the option exists.
85. Try the "directions" flow up to (but not including) starting real navigation.

## [install] Duolingo — strong onboarding tutorial, best test of learn-from-tutorial

86. Install Duolingo.
87. Go through the onboarding flow, capturing every coach-mark/tutorial screen per core/learn-from-tutorial's format.
88. Note whether it requires account creation to proceed past onboarding — if so, stop there (credentials/account-creation gate) and log exactly where.
89. If a guest/skip-signup path exists, take it and note the first real lesson screen's UI conventions.
90. Tag any generalizable interaction pattern found in onboarding (e.g. progress-bar conventions) for later cross-app comparison.

## [install] Spotify — media-player specific patterns (not yet in core/mobile-ux-primitives)

91. Install Spotify.
92. Check whether browsing/search works without login; log where the wall is if not.
93. If accessible, open a public playlist and note the play/pause/skip control layout.
94. Check for a mini-player bar above the bottom nav and how tapping it expands to a full player.
95. Note whether swiping the mini-player left/right does anything (skip track?) — a new gestures.md candidate if so.

## [install] X (Twitter) — feed/threading comparison to Reddit

96. Install X.
97. Check whether the home feed is viewable without login.
98. If accessible, compare its infinite-scroll behavior to Reddit's and Instagram's.
99. Check the reply/thread nesting convention vs. Reddit's comment nesting.
100. Note the compose FAB position and whether it matches the general FAB prediction.

## Repeat round (do these AFTER at least 20 other tasks, to measure improvement — see README)

101. Repeat task 4 (battery toggle) — should now be faster with Settings CARD notes, if one was started.
102. Repeat a Reddit feed-scroll check (like #53) on a different subreddit — should need zero corrections if the CARD held.
103. Repeat an Instagram feed check (like #64) — same idea.
104. Repeat an eBay search with a different query (e.g. "iphone") — should reuse the Sort-sheet gotcha without rediscovering it.
105. Repeat the Settings search-field test (already known gotcha from the earlier live session) — confirm the re-tap workaround still holds, or find a cleaner fix.

## Overflow — add more here if the queue runs out before the session does

(Extend by pairing remaining pre-installed system apps with not-yet-tried interactions, or picking additional Play Store apps in the same spirit: no login where avoidable, no purchases/messages/forms ever.)
