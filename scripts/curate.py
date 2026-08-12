#!/usr/bin/env python3
"""
curate.py — Skill Curator: cross-app pattern promotion for mobile-harness.

Ported from autotap's curate.py and extended for this repo's actual layout.
Separate, periodic, human-reviewed process — not part of any per-task loop,
not invoked automatically by an agent mid-task. It looks ACROSS every app's
CARD.md *and* every memory/ file for `<!-- generalizable: <tag> -->`
annotations (left behind per `core/learn-from-tutorial/GUIDE.md`) and
proposes promoting patterns that show up independently in enough apps into
`core/mobile-ux-primitives/` — the cross-app layer every run reads.

Two sources are scanned, because this repo splits findings across both:
  - apps/<platform>/<app-id>/CARD.md   (committed, app-specific, stable facts)
  - memory/**/*.md                     (local, gitignored, where
    core/learn-from-tutorial/GUIDE.md tells agents to write fresh findings
    before they're confirmed enough for a CARD)
Memory files named `memory/apps/<app-id>.md` are attributed to that app id
for the >= --min-apps count. Other memory files (freeform notes that predate
or don't follow that convention) are still scanned and reported, but don't
count toward the app-count threshold — a single freeform file isn't cross-app
evidence on its own, even if it happens to touch several apps in prose.

By default this only ever emits a report — nothing under core/ or apps/ is
touched. Pass --apply to also draft the promotion directly into the
suggested core/mobile-ux-primitives/<file>.md, under a clearly marked
"Curator-suggested additions (unreviewed)" section, so a human only needs to
review/edit/remove rather than hand-copy from the report. --apply still never
touches apps/ or memory/ and never removes the source tags — it only writes its
own marked block, replacing that block on re-runs rather than stacking copies,
and removing blocks whose evidence no longer promotes.

Closing the loop: when a human folds a draft block into prose they add
`<!-- promoted: <tag> -->` beside it. Source tags stay in the cards and memory
files, so the evidence trail survives and new apps confirming the pattern still
register — but the tag is never proposed again. Without that marker the same
evidence promotes on every run forever, re-suggesting a pattern already written
into the very file the block is appended to.

Usage:
  python curate.py --harness /path/to/mobile-harness [--min-apps 3] [--out DIR] [--apply]

Output:
  <out>/curator-report-<UTC timestamp>.md — candidate promotions + a staleness pass.
  With --apply: also writes drafts into core/mobile-ux-primitives/<file>.md.
"""
import argparse
import difflib
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

GENERALIZABLE_RE = re.compile(r"<!--\s*generalizable:\s*([\w-]+)\s*-->")
# Written by a human into core/mobile-ux-primitives/<file>.md when they fold a
# curator block into prose. Source tags stay put, so the evidence trail survives
# and new apps confirming the pattern still register; the tag just stops being
# re-proposed as though it were a fresh candidate on every run.
PROMOTED_RE = re.compile(r"<!--\s*promoted:\s*([\w-]+)\s*-->")
SECTION_RE = re.compile(r"^##\s+(Useful Labels|Flow Notes|Traps)\s*$", re.MULTILINE)
BULLET_START_RE = re.compile(r"^(\s*)-\s+(.*)$")
ONLY_MARKER_RE = re.compile(r"^\s*<!--\s*generalizable:\s*[\w-]+\s*-->\s*$")
FENCE_RE = re.compile(r"^\s*```")
HEADING_RE = re.compile(r"^#{1,6}\s")

# A whole curator-drafted block, so --apply can replace its own previous output
# instead of stacking another copy on top of it.
CANDIDATE_BLOCK_RE = re.compile(
    r"\n*<!-- BEGIN curator-candidate.*?<!-- END curator-candidate -->[ \t]*\n?",
    re.DOTALL,
)

# Crude keyword buckets → which core/mobile-ux-primitives reference file a promoted
# pattern probably belongs in. First-pass heuristic; a human confirms in review.
TARGET_HINTS = [
    ("gestures.md", ("swipe", "tap", "long-press", "long press", "pinch", "double-tap",
                      "double tap", "drag", "pull-to-refresh", "pull to refresh")),
    ("navigation-patterns.md", ("nav", "hamburger", "drawer", "tab bar", "back button",
                                 "back gesture", "fab", "floating action", "breadcrumb",
                                 "overflow menu", "search bar", "search icon")),
    ("content-and-feeds.md", ("feed", "scroll", "upvote", "downvote", "like", "heart",
                                "share sheet", "comment", "follow", "subscribe", "card")),
    ("system-surfaces.md", ("permission", "notification", "keyboard", "app switcher",
                              "deep link", "intent", "toast", "snackbar")),
    ("onboarding-and-forms.md", ("carousel", "coach mark", "coach-mark", "onboarding",
                                    "progress indicator", "validation", "autofill", "oauth",
                                    "sso", "required field")),
]


