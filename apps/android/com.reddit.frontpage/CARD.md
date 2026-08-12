# Reddit Card

Package: `com.reddit.frontpage`

Use this card only when Reddit is the foreground package or the task explicitly targets Reddit.

## Useful Labels

- Up/down arrows next to a post or comment are vote controls; the count between them is net score, not a rating.
- A top-left menu icon often opens community/navigation options; a magnifying glass opens search.

## Flow Notes

- Subreddit and post feeds auto-load additional content near the bottom of the scroll; there is no numbered pagination control. <!-- generalizable: infinite-scroll-no-pagination -->
- Tapping an active vote arrow again returns it to neutral rather than flipping straight to the opposite vote — expect two taps to reverse a vote.
- Comment threads nest by indentation; a "N more replies" control often replaces a fully expanded thread.

## Traps

- Vote counts can lag briefly after tapping; re-observe rather than assuming the tap failed if the score doesn't change instantly.
- If Reddit asks to log in or verify an account, stop and read `core/credentials`.
