#!/usr/bin/env python3
"""
test_curate.py — Fixture-based tests for scripts/curate.py.

Ported from autotap's tests/test_core_skills.py (the curate.py-specific
tests), adapted for this repo's actual curate.py: find_cards/collect_tagged
now return (source, app_id, path, text) / (source, app_id, section, bullet)
4-tuples (source is "card:<platform>" or "memory:apps"/"memory:freeform",
not a bare platform name), plus new coverage for the memory/ scan and the
--apply flag that autotap's curate.py never had.

No network, no mobilerun_core, no phone -- every fixture here is a fake
mobile-harness directory built under a tempdir.

Run:
  python3 tests/test_curate.py                    # standalone, no pytest needed
  python3 -m pytest tests/test_curate.py -v        # also works if pytest is installed
"""
import sys
import tempfile
import traceback
from pathlib import Path

# mobile-harness/tests/test_curate.py -> mobile-harness/scripts
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import curate as C  # noqa: E402


# ── fixture builder ─────────────────────────────────────────────────

CARD_TEMPLATE = """# {app_id} Card
Package: `{app_id}`
Use this card only when automating this app.

## Useful Labels
- Search icon is usually top-right.

## Flow Notes
{flow_note}

## Traps
- Never enter a password; see core/credentials.
"""


def make_harness(tmp: Path, n_tagged_cards=3, n_tagged_memory_apps=0, add_freeform_memory=False):
    """Build a fake mobile-harness tree under tmp. Returns the harness root.

    n_tagged_cards: how many apps/android/<id>/CARD.md get the
      `generalizable: pull-refresh` tag.
    n_tagged_memory_apps: how many memory/apps/<id>.md get the same tag
      (distinct app ids from the card ones, so a test can control whether
      the combined card+memory count crosses --min-apps on its own).
    add_freeform_memory: adds one memory/*.md file NOT under memory/apps/,
      tagged, to exercise the "reported but not counted" path.
    """
    harness = tmp / "harness"
    (harness / "apps" / "android").mkdir(parents=True)
    (harness / "memory" / "apps").mkdir(parents=True)
    (harness / "core" / "mobile-ux-primitives").mkdir(parents=True)
    (harness / "core" / "mobile-ux-primitives" / "content-and-feeds.md").write_text(
        "# Content & Feeds\n\n## Pull to refresh\n(placeholder)\n"
    )

    tagged_bullet = ("- Pulling down on a feed triggers a refresh spinner before new content "
                      "loads. <!-- generalizable: pull-refresh -->")
    plain_bullet = "- Pulling down on a feed triggers a refresh spinner before new content loads."

    card_apps = [f"com.app.card{i}" for i in range(4)]
    for i, app_id in enumerate(card_apps):
        app_dir = harness / "apps" / "android" / app_id
        app_dir.mkdir(parents=True)
        flow_note = tagged_bullet if i < n_tagged_cards else plain_bullet
        (app_dir / "CARD.md").write_text(CARD_TEMPLATE.format(app_id=app_id, flow_note=flow_note))

    memory_apps = [f"com.app.memory{i}" for i in range(3)]
    for i, app_id in enumerate(memory_apps[:n_tagged_memory_apps]):
        (harness / "memory" / "apps" / f"{app_id}.md").write_text(
            f"- 2026-07-17: Pulling down on a feed triggers a refresh spinner. "
            f"<!-- generalizable: pull-refresh --> Source: observed. Confidence: observed.\n"
        )

    if add_freeform_memory:
        (harness / "memory" / "session-notes.md").write_text(
            "- 2026-07-17: Saw the same refresh pattern across a few apps today. "
            "<!-- generalizable: pull-refresh --> Source: observed. Confidence: unverified.\n"
        )

    return harness


# ── find_cards / find_memory ─────────────────────────────────────────

def test_find_cards_returns_card_prefixed_source():
    with tempfile.TemporaryDirectory() as tmp:
        harness = make_harness(Path(tmp), n_tagged_cards=3)
        cards = list(C.find_cards(harness))
        assert len(cards) == 4
        assert all(source == "card:android" for source, *_r in cards)


