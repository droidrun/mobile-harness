# System Surfaces

## Permission dialogs
A system-styled (not app-styled) modal asking to allow camera, location, notifications, contacts, etc. Usually two or three options ("While using the app" / "Only this time" / "Don't allow" on Android; "Allow Once" / "Allow While Using App" / "Don't Allow" on iOS). These interrupt the app's own flow and must be resolved before the underlying screen becomes interactive again — check for one before assuming a tap "did nothing."

## Notification shade / control center
Swiping down from the very top of the screen (outside any app's own pull-to-refresh, i.e. from above the app content into the status bar area) reveals system notifications and quick settings, not app content. This is an OS-level surface, not something an app renders — if it appears unexpectedly, the previous gesture likely started too close to the top edge.

## Keyboard behavior
Tapping a text field raises the on-screen keyboard, which covers roughly the bottom third to half of the screen. Elements that were visible before (e.g. a submit button) may now be hidden behind the keyboard rather than gone — scroll the field into view or dismiss the keyboard (tap outside the field, or a dedicated down-chevron/"Done" key) before deciding an element disappeared. Keyboards often have a contextual action key (Search, Go, Next, Done) that submits the current field or advances to the next one, which can substitute for finding an explicit on-screen button.

## App switcher / recents
A system-level gesture (swipe up and hold, or a dedicated button) shows recently used apps as cards, independent of any in-app navigation. Useful context if a task ever requires returning to a previous app rather than navigating back within the current one.

## Deep links and intents
Some actions (tapping a shared link, an OAuth "Continue with Google" button, a "Open in App" banner) hand off to another app or a system browser view and then return. Expect a brief app-switch during these — it is not an error state, and the return trip usually lands back in the originating app automatically once the handoff completes.

## Compatibility / informational dialogs
Some system or older pre-installed apps show a one-time system-styled dialog on launch warning the app targets an old Android version and "may not work correctly" or lacks recent security/privacy protections, with an "OK" (dismiss) and a "check for update" option. Confirmed live (2026-07-10, stock SMS/MMS app). Treat like a permission dialog: resolve it (dismiss with OK unless the task specifically wants an update check) before the underlying screen becomes interactive — it's informational, not a task blocker, and dismissing it doesn't affect the app's actual functionality for a given run.

## Toasts, snackbars, and banners
Small, temporary messages (often at the bottom, auto-dismissing after a few seconds) confirm an action already happened (“Copied to clipboard”, “Post shared”) — they are not asking for input and don't need to be dismissed manually before continuing, though they may temporarily overlap other bottom-screen elements like a FAB.

## "Default" screen claims can actually be persisted last-used state
Many multi-tab apps (Clock's alarm/clock/timer/stopwatch tabs, Calendar's day/week/month views, and similar) remember which tab or view was open last and reopen to *that*, rather than a fixed factory-default tab — so re-launching the same app later in a session can land on a completely different tab than a genuinely fresh install would, with no dialog or signal that this happened. **Confirmed live (2026-07-10, mobilerun Task Runner):** a task asking "which tab does the Clock app open to by default" got the answer "Timer (Minuteur)" with high confidence — but a separate, earlier task in the same session had explicitly navigated to and used the Minuteur tab, so this run's "default" was almost certainly that earlier session's leftover state, not the app's actual first-launch default. There was no way to tell the difference from a single observation. **Rule of thumb: treat "what does this app open to by default" as unverifiable from a single launch if the app (or another task) has been opened before in the same device session — the honest answer is "opened to X on this launch," not "defaults to X," unless the app was launched from a genuinely fresh/force-stopped state (or this is the very first time it's been opened this session).**