def excerpt(bullet, limit=180):
    """One-line, length-capped view of a bullet, for sections that exist to show
    *that* evidence exists rather than to be promoted from. Memory bullets run to
    several hundred words each; printing them whole buries the report."""
    text = " ".join(GENERALIZABLE_RE.sub("", bullet).split())
    return text if len(text) <= limit else text[:limit].rstrip() + " […]"


def guess_target_file(bullets):
    text = " ".join(bullets).lower()
    scores = {fname: sum(text.count(kw) for kw in kws) for fname, kws in TARGET_HINTS}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "(unclear — needs manual read)"


def find_cards(harness: Path):
    """Yield (source, app_id, path, text) for every apps/<platform>/<app-id>/CARD.md."""
    apps_dir = harness / "apps"
    if not apps_dir.is_dir():
        return
    for platform_dir in sorted(p for p in apps_dir.iterdir() if p.is_dir()):
        for app_dir in sorted(p for p in platform_dir.iterdir() if p.is_dir()):
            card_path = app_dir / "CARD.md"
            if card_path.exists():
                yield f"card:{platform_dir.name}", app_dir.name, card_path, card_path.read_text()


def find_memory(harness: Path):
    """Yield (source, app_id_or_None, path, text) for every memory/**/*.md file.

    memory/apps/<app-id>.md -> attributed to <app-id>. Anything else under
    memory/ is scanned but yielded with app_id=None (freeform, not counted
    toward the cross-app threshold).
    """
    memory_dir = harness / "memory"
    if not memory_dir.is_dir():
        return
    apps_subdir = memory_dir / "apps"
    for path in sorted(memory_dir.rglob("*.md")):
        if apps_subdir in path.parents and path.parent == apps_subdir:
            yield "memory:apps", path.stem, path, path.read_text()
        else:
            yield "memory:freeform", None, path, path.read_text()


def iter_bullets(text):
    """Yield each `- ` bullet with its continuation lines folded in.

    Matching only the first line of a bullet loses the `generalizable` marker in
    the two places it most often lands: on the wrapped remainder of a long bullet,
    and on its own line under the finding (the shape `core/learn-from-tutorial/
    GUIDE.md` used to show). Both dropped silently — a tagged pattern would just
    quietly fail to reach the app threshold — so fold continuations in first.

    A bullet stays open across blank lines *only* for a lone marker or a code
    fence; any other unindented content closes it, so an unrelated paragraph
    further down the section can't glom onto the bullet above it.
    """
    bullets = []
    current, indent, blank_seen = None, 0, False
    for line in text.splitlines():
        m = BULLET_START_RE.match(line)
        if m:
            if current is not None:
                bullets.append(current)
            indent, current, blank_seen = len(m.group(1)), m.group(2).strip(), False
            continue
        if current is None:
            continue
        stripped = line.strip()
        if not stripped:
            blank_seen = True
            continue
        if ONLY_MARKER_RE.match(line):
            current = f"{current} {stripped}"
            continue
        if FENCE_RE.match(line):
            continue  # a fenced standalone marker — skip the fence, keep the bullet open
        if not blank_seen and not HEADING_RE.match(line) and len(line) - len(line.lstrip()) > indent:
            current = f"{current} {stripped}"
            continue
        bullets.append(current)
        current, blank_seen = None, False
    if current is not None:
        bullets.append(current)
    return bullets


def extract_bullets_by_section(text):
    """Split a CARD.md body into {section_name: [bullet_text, ...]}."""
    sections = {}
    headers = list(SECTION_RE.finditer(text))
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        sections[m.group(1)] = iter_bullets(text[start:end])
    return sections


def extract_flat_bullets(text):
    """Memory files aren't sectioned like CARD.md — just dated bullets. Section name
    is reported as 'memory' for provenance in the output."""
    return {"memory": iter_bullets(text)}


def normalize(s):
    s = GENERALIZABLE_RE.sub("", s)
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def collect_tagged(records):
    """tag -> [(source, app_id, section, bullet_text), ...] across cards + memory.

    app_id may be None for freeform memory files — those entries are still
    shown in the report (provenance matters) but excluded from the distinct-
    app count used for promotion thresholds.
    """
    tagged = defaultdict(list)
    for source, app_id, _path, text in records:
        by_section = (extract_bullets_by_section(text) if source.startswith("card:")
                      else extract_flat_bullets(text))
        for section, bullets in by_section.items():
            for b in bullets:
                m = GENERALIZABLE_RE.search(b)
                if m:
                    tagged[m.group(1)].append((source, app_id, section, b))
    return tagged


