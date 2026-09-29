#!/usr/bin/env python3
"""Regression tests for package generation and release safeguards."""

from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts import build, release_check
from tests import check_language_fixtures, run_evaluations


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


class LanguageFixtureTests(unittest.TestCase):
    def test_checks_applied_go_and_java_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory)
            go_repository = cases / "go-case/repository"
            go_repository.mkdir(parents=True)
            (go_repository / "go.mod").write_text("module example.org/check\n")
            (go_repository / "check.go").write_text("package check\n")
            (cases / "go-case/change.diff").write_text("sample patch\n")
            java_repository = cases / "java-case/repository"
            java_repository.mkdir(parents=True)
            (java_repository / "Check.java").write_text("class Check {}\n")
            (cases / "java-case/change.diff").write_text("sample patch\n")

            with patch.object(check_language_fixtures, "CASES", cases), patch.object(
                check_language_fixtures, "run"
            ) as run_command, patch.object(
                check_language_fixtures.subprocess, "run"
            ) as gofmt_command, redirect_stdout(StringIO()):
                gofmt_command.return_value.returncode = 0
                gofmt_command.return_value.stdout = ""
                self.assertEqual(check_language_fixtures.check_fixtures(), 0)

            commands = [invocation.args[0] for invocation in run_command.call_args_list]
            self.assertEqual([command[0] for command in commands].count("git"), 2)
            self.assertIn(["go", "test", "./..."], commands)
            self.assertTrue(any(command[:3] == ["javac", "--release", "17"] for command in commands))
            go_environment = next(
                invocation.args[2] for invocation in run_command.call_args_list
                if invocation.args[0][:2] == ["go", "test"]
            )
            self.assertEqual(go_environment["GOPROXY"], "off")
            self.assertEqual(go_environment["GOTOOLCHAIN"], "local")
            self.assertEqual(gofmt_command.call_args.args[0][:2], ["gofmt", "-l"])

    def test_failure_has_concise_error_message(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory)
            repository = cases / "go-case/repository"
            repository.mkdir(parents=True)
            (repository / "go.mod").write_text("module example.org/check\n")
            (cases / "go-case/change.diff").write_text("sample patch\n")
            output = StringIO()
            with patch.object(check_language_fixtures, "CASES", cases), patch.object(
                check_language_fixtures, "run", side_effect=RuntimeError("patch failed")
            ), redirect_stdout(output):
                self.assertEqual(check_language_fixtures.main(), 1)
            self.assertEqual(output.getvalue(), "ERROR: patch failed\n")


class EvaluationFixtureTests(unittest.TestCase):
    def test_negative_cases_require_no_findings_and_empty_finding_fields(self) -> None:
        valid = {
            "must_report": [],
            "must_not_report": ["An unsupported finding"],
            "prefixes": [],
            "output": "no_findings",
        }
        case_path = Path("tests/cases/example/case.json")
        self.assertEqual(run_evaluations.negative_expectation_errors(valid, case_path), [])

        invalid_values = {
            "output": "findings",
            "must_report": ["A finding"],
            "prefixes": ["MUST(Functionality)"],
            "must_not_report": [],
        }
        for field, value in invalid_values.items():
            with self.subTest(field=field):
                expectations = {**valid, field: value}
                errors = run_evaluations.negative_expectation_errors(
                    expectations, case_path
                )
                self.assertEqual(len(errors), 1)
                self.assertIn(field if field != "output" else "no_findings", errors[0])


if __name__ == "__main__":
    unittest.main()