def test_find_memory_splits_apps_vs_freeform():
    with tempfile.TemporaryDirectory() as tmp:
        harness = make_harness(Path(tmp), n_tagged_memory_apps=2, add_freeform_memory=True)
        records = list(C.find_memory(harness))
        by_source = {r[0] for r in records}
        assert by_source == {"memory:apps", "memory:freeform"}
        apps_records = [r for r in records if r[0] == "memory:apps"]
        assert len(apps_records) == 2
        assert all(app_id is not None for _s, app_id, _p, _t in apps_records)
        freeform = [r for r in records if r[0] == "memory:freeform"]
        assert len(freeform) == 1
        assert freeform[0][1] is None, "freeform memory files must not get an app_id"


def test_local_overlay_is_never_scanned_or_promoted():
    """local/ holds the user's own cards -- private apps, internal builds,
    personal overrides. Those must never reach a shared core/ promotion, no
    matter how many of them carry a generalizable tag. find_cards() walks
    <harness>/apps specifically, so the overlay is invisible by construction;
    this pins that down before someone widens the glob to rglob("CARD.md").
    """
    with tempfile.TemporaryDirectory() as tmp:
        harness = make_harness(Path(tmp), n_tagged_cards=0)
        # Three local cards, all tagged -- enough to cross any threshold if seen.
        for i in range(3):
            d = harness / "local" / "apps" / "android" / f"com.private.app{i}"
            d.mkdir(parents=True)
            (d / "CARD.md").write_text(CARD_TEMPLATE.format(
                app_id=f"com.private.app{i}",
                flow_note="- Internal build hides the tab bar. <!-- generalizable: secret-pattern -->",
            ))
        (harness / "local" / "README.md").write_text("# Local Overlay\n")

        card_paths = [p for _s, _a, p, _t in C.find_cards(harness)]
        assert not any("local" in p.parts for p in card_paths), (
            f"find_cards() reached into local/: {card_paths}"
        )
        mem_paths = [p for _s, _a, p, _t in C.find_memory(harness)]
        assert not any("local" in p.parts for p in mem_paths), (
            f"find_memory() reached into local/: {mem_paths}"
        )

        records = list(C.find_cards(harness)) + list(C.find_memory(harness))
        tagged = C.collect_tagged(records)
        assert "secret-pattern" not in tagged, (
            "a tag confined to local/ became a promotion candidate; user overrides "
            "must never be promoted into shared core/ knowledge"
        )


# ── collect_tagged: cards + memory combined ──────────────────────────

def test_collect_tagged_counts_cards_and_memory_apps_toward_threshold():
    with tempfile.TemporaryDirectory() as tmp:
        # 2 tagged cards + 1 tagged memory/apps file = 3 distinct apps, meets default threshold.
        harness = make_harness(Path(tmp), n_tagged_cards=2, n_tagged_memory_apps=1)
        records = list(C.find_cards(harness)) + list(C.find_memory(harness))
        tagged = C.collect_tagged(records)
        assert "pull-refresh" in tagged
        distinct_apps = {app for _s, app, _sec, _b in tagged["pull-refresh"] if app}
        assert len(distinct_apps) == 3


def test_collect_tagged_freeform_memory_excluded_from_app_count():
    with tempfile.TemporaryDirectory() as tmp:
        # Only 2 real apps tag it; the freeform file also mentions it but must not
        # push the distinct-app count over the threshold on its own.
        harness = make_harness(Path(tmp), n_tagged_cards=2, add_freeform_memory=True)
        records = list(C.find_cards(harness)) + list(C.find_memory(harness))
        tagged = C.collect_tagged(records)
        distinct_apps = {app for _s, app, _sec, _b in tagged["pull-refresh"] if app}
        assert len(distinct_apps) == 2, "freeform memory (app_id=None) must not count as a distinct app"
        # but it should still be present in the raw entries, for visibility in the report
        all_entries = tagged["pull-refresh"]
        assert any(app is None for _s, app, _sec, _b in all_entries)


