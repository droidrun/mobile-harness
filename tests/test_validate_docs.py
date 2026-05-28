from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validate_docs():
    spec = importlib.util.spec_from_file_location("validate_docs", ROOT / "scripts/validate_docs.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["validate_docs"] = module
    spec.loader.exec_module(module)
    return module


class ValidateDocsTest(unittest.TestCase):
    def test_current_repo_validates(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/validate_docs.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("validate_docs: ok", result.stdout)

    def test_frontmatter_validation_reports_missing_fields(self) -> None:
        module = load_validate_docs()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text("---\nname: only-name\n---\n# Body\n", encoding="utf-8")
            errors: list[str] = []
            module.validate_frontmatter(path, errors)
            self.assertTrue(any("missing description" in error for error in errors))

    def test_frontmatter_validation_accepts_name_and_description(self) -> None:
        module = load_validate_docs()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text("---\nname: test\ndescription: useful\n---\n# Body\n", encoding="utf-8")
            errors: list[str] = []
            module.validate_frontmatter(path, errors)
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
