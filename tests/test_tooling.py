#!/usr/bin/env python3
"""Regression tests for package generation and release safeguards."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build, release_check


class ReleaseCheckTests(unittest.TestCase):
    def test_detects_supported_github_token_formats(self) -> None:
        pattern = release_check.SECRET_PATTERNS["GitHub token"]
        legacy_token = "gh" + "p_" + "a" * 36
        fine_grained_token = "github" + "_pat_" + "a" * 30

        self.assertIsNotNone(pattern.search(legacy_token))
        self.assertIsNotNone(pattern.search(fine_grained_token))
        self.assertIsNone(pattern.search("github_pat_example"))

    def test_detects_supported_platform_home_paths(self) -> None:
        separator = chr(92)
        paths = (
            "/" + "Users/alice/project/file",
            "/" + "home/alice/project/file",
            f"C:{separator}Users{separator}alice{separator}project{separator}file",
            "D:/" + "Users/alice/project/file",
        )

        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(release_check.contains_local_home_path(path))
        self.assertFalse(
            release_check.contains_local_home_path("docs/INSTALLATION.md")
        )


class BuildTests(unittest.TestCase):
    def test_rejects_and_removes_obsolete_generated_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text("reference\n", encoding="utf-8")
            target = root / "dist/agent/evidence-code-review/SKILL.md"
            targets = {"agent": target}
            references = {Path("references/reference.md"): source}

            with patch.object(build, "ROOT", root), patch.object(
                build, "TARGETS", targets
            ), patch.object(build, "REFERENCE_FILES", references):
                build.write_outputs("generated\n")
                obsolete = target.parent / "obsolete.md"
                obsolete.write_text("obsolete\n", encoding="utf-8")

                errors = build.check_outputs("generated\n")
                self.assertTrue(
                    any("unexpected generated file" in error for error in errors)
                )

                build.write_outputs("generated\n")
                self.assertFalse(obsolete.exists())
                self.assertEqual(build.check_outputs("generated\n"), [])


if __name__ == "__main__":
    unittest.main()