def test_promotion_threshold_respected():
    with tempfile.TemporaryDirectory() as tmp:
        harness = make_harness(Path(tmp), n_tagged_cards=2)  # below default min-apps=3
        records = list(C.find_cards(harness)) + list(C.find_memory(harness))
        tagged = C.collect_tagged(records)
        promotions = {t: e for t, e in tagged.items()
                      if len({a for _s, a, _sec, _b in e if a}) >= 3}
        assert "pull-refresh" not in promotions


# ── --apply: drafting into core/mobile-ux-primitives/<file>.md ──────

def test_apply_drafts_marked_block_and_only_appends():
    with tempfile.TemporaryDirectory() as tmp:
        harness = make_harness(Path(tmp), n_tagged_cards=3)
        target_path = harness / "core" / "mobile-ux-primitives" / "content-and-feeds.md"
        before = target_path.read_text()

        records = list(C.find_cards(harness)) + list(C.find_memory(harness))
        tagged = C.collect_tagged(records)
        promotions = {t: e for t, e in tagged.items()
                      if len({a for _s, a, _sec, _b in e if a}) >= 3}
        assert "pull-refresh" in promotions

        written = C.apply_drafts(harness, promotions)
        assert str(target_path) in written

        after = target_path.read_text()
        assert after.startswith(before), "apply_drafts must only append, never rewrite existing prose"
        assert "<!-- BEGIN curator-candidate" in after
        assert "<!-- END curator-candidate -->" in after
        assert "pull-refresh" in after


def test_default_run_never_writes_to_core_or_apps_or_memory():
    with tempfile.TemporaryDirectory() as tmp:
        harness = make_harness(Path(tmp), n_tagged_cards=3)
        before = {
            p: p.read_text() for p in harness.rglob("*")
            if p.is_file() and any(part in ("core", "apps", "memory") for part in p.parts)
        }
        out_dir = Path(tmp) / "report-out"
        sys.argv = ["curate.py", "--harness", str(harness), "--out", str(out_dir)]
        C.main()
        after = {
            p: p.read_text() for p in harness.rglob("*")
            if p.is_file() and any(part in ("core", "apps", "memory") for part in p.parts)
        }
        assert before == after, "without --apply, curate.py must never modify core/, apps/, or memory/"
        reports = list(out_dir.glob("curator-report-*.md"))
        assert len(reports) == 1
        report_text = reports[0].read_text()
        assert "pull-refresh" in report_text
        assert "Nothing has been written to `core/` or `apps/`" in report_text


def test_apply_flag_end_to_end_via_main():
    with tempfile.TemporaryDirectory() as tmp:
        harness = make_harness(Path(tmp), n_tagged_cards=3)
        target_path = harness / "core" / "mobile-ux-primitives" / "content-and-feeds.md"
        out_dir = Path(tmp) / "report-out"
        sys.argv = ["curate.py", "--harness", str(harness), "--out", str(out_dir), "--apply"]
        C.main()
        assert "curator-candidate" in target_path.read_text()
        # apps/ must still be untouched even with --apply
        card_path = harness / "apps" / "android" / "com.app.card0" / "CARD.md"
        assert "curator-candidate" not in card_path.read_text()


def test_no_apps_or_memory_dir_exits_cleanly():
    with tempfile.TemporaryDirectory() as tmp:
        empty_harness = Path(tmp) / "empty-harness"
        empty_harness.mkdir()
        assert list(C.find_cards(empty_harness)) == []
        assert list(C.find_memory(empty_harness)) == []


# ── runner (no pytest dependency required) ───────────────────────────

def _run_all():
    tests = [(name, fn) for name, fn in list(globals().items())
             if name.startswith("test_") and callable(fn)]
    passed, failed = 0, []
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
            passed += 1
        except Exception:
            print(f"  FAIL  {name}")
            traceback.print_exc()
            failed.append(name)
    print(f"\n{passed}/{len(tests)} passed")
    if failed:
        print("Failed: " + ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    _run_all()
