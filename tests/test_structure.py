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
import subprocess
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE_DIR = REPO_ROOT / "core"
PLATFORMS_DIR = REPO_ROOT / "platforms"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
# Matches `core/<x>` / `core/<x>/GUIDE.md` and `platforms/<p>/GUIDE.md` /
# `platforms/<p>/recovery/GUIDE.md`-shaped references inside backticks.
REF_RE = re.compile(r"`((?:core|platforms|apps|scripts|tests|local)/[\w./-]+)`")

# Agent-owned local state, gitignored and with no fixed structure to check:
# excluded from the repo-wide scan below.
EXCLUDED_DIRS = {"memory", "credentials", ".curator"}

# local/ is the user's own overlay: gitignored except for its README, and its
# contents are whatever the user put there. Lint the tracked README, never the
# user's files -- a personal card must not be able to fail the repo's tests.
LOCAL_TRACKED = Path("local/README.md")


def all_core_guides():
    return sorted(CORE_DIR.glob("*/GUIDE.md"))


def all_repo_markdown():
    """Every committed .md file except agent-owned local state."""
    for path in REPO_ROOT.rglob("*.md"):
        rel = path.relative_to(REPO_ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if rel.parts[0] == "local" and rel != LOCAL_TRACKED:
            continue
        yield path


def _git(*args):
    """Run a git command in REPO_ROOT. Returns (returncode, stdout) or None if
    git is unavailable / this isn't a checkout, so the suite still runs from a
    plain unpacked copy."""
    try:
        p = subprocess.run(("git", "-C", str(REPO_ROOT)) + args,
                           capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode > 1:  # 128 == not a repo, etc. 0/1 are real answers.
        return None
    return p.returncode, p.stdout


def test_every_core_dir_has_a_guide_not_a_skill_file():
    skill_files = list(CORE_DIR.glob("*/SKILL.md"))
    assert not skill_files, (
        f"found leftover SKILL.md under core/, should be GUIDE.md: {skill_files}"
    )


def test_every_guide_has_name_and_description_frontmatter():
    guides = all_core_guides() + sorted(PLATFORMS_DIR.glob("*/GUIDE.md")) + sorted(PLATFORMS_DIR.glob("*/*/GUIDE.md"))
    assert guides, "expected at least one core/*/GUIDE.md or platforms/**/GUIDE.md"
    for path in guides:
        text = path.read_text()
        m = FRONTMATTER_RE.match(text)
        assert m, f"{path}: missing --- frontmatter block"
        fm = m.group(1)
        assert re.search(r"^name:\s*\S+", fm, re.MULTILINE), f"{path}: frontmatter missing name:"
        assert re.search(r"^description:\s*\S+", fm, re.MULTILINE), f"{path}: frontmatter missing description:"


def test_cross_references_resolve_repo_wide():
    """Every `core/<x>`, `platforms/<p>/GUIDE.md`, or `apps/index.md`-shaped
    reference anywhere in the repo (AGENTS.md, SKILL.md, README.md,
    install.md, platforms/**, core/**) must correspond to a real path.
    Excludes CARD.md-style app-id placeholders like `apps/android/<package>/CARD.md`,
    which are intentionally not real paths.
    """
    broken = []
    for path in all_repo_markdown():
        text = path.read_text()
        for ref in REF_RE.findall(text):
            if "<" in ref:  # placeholder path, e.g. apps/android/<package>/CARD.md
                continue
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


def test_no_unreviewed_curator_draft_is_committed_under_core():
    """`--apply` writes a deliberately loud, unreviewed block for a human to fold
    in or delete. One got committed into content-and-feeds.md, which meant every
    agent reading that guide read raw curator output as if it were guidance —
    and the block is what the review step is supposed to consume, not ship.
    """
    leaked = [str(path.relative_to(REPO_ROOT)) for path in CORE_DIR.rglob("*.md")
              if "curator-candidate" in path.read_text()]
    assert not leaked, (
        "unreviewed curator draft block(s) committed under core/ — fold the content "
        "into prose or delete the block:\n  " + "\n  ".join(leaked)
    )


def test_local_overlay_is_gitignored_but_its_readme_is_not():
    """The entire point of local/ is that a user can override or add a card
    without ever dirtying a tracked file, so `git pull --ff-only` at session
    start keeps fast-forwarding. That guarantee lives entirely in .gitignore,
    so assert git's real answer rather than trusting the patterns by eye.
    """
    res = _git("rev-parse", "--git-dir")
    if res is None:
        print("       (skipped: not a git checkout)")
        return

    must_be_ignored = [
        "local/apps/android/com.example.app/CARD.md",
        "local/apps/ios/com.example.ios/CARD.md",
        "local/core/memory/GUIDE.md",
        "local/notes.md",
    ]
    for rel in must_be_ignored:
        res = _git("check-ignore", "-q", rel)
        assert res is not None and res[0] == 0, (
            f"{rel} is NOT gitignored -- a user's local overlay would dirty the "
            f"worktree and break `git pull --ff-only`"
        )

    res = _git("check-ignore", "-q", str(LOCAL_TRACKED))
    assert res is not None and res[0] == 1, (
        f"{LOCAL_TRACKED} must stay tracked -- it documents the overlay"
    )


def test_local_overlay_is_documented_where_agents_are_routed():
    """An overlay nothing tells the agent to read is dead weight. AGENTS.md is
    the entry point every runtime loads, so the routing has to be stated there.
    """
    agents = (REPO_ROOT / "AGENTS.md").read_text()
    assert "local/apps/android/<package>/CARD.md" in agents, (
        "AGENTS.md does not tell the agent to read the local/ Android card overlay"
    )
    assert "local/apps/ios/<bundle-id>/CARD.md" in agents, (
        "AGENTS.md does not tell the agent to read the local/ iOS card overlay"
    )
    assert (REPO_ROOT / LOCAL_TRACKED).exists(), (
        "local/README.md is missing; AGENTS.md points at it"
    )


def test_local_overlay_is_documented_where_users_look():
    """local/ is a feature for humans, so agent-facing routing is not enough:
    a user reading README.md front to back has to learn it exists. This was a
    real miss -- the overlay shipped documented only in AGENTS.md, SKILL.md,
    apps/index.md, and local/README.md, i.e. nowhere a user would look first.
    """
    readme = (REPO_ROOT / "README.md").read_text()
    assert "local/" in readme, (
        "README.md never mentions local/ -- a user reading the docs would never "
        "learn the overlay exists"
    )
    assert "local/README.md" in readme, (
        "README.md should point at local/README.md for the full overlay rules"
    )
    assert "--ff-only" in readme, (
        "README.md should say why the overlay exists: editing a tracked file "
        "breaks the session-start `git pull --ff-only`"
    )


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
