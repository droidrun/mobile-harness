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

## Toasts, snackbars, and banners
Small, temporary messages (often at the bottom, auto-dismissing after a few seconds) confirm an action already happened (“Copied to clipboard”, “Post shared”) — they are not asking for input and don't need to be dismissed manually before continuing, though they may temporarily overlap other bottom-screen elements like a FAB.
