# Android eBay Card

Package: `com.ebay.mobile`

Use this card only when eBay is the foreground package or the task explicitly
targets eBay on Android.

## Useful Labels And Selectors

- Search entry points are usually exposed by visible search text near the top
  of the home or results screen.
- Search result title nodes have resource ids ending in
  `textview_header_0`.
- Displayed result price nodes have resource ids ending in
  `textview_primary_0`; shipping and secondary price text can use different
  ids.
- Sort and filter controls are usually visible above search results.

## Flow Notes

- Browsing and search can work without login, but purchases, saved searches,
  messages, and account actions are credential-gated.
- Prefer `find_nodes`, `tap_node`, and resource ids over fixed coordinates.
- Verify the result sort before collecting data; visually plausible results can
  still be sorted by a default ranking.
- Results use infinite scroll. Keep scrolling until the collected count stops
  growing; there is no next-page control. <!-- generalizable: infinite-scroll-no-pagination -->

## Traps

- Sort and filter bottom sheets can be delayed in the accessibility tree after
  opening. Re-observe before deciding an option is absent.
- The active sort option is often omitted from the sort sheet, which lists only
  the other choices. Absence can mean "already selected", not "not available".
- eBay can resume on a previous screen. Confirm the current page before
  searching, sorting, or scraping.
- Search result cards can repeat similar titles. Verify the intended listing
  opened after tapping.
- Currency and marketplace depend on the device/account storefront.
- If eBay asks to sign in, add a payment method, or verify identity, stop and
  read `core/credentials/GUIDE.md`.
