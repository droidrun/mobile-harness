
---
name: scraping-newest-items
description: >
  Search the eBay app for a query, sort by newest first ("Newly Listed"), and
  scrape the top N listings' name and price into JSON, via mobilerun_core. Use
  to collect the latest listings/insertions for a search term on Android.
  Graduated from autotap on a cloud device (worked example: 50 newest "mac mini"
  listings).
---

# eBay: search → sort newest → scrape listings — Mobile Skill

## Purpose
Collect the **N newest** eBay listings for a search query (name + price) by driving the eBay
Android app and reading its accessibility tree. No login required.

## When to Use
You need the latest listings/insertions for a term (price + title) from eBay on a device — e.g.
"the 50 newest 'mac mini' listings, newest first".

## Control surface
`mobilerun_core` `device`: `start_app`, `ui()` / `find_nodes`, `tap_text`, `tap_node`, `tap(x,y)`,
`type`, `key`, `swipe`. Prefer resource-ids over coordinates (ports across screen sizes).

## Workflow

1. `start_app("com.ebay.mobile")` — opens to Home; browsing/searching needs **no login**.
2. Tap the search bar (top of Home), `type("<query>")`, `key("enter")`.
3. **Sort — poll the option SET; handle "already selected".** Tap "Sort" (bar coord ≈(595,420) on a
   1440-wide screen). The sheet is **intermittently absent from the a11y tree right after opening**
   (even when visually open), so POLL: re-fetch `ui()` (up to ~10×/0.6s) until ANY sort option text
   appears. Then:
   - "Newly Listed" is in the list → tap it (≈(720,2818) here) and wait ~3s; **or**
   - "Newly Listed" is ABSENT while other options show → it's already the active sort (eBay omits the
     active sort from the list under a "currently selected" header). Nothing to do.
   **Verify:** reopen Sort, poll again — "Newly Listed" must be ABSENT (= it's the active sort). Close
   the sheet. NEVER scrape an unverified sort: an unsorted (Best Match) list looks fine but is wrong data.
4. Scrape + scroll until N unique listings collected (see code below).

## Scraping the results (core)
Search cards expose stable resource-ids: title `…:id/textview_header_0`, price
`…:id/textview_primary_0` (shipping is `textview_primary_1` — ignore). Walk `ui().nodes` in order,
pairing each header with the next price; dedupe by title preserving order:

```python
def extract(tree):
    pairs, cur = [], None
    for n in tree.nodes:
        rid = (n.get("resourceId") or n.get("resource_id") or n.get("accessibilityIdentifier") or "")
        txt = n.get("text") or n.get("contentDescription") or n.get("content_description")
        if rid.endswith("textview_header_0") and txt:
            cur = txt
        elif rid.endswith("textview_primary_0") and txt and cur:
            pairs.append((cur, txt)); cur = None
    return pairs

seen, order, prev, stale, N = {}, [], -1, 0, 50
for _ in range(60):
    for t, p in extract(device.ui()):
        if t not in seen: seen[t] = p; order.append(t)
    if len(order) >= N: break
    stale = stale + 1 if len(order) == prev else 0
    prev = len(order)
    if stale >= 4: break          # end of results
    device.swipe(720, 2600, 720, 1000, 520); time.sleep(2.0)  # scroll within content
listings = [{"name": t, "price": seen[t]} for t in order[:N]]
```
(Swipe coordinates above suit a 1440x3088 screen — keep the swipe inside the content body, below the
filter/sort bar and above the bottom nav.)

## App-Specific Gotchas
- Prices are in the storefront's currency — on the tested device that's **USD (eBay.com)**.
- The "Shop by Release Year" carousel uses `textview_item_title` (different id), so the
  header/price extraction skips it automatically.
- **Bottom sheets (Sort/Filter) are flaky in the a11y tree** — even when visually open, their option
  nodes can be missing for a beat after opening, and `tap_text` on an option misses silently. POLL the
  option SET until it renders; tap by node or coordinate (Newly Listed ≈ (720,2818) on 1440x3088).
  A poll finding *nothing* is **ambiguous** — the option may be absent because it's already the active
  sort — so always VERIFY by reopening and reading the option set.
- The app may **resume on a previous screen** (not Home). Reach results via the search landing or a
  "Recent" entry, and confirm the Sort/Filter bar + result cards are present before sorting/scraping.
- Some cards show was/now prices; `textview_primary_0` is the displayed price (what we capture).
- Rely on resource-ids + the a11y tree, not hardcoded coordinates (screen sizes differ across devices).

## Failure Recovery
- Results not sorted → re-open Sort and re-select "Newly Listed"; verify the first cards changed.
- Stalls before N → likely end of results; report the count actually collected in `error_reasoning`.

## Expected Output
```json
{ "success": true, "query": "<q>", "sort": "newly listed", "count": 50,
  "listings": [ { "name": "<title>", "price": "<price>" } ], "error_reasoning": null }
```