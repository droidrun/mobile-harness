#!/usr/bin/env python3
"""Run behavior fixtures through fresh Codex CLI processes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/agent_eval/prompts/fixtures.jsonl"
REPORT = ROOT / "tmp/agent-eval-report.json"
CONTEXT_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "core/android/SKILL.md",
    ROOT / "core/recovery/SKILL.md",
    ROOT / "core/credentials/SKILL.md",
    ROOT / "core/memory/SKILL.md",
    ROOT / "apps/index.md",
]

EXPECTED_CATEGORY_COUNTS = {
    "capability": 6,
    "credential": 6,
    "app-card": 6,
    "memory": 6,
    "recovery": 6,
}

ALLOWED_DECISIONS = [
    "HYBRID",
    "ADB_ONLY",
    "PORTAL_HTTP_ONLY",
    "BLOCKED",
    "STOP_AND_ASK_CREDENTIAL",
    "READ_APP_CARD apps/com.google.android.gm/CARD.md",
    "READ_APP_CARD apps/com.android.chrome/CARD.md",
    "READ_APP_CARD apps/com.android.settings/CARD.md",
    "USE_GENERIC_ANDROID",
    "READ_MEMORY",
    "WRITE_MEMORY",
    "DO_NOT_WRITE_MEMORY",
    "READ_RECOVERY",
]


@dataclass
class FixtureResult:
    id: str
    category: str
    expected: str
    ok: bool
    output: str
    returncode: int
    stderr: str


def load_fixtures() -> list[dict[str, str]]:
    fixtures: list[dict[str, str]] = []
    with FIXTURES.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{FIXTURES}:{line_number}: invalid JSON: {exc}") from exc
            for key in ("id", "category", "prompt", "expected"):
                if key not in item:
                    raise ValueError(f"{FIXTURES}:{line_number}: missing {key}")
            fixtures.append(item)

    counts: dict[str, int] = {}
    for item in fixtures:
        counts[item["category"]] = counts.get(item["category"], 0) + 1

    if len(fixtures) != 30:
        raise ValueError(f"expected 30 fixtures, found {len(fixtures)}")
    if counts != EXPECTED_CATEGORY_COUNTS:
        raise ValueError(f"unexpected category counts: {counts}")

    return fixtures


def load_harness_context() -> str:
    parts: list[str] = []
    paths = CONTEXT_FILES + sorted((ROOT / "apps").glob("*/CARD.md"))
    for path in paths:
        rel = path.relative_to(ROOT)
        parts.append(f"## {rel}\n\n```markdown\n{path.read_text(encoding='utf-8')}\n```")
    return "\n\n".join(parts)


def build_prompt(fixture: dict[str, str], harness_context: str) -> str:
    decisions = "\n".join(f"- {decision}" for decision in ALLOWED_DECISIONS)
    return f"""You are evaluating the Android mobile harness instructions in this repository.

Use the embedded harness Markdown context below as authoritative. Do not edit files. Do not run shell commands.

Return exactly one line in this form:
DECISION: <one allowed decision>

Allowed decisions:
{decisions}

Harness context:
<harness_context>
{harness_context}
</harness_context>

Scenario:
{fixture["prompt"]}
"""


def run_fixture(codex: str, fixture: dict[str, str], timeout: int, harness_context: str) -> FixtureResult:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f"{fixture['id']}-", suffix=".txt", dir=REPORT.parent, delete=False) as output_file:
        output_path = Path(output_file.name)

    cmd = [
        codex,
        "exec",
        "--ephemeral",
        "-C",
        str(ROOT),
        "-s",
        "read-only",
        "--output-last-message",
        str(output_path),
        build_prompt(fixture, harness_context),
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )

    output = output_path.read_text(encoding="utf-8", errors="replace").strip() if output_path.exists() else ""
    expected = fixture["expected"]
    normalized = " ".join(output.upper().split())
    ok = proc.returncode == 0 and f"DECISION: {expected.upper()}" in normalized
    return FixtureResult(
        id=fixture["id"],
        category=fixture["category"],
        expected=expected,
        ok=ok,
        output=output,
        returncode=proc.returncode,
        stderr=proc.stderr.strip(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex", required=True)
    parser.add_argument("--parallel", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    fixtures = load_fixtures()
    harness_context = load_harness_context()
    results: list[FixtureResult] = []

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = [pool.submit(run_fixture, args.codex, fixture, args.timeout, harness_context) for fixture in fixtures]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(("PASS" if result.ok else "FAIL") + f": {result.id}")

    results.sort(key=lambda item: item.id)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps({"ok": all(item.ok for item in results), "results": [asdict(item) for item in results]}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    failures = [item for item in results if not item.ok]
    if failures:
        for failure in failures:
            print(
                f"FAIL: {failure.id} expected={failure.expected!r} returncode={failure.returncode} output={failure.output!r} stderr={failure.stderr!r}",
                file=sys.stderr,
            )
        return 1

    print(f"agent_eval: ok ({len(results)} fixtures)")
    print(f"report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
