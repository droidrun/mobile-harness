# Instagram Card

Package: `com.instagram.android`

Use this card only when Instagram is the foreground package or the task explicitly targets Instagram.

## Useful Labels

- Home, Search, Reels, and Profile are often the bottom nav tabs.
- The heart icon under a post toggles like state; a filled/colored heart means already liked.
- The paper-plane icon opens the share sheet for a post.

## Flow Notes

- The home feed loads more posts automatically near the bottom of the scroll; there's no "load more" button — keep scrolling until new posts stop appearing. <!-- generalizable: infinite-scroll-no-pagination -->
- Double-tapping a post image likes it — equivalent to tapping the heart once from an unliked state.
- Stories, if present, are a horizontally scrollable row above the feed, distinct from the vertically scrolling feed below.

## Traps

- Double-tapping an already-liked post does not unlike it — only the heart icon reliably toggles both directions.
- If Instagram asks to log in, verify a code, or confirm a phone number, stop and read `core/credentials`.
