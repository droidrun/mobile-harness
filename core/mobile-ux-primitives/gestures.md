# Gestures

## Tap vs. long-press
A single tap triggers the primary action. A long-press (hold ~500ms+) typically surfaces a secondary/contextual menu, a preview (peek), drag mode, or a selection mode (e.g. long-pressing a chat message to react/reply/delete, long-pressing a home-screen icon to move/uninstall it). If a tap does nothing and the element looks interactive, try long-press before concluding it's disabled.

## Double-tap
Overwhelmingly means "like/favorite" in media and social contexts (photo/video feeds). Outside of feeds, double-tap can also mean "zoom in" on an image/map. Rare elsewhere — don't reach for it as a general-purpose action.

## Swipe on a list row
Swiping a row left or right (email, messages, task lists) usually reveals one or more action buttons underneath (archive, delete, mark read, snooze) rather than navigating anywhere. The row itself typically still opens on a plain tap. Direction convention varies by app — right-swipe and left-swipe often map to different actions (e.g. right = archive, left = delete) rather than being redundant.

## Swipe to dismiss
Swiping a card, notification, or bottom sheet away (often in the direction it entered from, or straight down for bottom sheets) dismisses it without taking any other action. Distinguish this from a swipe-on-list-row: dismissal removes the element from view; the list-row swipe reveals actions but keeps the row.

## Pull-to-refresh
Dragging down from the very top of a scrollable feed (when already scrolled to the top) triggers a content refresh, usually with a spinner or animation before snapping back. Only works from the top of the scroll position — pulling down mid-list just scrolls.

## Pinch / spread to zoom
Two-finger pinch zooms out, spread zooms in — images, maps, PDFs. If a single accessibility-driven tap-based harness can't produce a pinch gesture natively, treat zoom controls (+/- buttons, double-tap-to-zoom) as the fallback path.

## Edge-swipe-back
Swiping from the very left edge of the screen toward the center is the Android/iOS system-level "go back" gesture, distinct from swiping a list row (which starts mid-screen, not at the edge). Starting position matters more than direction for disambiguating these.

## Drag and drop
Long-press-then-drag reorders list items, moves home-screen icons, or moves cards between columns (kanban-style UIs). Expect a visual lift/shadow effect on the dragged element as confirmation the gesture registered before continuing to drag.

## Scroll vs. swipe ambiguity
A vertical drag on a feed scrolls; a vertical drag on a horizontally-paged carousel (stories, image galleries within a post) may do nothing or bleed into the parent scroll. When an app has both nested horizontal and outer vertical scrolling regions, a failed gesture is often a hit-target problem, not a wrong-gesture problem — try anchoring the gesture more precisely inside the intended region.
