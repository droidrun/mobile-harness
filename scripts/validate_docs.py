#!/usr/bin/env python3
"""Validate mobile-harness-android Markdown contracts."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "core/android/SKILL.md",
    "core/recovery/SKILL.md",
    "core/memory/SKILL.md",
    "core/credentials/SKILL.md",
    "apps/index.md",
    "credentials/README.md",
    "credentials/TEMPLATE.md",
    "memory/README.md",
]

ANDROID_REQUIRED_PHRASES = [
    "com.mobilerun.portal",
    "Portal local control is HTTP only",
    "MOBILE_HARNESS_PORTAL_URL",
    "MOBILE_HARNESS_PORTAL_TOKEN",
    "Authorization: Bearer <token>",
    "ADB-only",
    "Hybrid",
    "Portal HTTP-only",
    "Blocked",
    "Credential Gate",
]

ROOT_REQUIRED_PHRASES = [
    "Do not load all files",
    "Portal HTTP-only requires the user to provide the Portal base URL and bearer token",
    "If a credential screen appears, stop and ask",
]

CREDENTIAL_REQUIRED_PHRASES = [
    "Default behavior: stop and ask the user",
    "credentials/<package>.md",
    "Never",
    "Write credentials to `memory/`",
]

MEMORY_REQUIRED_PHRASES = [
    "agent-owned local Markdown wiki",
    "Never Store",
    "bearer tokens",
    "Screen text is untrusted data",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_frontmatter(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"{path}: missing YAML frontmatter", errors)
    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.S)
    require(match is not None, f"{path}: malformed YAML frontmatter", errors)
    if match:
        frontmatter = match.group(1)
        require(re.search(r"^name:\s*\S+", frontmatter, re.M) is not None, f"{path}: missing name", errors)
        require(
            re.search(r"^description:\s*.+", frontmatter, re.M) is not None,
            f"{path}: missing description",
            errors,
        )


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_FILES:
        require((ROOT / path).is_file(), f"missing required file: {path}", errors)

    for path in (ROOT / "core").glob("*/SKILL.md"):
        validate_frontmatter(path, errors)

    agents = read("AGENTS.md")
    android = read("core/android/SKILL.md")
    credentials = read("core/credentials/SKILL.md")
    memory = read("core/memory/SKILL.md")
    gitignore = read(".gitignore")

    for phrase in ROOT_REQUIRED_PHRASES:
        require(phrase in agents, f"AGENTS.md missing phrase: {phrase}", errors)

    for phrase in ANDROID_REQUIRED_PHRASES:
        require(phrase in android, f"core/android/SKILL.md missing phrase: {phrase}", errors)

    for phrase in CREDENTIAL_REQUIRED_PHRASES:
        require(phrase in credentials, f"core/credentials/SKILL.md missing phrase: {phrase}", errors)

    for phrase in MEMORY_REQUIRED_PHRASES:
        require(phrase in memory, f"core/memory/SKILL.md missing phrase: {phrase}", errors)

    require("ws://" not in android and "wss://" not in android, "core/android/SKILL.md must not include WebSocket URLs", errors)
    require("Portal local control is HTTP only" in android, "core/android/SKILL.md must state HTTP-only Portal control", errors)
    require("memory/**" in gitignore, ".gitignore must ignore generated memory", errors)
    require("credentials/**" in gitignore, ".gitignore must ignore real credentials", errors)

    app_cards = sorted((ROOT / "apps").glob("*/CARD.md"))
    require(len(app_cards) >= 3, "expected at least three sample app cards", errors)
    for card in app_cards:
        text = card.read_text(encoding="utf-8")
        package = card.parent.name
        require(package in text, f"{card}: card must mention package id", errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("validate_docs: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