def collect_promoted(harness: Path):
    """tag -> the primitive file that claims it, for every `promoted` marker.

    Promotion is the one step the curator can't do for itself: a human reads the
    draft block, writes the prose, and marks the tag as landed. Without that
    record the same evidence promotes forever, so every run re-proposes a pattern
    already sitting in the file it would be added to.
    """
    promoted = {}
    ux_dir = harness / "core" / "mobile-ux-primitives"
    if not ux_dir.is_dir():
        return promoted
    for path in sorted(ux_dir.glob("*.md")):
        for m in PROMOTED_RE.finditer(path.read_text()):
            promoted.setdefault(m.group(1), path)
    return promoted


def collect_untagged_clusters(records, similarity_threshold=0.72):
    """Best-effort fallback: near-duplicate bullets across apps that were never tagged.
    Conservative — only flags a candidate cluster, never auto-promotes it.
    Only considers entries with a known app_id (card or memory/apps/<id>.md);
    freeform memory notes are too unstructured to cluster reliably by app.
    """
    all_bullets = []  # (source, app_id, section, raw_text, normalized_text)
    for source, app_id, _path, text in records:
        if app_id is None:
            continue
        by_section = (extract_bullets_by_section(text) if source.startswith("card:")
                      else extract_flat_bullets(text))
        for section, bullets in by_section.items():
            for b in bullets:
                if GENERALIZABLE_RE.search(b):
                    continue  # already handled via explicit tag
                if "core/" in b:
                    continue  # already points at an existing core file (e.g. the mandatory
                              # credential STOP line) — boilerplate, not a promotion candidate
                norm = normalize(b)
                if norm:
                    all_bullets.append((source, app_id, section, b, norm))

    clusters = []
    used = set()
    for i, (s1, a1, sec1, raw1, n1) in enumerate(all_bullets):
        if i in used:
            continue
        group = [(s1, a1, sec1, raw1)]
        for j, (s2, a2, sec2, raw2, n2) in enumerate(all_bullets):
            if j <= i or j in used or a2 == a1:
                continue
            if difflib.SequenceMatcher(None, n1, n2).ratio() >= similarity_threshold:
                group.append((s2, a2, sec2, raw2))
                used.add(j)
        if len({app for _, app, _, _ in group}) > 1:
            used.add(i)
            clusters.append(group)
    return clusters


def staleness_pass(records, harness: Path):
    """Crude proxy: file mtime. Real usage counts need trace-dir scanning per app, which
    isn't centralized yet — flagged here as a known gap, not silently assumed away.
    """
    now = datetime.now(timezone.utc).timestamp()
    rows = []
    for source, app_id, path, _text in records:
        age_days = (now - path.stat().st_mtime) / 86400
        state = "active" if age_days < 30 else ("stale" if age_days < 90 else "archived")
        label = app_id if app_id else str(path.relative_to(harness))
        rows.append((source, label, round(age_days, 1), state))
    return rows


