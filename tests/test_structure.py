#!/usr/bin/env python3
"""
test_structure.py — Structural lint for this checkout, focused on catching
the exact mistake a hand-adapted port is prone to: a cross-reference that
looks right but points at a path that doesn't actually exist.

Checks every core/*/GUIDE.md and *.md reference file for:
  - valid frontmatter (name + description present)
  - every `core/<x>` or `core/<x>/GUIDE.md`-shaped reference in the body
    resolves to a real file or directory in this checkout
  - no leftover references to the old `SKILL.md` filename within core/
    (the port renamed these to GUIDE.md; a stray reference would be a bug)

Deliberately narrow: this is a lint pass, not a behavior test. It can't tell
you whether the content is *good*, only that it's internally consistent.

Run:
  python3 tests/test_structure.py
"""
import re
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = REPO_ROOT / "core"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
CORE_REF_RE = re.compile(r"`(core/[\w-]+(?:/GUIDE\.md)?)`")


def all_core_guides():
    return sorted(CORE_DIR.glob("*/GUIDE.md"))


def test_every_core_dir_has_a_guide_not_a_skill_file():
    skill_files = list(CORE_DIR.glob("*/SKILL.md"))
    assert not skill_files, (
        f"found leftover SKILL.md under core/, should be GUIDE.md: {skill_files}"
    )


def test_every_guide_has_name_and_description_frontmatter():
    guides = all_core_guides()
    assert guides, "expected at least one core/*/GUIDE.md"
    for path in guides:
        text = path.read_text()
        m = FRONTMATTER_RE.match(text)
        assert m, f"{path}: missing --- frontmatter block"
        fm = m.group(1)
        assert re.search(r"^name:\s*\S+", fm, re.MULTILINE), f"{path}: frontmatter missing name:"
        assert re.search(r"^description:\s*\S+", fm, re.MULTILINE), f"{path}: frontmatter missing description:"


def test_core_cross_references_resolve():
    """Every `core/<x>` or `core/<x>/GUIDE.md` mentioned in a core/*/GUIDE.md's
    body (or its reference files) must correspond to a real path in this repo.
    """
    checked_files = list(all_core_guides()) + list(CORE_DIR.glob("*/*.md"))
    broken = []
    for path in checked_files:
        text = path.read_text()
        for ref in CORE_REF_RE.findall(text):
            target = REPO_ROOT / ref
            # Accept either the literal path, or (if it names a bare `core/<x>`
            # without /GUIDE.md) the directory existing with a GUIDE.md inside.
            resolves = target.exists() or (REPO_ROOT / ref / "GUIDE.md").exists()
            if not resolves:
                broken.append(f"{path.relative_to(REPO_ROOT)}: `{ref}` does not resolve")
    assert not broken, "broken cross-references found:\n" + "\n".join(broken)


def test_no_stray_skill_md_references_within_core():
    """The port renamed core/mobile-ux-primitives/SKILL.md and
    core/learn-from-tutorial/SKILL.md to GUIDE.md. Any remaining reference to
    those specific paths under core/ is a leftover from the pre-port content.
    """
    stale_patterns = ["core/mobile-ux-primitives/SKILL.md", "core/learn-from-tutorial/SKILL.md"]
    hits = []
    for path in list(all_core_guides()) + list(CORE_DIR.glob("*/*.md")):
        text = path.read_text()
        for pat in stale_patterns:
            if pat in text:
                hits.append(f"{path.relative_to(REPO_ROOT)}: references stale path `{pat}`")
    assert not hits, "stale SKILL.md references found:\n" + "\n".join(hits)


def test_apply_target_files_exist_for_every_ux_primitive_reference_file():
    """curate.py's TARGET_HINTS names five files under core/mobile-ux-primitives/;
    if that directory's layout ever changes, --apply would silently no-op for
    whichever target file went missing. Guard against that drift here rather
    than only discovering it at runtime.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import curate as C  # noqa: E402
    ux_dir = CORE_DIR / "mobile-ux-primitives"
    for target_file, _keywords in C.TARGET_HINTS:
        assert (ux_dir / target_file).exists(), f"curate.py targets {target_file}, but it doesn't exist under {ux_dir}"


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
