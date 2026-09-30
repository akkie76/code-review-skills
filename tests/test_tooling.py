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
    def test_checks_applied_go_java_and_python_fixtures(self) -> None:
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
            python_repository = cases / "python-case/repository"
            python_repository.mkdir(parents=True)
            (python_repository / "check.py").write_text("value = 1\n")
            (python_repository / "test_check.py").write_text("import unittest\n")
            (cases / "python-case/change.diff").write_text("sample patch\n")
            python_without_tests = cases / "python-no-tests/repository"
            python_without_tests.mkdir(parents=True)
            (python_without_tests / "check.py").write_text("value = 1\n")
            (cases / "python-no-tests/change.diff").write_text("sample patch\n")

            with patch.object(check_language_fixtures, "CASES", cases), patch.object(
                check_language_fixtures, "run"
            ) as run_command, patch.object(
                check_language_fixtures.subprocess, "run"
            ) as gofmt_command, redirect_stdout(StringIO()):
                gofmt_command.return_value.returncode = 0
                gofmt_command.return_value.stdout = ""
                self.assertEqual(check_language_fixtures.check_fixtures(), 0)

            commands = [invocation.args[0] for invocation in run_command.call_args_list]
            self.assertEqual([command[0] for command in commands].count("git"), 4)
            self.assertIn(["go", "test", "./..."], commands)
            self.assertTrue(any(command[:3] == ["javac", "--release", "17"] for command in commands))
            self.assertTrue(any(command[1:] == ["-m", "compileall", "-q", "."] for command in commands))
            self.assertEqual(
                sum(command[1:3] == ["-m", "unittest"] for command in commands), 1
            )
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

    def test_mixed_noise_cases_need_evidence_and_both_candidate_types(self) -> None:
        case = {
            "kind": "positive",
            "source": "original-synthetic",
            "ecosystem": "Go 1.22",
            "assumptions": ["Documented contract"],
            "limitations": ["No model execution"],
            "expected_evidence": ["Changed function and unchanged caller"],
            "expectations": {
                "must_report": ["Valid defect"],
                "must_not_report": ["Invalid candidate"],
            },
        }
        case_path = Path("tests/cases/example/case.json")
        self.assertEqual(run_evaluations.mixed_noise_errors(case, case_path), [])
        incomplete = {
            **case,
            "expected_evidence": [],
            "expectations": {"must_report": ["Valid defect"], "must_not_report": []},
        }
        errors = run_evaluations.mixed_noise_errors(incomplete, case_path)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("expected_evidence" in error for error in errors))
        self.assertTrue(any("valid and invalid candidates" in error for error in errors))
        for field in ("must_report", "must_not_report"):
            invalid_values = (
                "candidate", {"finding": "candidate"}, [""], ["  "],
                [42], ["valid", None],
            )
            for invalid in invalid_values:
                with self.subTest(field=field, invalid=invalid):
                    malformed = {
                        **case,
                        "expectations": {**case["expectations"], field: invalid},
                    }
                    errors = run_evaluations.mixed_noise_errors(malformed, case_path)
                    self.assertEqual(len(errors), 1)
                    self.assertIn("valid and invalid candidates", errors[0])
        external = {**case, "source": "https://example.org/source"}
        errors = run_evaluations.mixed_noise_errors(external, case_path)
        self.assertEqual(len(errors), 4)
        self.assertTrue(any("redistribution_basis" in error for error in errors))

    def test_optional_findings_must_be_nonempty_text(self) -> None:
        self.assertTrue(run_evaluations.is_nonempty_text_list(["Valid test gap"]))
        for invalid in ([], [""], [42], "Valid test gap"):
            with self.subTest(invalid=invalid):
                self.assertFalse(run_evaluations.is_nonempty_text_list(invalid))


if __name__ == "__main__":
    unittest.main()