def apply_drafts(harness: Path, promotions: dict):
    """Write a clearly-marked, unreviewed draft block per promoted tag into its
    suggested core/mobile-ux-primitives/<file>.md. Never touches apps/ or memory/,
    never removes source tags, never rewrites prose outside its own block.

    Idempotent: the curator is meant to run periodically and deliberately leaves
    source tags in place, so the same evidence promotes again on every run. If a
    previous draft block is already in the file, replace it rather than appending
    a second copy (and collapse any duplicates an earlier run left behind).

    The curator owns its blocks for their whole lifetime, not just while the
    evidence holds. Evidence goes away — a tag gets removed, a card is deleted,
    --min-apps is raised — and a block written by an earlier run would otherwise
    sit in a tracked guide forever, read as guidance by every agent, describing a
    pattern the curator no longer stands behind. So each run also sweeps
    core/mobile-ux-primitives/ and drops curator blocks it isn't re-emitting.
    Returns [(path, "appended"|"replaced"|"removed"), ...].
    """
    written = []
    by_target = defaultdict(list)
    for tag, entries in promotions.items():
        target = guess_target_file([b for *_r, b in entries])
        by_target[target].append((tag, entries))

    for target, tag_entries in by_target.items():
        if target == "(unclear — needs manual read)":
            continue
        target_path = harness / "core" / "mobile-ux-primitives" / target
        if not target_path.exists():
            continue
        block = ["", "<!-- BEGIN curator-candidate: review and fold into the prose above, or delete -->",
                 "## Curator-suggested additions (unreviewed)", ""]
        for tag, entries in sorted(tag_entries):
            apps = sorted({f"{s}/{a}" for s, a, _sec, _b in entries if a})
            block.append(f"- `{tag}` — seen in: {', '.join(apps)}")
            for source, app_id, section, bullet in entries:
                block.append(f"  - [{source}/{app_id or 'unscoped'} · {section}] "
                              f"{GENERALIZABLE_RE.sub('', bullet).strip()}")
        block.append("<!-- END curator-candidate -->")
        new_block = "\n".join(block[1:]) + "\n"  # block[0] is a spacer; add it explicitly below

        text = target_path.read_text()
        had_block = bool(CANDIDATE_BLOCK_RE.search(text))
        # Strip every prior draft block (an earlier, non-idempotent run may have
        # left several) and re-emit exactly one, rather than substituting in place
        # — bullet text is arbitrary and would be read as regex backreferences.
        text = CANDIDATE_BLOCK_RE.sub("", text).rstrip("\n") + "\n\n" + new_block
        action = "replaced" if had_block else "appended"
        target_path.write_text(text)
        written.append((str(target_path), action))

    # Sweep: a block whose evidence no longer promotes is stale guidance, so drop it.
    rewritten = {path for path, _action in written}
    ux_dir = harness / "core" / "mobile-ux-primitives"
    if ux_dir.is_dir():
        for path in sorted(ux_dir.glob("*.md")):
            if str(path) in rewritten:
                continue
            text = path.read_text()
            if not CANDIDATE_BLOCK_RE.search(text):
                continue
            path.write_text(CANDIDATE_BLOCK_RE.sub("", text).rstrip("\n") + "\n")
            written.append((str(path), "removed"))
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harness", required=True, help="path to a mobile-harness checkout")
    ap.add_argument("--min-apps", type=int, default=3,
                     help="min. distinct apps a pattern must appear in before it's a promotion candidate (default: 3)")
    ap.add_argument("--out", default=None, help="output directory for the report (default: <harness>/.curator/reports)")
    ap.add_argument("--apply", action="store_true",
                     help="also append promotion drafts directly into core/mobile-ux-primitives/<file>.md "
                          "(marked, unreviewed — still requires a human to fold in or discard)")
    args = ap.parse_args()

    harness = Path(args.harness).resolve()
    if not harness.is_dir():
        print(f"ERROR: {harness} is not a directory", file=sys.stderr)
        sys.exit(1)

    records = list(find_cards(harness)) + list(find_memory(harness))
    cards_only = [r for r in records if r[0].startswith("card:")]
    if not records:
        print(f"No apps/*/*/CARD.md or memory/**/*.md found under {harness} — nothing to curate yet.", file=sys.stderr)
        sys.exit(0)

    tagged = collect_tagged(records)
    promoted = collect_promoted(harness)
    # A tag a human has already folded into prose is not a candidate at any app
    # count, so it leaves the pool before the threshold is applied rather than
    # falling through to the below-threshold section.
    already_promoted = {tag: entries for tag, entries in tagged.items() if tag in promoted}
    open_tags = {tag: entries for tag, entries in tagged.items() if tag not in promoted}

    promotions = {tag: entries for tag, entries in open_tags.items()
                  if len({app for _s, app, _sec, _b in entries if app}) >= args.min_apps}
    # Tagged, but not yet in enough distinct apps — including tags seen only in
    # freeform memory. Reported separately so evidence is visible while it
    # accumulates, instead of vanishing until the moment it crosses the threshold.
    below_threshold = {tag: entries for tag, entries in open_tags.items() if tag not in promotions}

    clusters = [g for g in collect_untagged_clusters(records)
                if len({app for _s, app, _sec, _r in g}) >= args.min_apps]

    stale = staleness_pass(records, harness)

    out_dir = Path(args.out) if args.out else (harness / ".curator" / "reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = out_dir / f"curator-report-{ts}.md"

    lines = [
        f"# Curator Report — {ts}",
        "",
        f"Scanned {len(cards_only)} CARD.md file(s) under `{harness / 'apps'}` and "
        f"{len(records) - len(cards_only)} memory file(s) under `{harness / 'memory'}`. "
        f"Threshold: pattern seen in >= {args.min_apps} distinct apps. Freeform memory "
        f"notes with no attributable app id don't count toward that threshold; they still "
        f"appear as evidence under whichever tag they carry. Tags marked "
        f"`<!-- promoted: <tag> -->` in a primitive file are listed separately and never "
        f"re-proposed, however much evidence accumulates.",
        "",
        "**Nothing has been written to `core/` or `apps/` unless `--apply` was passed "
        "(and even then, only as a clearly marked, unreviewed draft appended to the "
        "suggested file — nothing is auto-merged into prose).**",
        "",
        "## Promotion candidates (explicitly tagged `generalizable`)",
        "",
    ]
    if not promotions:
        lines.append("_None yet — tag findings with `<!-- generalizable: <tag> -->` "
                      "(see `core/learn-from-tutorial/GUIDE.md`) as apps accumulate._")
    for tag, entries in sorted(promotions.items()):
        apps = sorted({f"{s}/{a}" for s, a, _sec, _b in entries if a})
        target = guess_target_file([b for *_r, b in entries])
        lines += [
            f"### `{tag}`",
            f"- Seen in: {', '.join(apps)}",
            f"- Suggested target: `core/mobile-ux-primitives/{target}`",
            "- Source bullets (pick/merge the clearest phrasing when promoting):",
        ]
        for source, app_id, section, bullet in entries:
            lines.append(f"  - [{source}/{app_id or 'unscoped'} · {section}] {GENERALIZABLE_RE.sub('', bullet).strip()}")
        lines.append("")

    lines += ["## Already promoted (marked in `core/mobile-ux-primitives/`, not re-proposed)", ""]
    if not promoted:
        lines.append("_None yet. Add `<!-- promoted: <tag> -->` beside the prose when you fold a "
                     "draft block in, so the tag stops being re-proposed._")
    for tag, path in sorted(promoted.items()):
        entries = already_promoted.get(tag, [])
        apps = sorted({f"{s}/{a}" for s, a, _sec, _b in entries if a})
        where = path.relative_to(harness)
        if not entries:
            lines.append(f"- `{tag}` — in `{where}`, but no source tag carries it any more. "
                         f"Either the evidence was removed, or the marker is a typo.")
        else:
            lines.append(f"- `{tag}` — in `{where}`; still tagged in {len(apps)} app(s)"
                         f"{': ' + ', '.join(apps) if apps else ''}")
    lines.append("")

    lines += [f"## Tagged evidence below the threshold (< {args.min_apps} distinct apps — not candidates yet)", ""]
    if not below_threshold:
        lines.append("_None — every tag found is already a candidate above._")
    for tag, entries in sorted(below_threshold.items()):
        apps = sorted({f"{s}/{a}" for s, a, _sec, _b in entries if a})
        n = len(apps)
        lines.append(f"- `{tag}` — {n} attributable app(s)"
                     f"{': ' + ', '.join(apps) if apps else ' (freeform memory only)'}")
        for source, app_id, section, bullet in entries:
            lines.append(f"  - [{source}/{app_id or 'unscoped'} · {section}] {excerpt(bullet)}")
    lines.append("")

    lines += ["## Untagged near-duplicates across apps (lower confidence — verify before tagging/promoting)", ""]
    if not clusters:
        lines.append("_None found this pass._")
    for group in clusters:
        apps = sorted({f"{s}/{a}" for s, a, _sec, _r in group})
        lines.append(f"- Apps: {', '.join(apps)}")
        for source, app_id, section, raw in group:
            lines.append(f"  - [{source}/{app_id} · {section}] {raw}")
    lines.append("")

    lines += ["## Freshness (mtime proxy — not real usage counts, see script docstring)", "",
              "| Source | App / file | Age (days) | State |", "|---|---|---|---|"]
    for source, label, age, state in sorted(stale, key=lambda r: -r[2]):
        lines.append(f"| {source} | {label} | {age} | {state} |")

    report_path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {report_path}")
    print(f"  {len(promotions)} tagged promotion candidate(s), "
          f"{len(below_threshold)} tagged below threshold, "
          f"{len(promoted)} already promoted, "
          f"{len(clusters)} untagged cluster(s), {len(records)} file(s) scanned "
          f"({len(cards_only)} cards).")

    if args.apply:
        # Runs even with nothing to promote: the sweep still has to clear blocks
        # left by earlier runs whose evidence has since gone away.
        actions = apply_drafts(harness, promotions)
        if not promotions:
            print("  --apply: nothing to draft (no promotion candidates met the threshold).")
        for path, action in actions:
            print(f"  --apply: {action} unreviewed draft in {path}")


if __name__ == "__main__":
    main()
