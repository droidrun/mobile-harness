# Navigation Patterns

## Bottom navigation bar
3-5 icons pinned to the bottom of the screen, one always highlighted (current section). Tapping a different icon switches the whole screen's content, not a modal — treat it like changing tabs, not opening something new. The center slot is sometimes a raised/circular "create" action (camera apps, social apps) rather than a section — don't assume all bottom-bar icons are peers.

## Hamburger / navigation drawer
Three horizontal lines, almost always top-left. Opens a side panel (slides in from the edge) with app sections, account info, settings. Closing it: tap the icon again, tap outside the panel, or swipe it back toward the edge it came from.

## Tab bar (segmented, below a header)
A row of text or icon labels directly under a screen's title (e.g. "For You / Following", "Posts / About / Photos"). Unlike bottom nav, this scopes content *within* the current section, not the whole app. Usually swipeable left/right in addition to tappable.

## Overflow / contextual menu
Three dots (vertical "⋮" or horizontal "⋯"), usually top-right of a screen or attached to a specific list item/card. Opens a small menu of actions scoped to that specific item or screen — different from the hamburger drawer, which is global.

## Floating Action Button (FAB)
A circular button, usually bottom-right, often raised above the content with a shadow. Almost always the primary "create new" action for the current screen (new email, new post, new chat). It can be obscured by keyboard or scroll in some apps — if expected but not visible, try scrolling up first before concluding it's absent.

## Back behavior
- Android: system back gesture (edge swipe) or back button returns to the previous screen/state. Some apps intercept it to close an overlay or a sub-step within a flow instead of leaving the app entirely — expect one "extra" back press inside multi-step flows (forms, media viewers, filters).
- iOS: back is usually a top-left chevron + label, or an edge swipe from the left. There's rarely a persistent back gesture across the whole OS the way Android has one.
- A payment/checkout/security-sensitive screen sometimes disables the standard back gesture and forces use of an explicit "Cancel" or "X" — if back does nothing, look for an X icon (usually top-left or top-right) before assuming the screen is stuck.

## Breadcrumbs / stepper headers
Multi-step flows (checkout, sign-up, filters) often show a progress indicator (dots, a fraction like "2/4", or a horizontal bar) near the top. Use it to gauge how much is left rather than assuming a fixed number of steps app-to-app.

## Search entry points
Search is usually one of: a persistent search bar at the top of a feed, a magnifying-glass icon that expands into a text field, or a dedicated bottom-nav tab. Tapping a search icon that doesn't visibly expand may have moved focus to an already-present but unstyled input — check for a cursor/keyboard before re-tapping.

**Observed (2026-07-10, live device, Android Settings):** typing immediately after the first tap into a freshly-opened search field can silently no-op — the keyboard was visibly up but the field hadn't taken focus yet, so the typed text didn't land and the field stayed empty. A second tap directly on the field (or a short `wait` before typing) fixed it. Treat "keyboard visible" and "field is actually focused and accepting input" as two different things to confirm, not one — re-observe/re-check the field's contents after typing rather than assuming it landed.

**Failure mode confirmed live (2026-07-10, mobilerun Task Runner, Android Settings, task: "turn dark theme on"):** an agent hit exactly this gotcha and did not recover — it typed into the search field, got no results, pressed Enter (still nothing), then gave up on search entirely and switched to manually scrolling the full Settings list, never finding the target ("Affichage"/Display) after two scroll attempts, and reported failure. The recovery it needed was much cheaper than what it tried: re-tap the search field and retype, since the first type most likely never landed (same root cause as the note above), rather than assuming the search feature itself was broken or the term had no matches. **Rule of thumb: if a search field returns zero results immediately after typing, don't trust that result — re-tap the field, confirm a cursor/typed characters are actually visible in it, and retype once before concluding the search has no matches or falling back to manual navigation.**

## Home screen icon clusters / folders
A small stack of 2-4 overlapping app icons inside one home-screen slot is a folder, not a single app — tapping it expands into a labeled overlay grid of the apps inside (e.g. "System Tools"), rather than launching anything directly. Confirmed live (2026-07-10): tapping a "System..." icon cluster on a stock Android launcher expanded into a named folder with 9 apps. Tap an app inside the overlay to launch it, or tap outside the overlay to collapse it back.
