#!/usr/bin/env python3
"""Regression tests for package generation and release safeguards."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts import build, release_check
from tests import agent_eval, check_language_fixtures, run_evaluations


class AgentEvaluationTests(unittest.TestCase):
    def test_dry_run_never_calls_agent(self) -> None:
        with patch.object(agent_eval, "evaluate_one") as evaluate, redirect_stdout(StringIO()) as output:
            self.assertEqual(
                agent_eval.main(["--case", "negative-refactor", "--runs", "2"]), 0
            )
        evaluate.assert_not_called()
        self.assertIn("No model calls made", output.getvalue())

    def test_prepare_repository_installs_skill_and_exposes_diff(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "fixture"
            agent_eval.prepare_repository(
                agent_eval.CASES / "negative-refactor", destination
            )
            self.assertTrue(
                (destination / ".agents/skills/evidence-code-review/SKILL.md").is_file()
            )
            diff = agent_eval.run_command(["git", "diff", "--name-only"], destination)
            self.assertEqual(diff.returncode, 0)
            self.assertIn("ReportService.java", diff.stdout)
            self.assertNotIn("SKILL.md", diff.stdout)
            author = agent_eval.run_command(
                ["git", "show", "-s", "--format=%an <%ae>", "HEAD"], destination
            )
            self.assertEqual(author.stdout.strip(), "Developer <dev@example.invalid>")

    def test_observed_checks_are_provisional(self) -> None:
        positive = agent_eval.observed_output(
            "- MUST(Functionality): confirmed defect\n", {
                "prefixes": ["MUST(Functionality)"], "output": "findings"
            }
        )
        self.assertTrue(positive["required_prefixes_present"])
        self.assertEqual(positive["semantic_judgment"], "pending_human_review")
        negative = agent_eval.observed_output(
            "No findings.\n", {"prefixes": [], "output": "no_findings"}
        )
        self.assertTrue(negative["negative_output_check"])

    def test_realistic_negative_answers_are_syntax_checks_only(self) -> None:
        expected = {"prefixes": [], "output": "no_findings"}
        answers = (
            "No actionable findings. Removing the nil check preserves behavior.",
            "No actionable defects found. The refactor preserves the output.",
            "I found no actionable defects in the working tree change.",
            "I found nothing that needs to change.",
            "変更を確認しました。修正が必要な指摘はありません。",
            "修正が必要な不具合は見つかりませんでした。",
        )
        for answer in answers:
            with self.subTest(answer=answer):
                observed = agent_eval.observed_output(answer, expected)
                self.assertTrue(observed["negative_output_check"])
                self.assertTrue(observed["explicit_no_findings"])
                self.assertEqual(observed["semantic_judgment"], "pending_human_review")
        # An unprefixed claim still requires human judgment, not automatic passing.
        observed = agent_eval.observed_output("The return value is wrong.", expected)
        self.assertTrue(observed["negative_output_check"])
        self.assertFalse(observed["explicit_no_findings"])
        self.assertEqual(observed["semantic_judgment"], "pending_human_review")
        for answer in ("", " \n"):
            self.assertFalse(agent_eval.observed_output(answer, expected)["negative_output_check"])
        contradictory = agent_eval.observed_output(
            "No findings.\n### MUST(Functionality): A verified defect", expected
        )
        self.assertTrue(contradictory["explicit_no_findings"])
        self.assertFalse(contradictory["negative_output_check"])

    def test_finding_prefixes_accept_review_markdown(self) -> None:
        expected = {"prefixes": ["MUST(Functionality)"], "output": "findings"}
        for title in (
            "### MUST(Functionality): A verified defect",
            "1. **MUST(Functionality): A verified defect**",
            "2) __MUST(Functionality)__: A verified defect",
            "- `MUST(Functionality): A verified defect`",
            "**MUST(Functionality)**: A verified defect",
            "> ### MUST(Functionality): A verified defect",
        ):
            with self.subTest(title=title):
                observed = agent_eval.observed_output(title, expected)
                self.assertEqual(observed["prefixes"], ["MUST(Functionality)"])
                self.assertTrue(observed["required_prefixes_present"])
        prose = agent_eval.observed_output(
            "Use MUST(Functionality): only for proven defects.", expected
        )
        self.assertEqual(prose["prefixes"], [])

    def test_reported_model_uses_metadata_not_review_prose(self) -> None:
        self.assertEqual(
            agent_eval.reported_model('{"type":"thread.started","model":"reported-model"}', ""),
            {"model": "reported-model", "source": "event"},
        )
        self.assertEqual(
            agent_eval.reported_model("", "OpenAI Codex\nmodel: reported-model\n"),
            {"model": "reported-model", "source": "stderr"},
        )
        self.assertEqual(
            agent_eval.reported_model(
                '{"type":"item.completed","model":"mentioned-model"}\n[]\nnot-json',
                "The reviewer mentions model: mentioned-model",
            ),
            {"model": None, "source": "unavailable"},
        )

    def test_package_metadata_tracks_reference_content_and_not_location(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            package.mkdir()
            (package / "SKILL.md").write_text(
                "<!-- skill-version: v0.1.0-beta.2 -->\n"
                + "<!-- source-sha256: " + "a" * 64 + " -->\n",
                encoding="utf-8",
            )
            reference = package / "references" / "criteria.md"
            reference.parent.mkdir()
            reference.write_text("original criteria", encoding="utf-8")
            original = agent_eval.package_metadata(package)
            self.assertEqual(original["version"], "v0.1.0-beta.2")
            self.assertEqual(original["source_sha256"], "a" * 64)
            reference.write_text("changed criteria", encoding="utf-8")
            changed = agent_eval.package_metadata(package)
            self.assertNotEqual(original["package_sha256"], changed["package_sha256"])
            moved = Path(directory) / "moved"
            package.rename(moved)
            self.assertEqual(changed, agent_eval.package_metadata(moved))

    def test_evaluation_captures_copied_skill_and_neutral_repository(self) -> None:
        original_command = agent_eval.run_command

        def fake_agent(args, cwd, **kwargs):
            if args[:2] == ["codex", "exec"]:
                self.assertTrue(cwd.parent.name.startswith("repo-"))
                self.assertNotIn("negative-refactor", str(cwd))
                self.assertEqual(args[-1], "Review the working tree changes.")
                answer = Path(args[args.index("--output-last-message") + 1])
                answer.write_text("No actionable findings. Behavior is preserved.", encoding="utf-8")
                return subprocess.CompletedProcess(args, 0, '{"type":"thread.started"}\n', "")
            return original_command(args, cwd, **kwargs)

        with tempfile.TemporaryDirectory() as directory, patch.object(
            agent_eval, "run_command", side_effect=fake_agent
        ):
            case = json.loads((agent_eval.CASES / "negative-refactor/case.json").read_text())
            result = agent_eval.evaluate_one(
                agent_eval.CASES / "negative-refactor", case,
                "Review the working tree changes.", "en", 1, Path(directory),
                "requested-model", 30,
            )
            self.assertEqual(result["skill"], agent_eval.package_metadata(agent_eval.SKILL))
            self.assertEqual(result["requested_model"], "requested-model")
            self.assertIsNone(result["observed_model"])
            self.assertEqual(result["invocation_mode"], "implicit")
            self.assertTrue(result["observed"]["negative_output_check"])

    def test_summary_records_reported_default_and_rejects_missing_answer(self) -> None:
        for status, expected_exit in (("completed", 0), ("no_answer", 1)):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                destination = Path(directory) / "results"
                result = {"status": status, "exit_code": 0, "observed_model": "reported-model"}
                with patch.object(agent_eval, "evaluate_one", return_value=result), \
                     patch.object(agent_eval.shutil, "which", return_value="codex"), \
                     patch.object(agent_eval, "worktree_dirty", return_value=False), \
                     patch.object(agent_eval, "run_command", return_value=subprocess.CompletedProcess([], 0, "test", "")), \
                     redirect_stdout(StringIO()):
                    self.assertEqual(agent_eval.main([
                        "--case", "negative-refactor", "--execute", "--output-dir", str(destination),
                    ]), expected_exit)
                report = json.loads((destination / "summary.json").read_text())
                self.assertEqual(report["schema_version"], 2)
                self.assertEqual(report["model"], "reported-model")
                self.assertEqual(report["model_source"], "cli_reported")
                self.assertIsNone(report["requested_model"])
                self.assertEqual(report["observed_models"], ["reported-model"])
                self.assertFalse(report["evaluation_inputs_dirty"])

    def test_worktree_state_does_not_treat_git_failure_as_clean(self) -> None:
        with patch.object(agent_eval, "run_command", return_value=subprocess.CompletedProcess([], 1, "", "failure")):
            self.assertIsNone(agent_eval.worktree_dirty())

    def test_event_usage_uses_completed_turn(self) -> None:
        events = '\n'.join([
            '{"type":"thread.started"}',
            '{"type":"turn.completed","usage":{"input_tokens":12,"output_tokens":3}}',
        ])
        self.assertEqual(
            agent_eval.event_usage(events), {"input_tokens": 12, "output_tokens": 3}
        )

    def test_skill_read_requires_successful_completed_command(self) -> None:
        events = '\n'.join([
            '{"type":"item.completed","item":{"type":"command_execution",'
            '"command":"cat .agents/skills/evidence-code-review/SKILL.md",'
            '"exit_code":1,"aggregated_output":"name: evidence-code-review"}}',
            '{"type":"item.completed","item":{"type":"command_execution",'
            '"command":"cat .agents/skills/evidence-code-review/SKILL.md",'
            '"exit_code":0,"aggregated_output":"name: evidence-code-review"}}',
        ])
        self.assertTrue(agent_eval.skill_file_read_observed(events))

    def test_skill_read_accepts_complete_content_before_later_command_failure(self) -> None:
        skill_text = "---\nname: evidence-code-review\n---\n# Complete workflow\n"
        event = {"type": "item.completed", "item": {
            "type": "command_execution",
            "command": "cat .agents/skills/evidence-code-review/SKILL.md && rg --files -g AGENTS.md",
            "exit_code": 1,
            "aggregated_output": skill_text,
        }}
        self.assertTrue(agent_eval.skill_file_read_observed(json.dumps(event), skill_text))
        event["item"]["aggregated_output"] = "name: evidence-code-review"
        self.assertFalse(agent_eval.skill_file_read_observed(json.dumps(event), skill_text))

    def test_auto_language_selects_available_request(self) -> None:
        selected = agent_eval.selected_cases(["must-stale-documentation"], False, "auto")
        self.assertEqual(selected[0][3], "ja")

    def test_rejects_result_directory_inside_repository(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside this repository"):
            agent_eval.output_directory(agent_eval.ROOT / "tests/results/local")

    def test_default_output_rejects_tmpdir_inside_repository_before_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            repository.mkdir()
            nested = repository / "tmp"
            nested.mkdir()
            alias = Path(directory) / "tmp-alias"
            alias.symlink_to(nested, target_is_directory=True)
            for temporary_root in (repository, nested, alias):
                with self.subTest(tmpdir=temporary_root), \
                     patch.object(agent_eval, "ROOT", repository), \
                     patch.dict(os.environ, {"TMPDIR": str(temporary_root)}), \
                     patch.object(tempfile, "tempdir", None), \
                     patch.object(tempfile, "mkdtemp", wraps=tempfile.mkdtemp) as create:
                    with self.assertRaisesRegex(ValueError, "outside this repository"):
                        agent_eval.output_directory(None)
                    create.assert_not_called()
            self.assertEqual(list(nested.iterdir()), [])

    def test_default_output_creates_new_directories_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory).resolve()
            repository = temporary_root / "repository"
            repository.mkdir()
            with patch.object(agent_eval, "ROOT", repository), \
                 patch.dict(os.environ, {"TMPDIR": str(temporary_root)}), \
                 patch.object(tempfile, "tempdir", None):
                first = agent_eval.output_directory(None)
                second = agent_eval.output_directory(None)
            self.assertNotEqual(first, second)
            for destination in (first, second):
                self.assertEqual(destination.parent, temporary_root)
                self.assertTrue(destination.is_dir())
                self.assertEqual(destination.stat().st_mode & 0o777, 0o700)

    def test_explicit_output_rejects_symlink_into_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            repository.mkdir()
            alias = Path(directory) / "alias"
            alias.symlink_to(repository, target_is_directory=True)
            with patch.object(agent_eval, "ROOT", repository):
                with self.assertRaisesRegex(ValueError, "outside this repository"):
                    agent_eval.output_directory(alias / "results")
            self.assertFalse((repository / "results").exists())


class ReleaseCheckTests(unittest.TestCase):
    def test_version_and_generated_package_markers_must_agree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "VERSION").write_text("0.1.0-beta.2\n", encoding="utf-8")
            for agent in ("codex", "claude-code"):
                package = root / "dist" / agent / "evidence-code-review/SKILL.md"
                package.parent.mkdir(parents=True)
                package.write_text("<!-- skill-version: v0.1.0-beta.2 -->\n", encoding="utf-8")
            with patch.object(release_check, "ROOT", root):
                self.assertEqual(release_check.version_consistency_errors(), [])
                (root / "VERSION").write_text("0.1.0-beta.02\n", encoding="utf-8")
                self.assertIn(
                    "valid SemVer", release_check.version_consistency_errors()[0]
                )
                (root / "VERSION").write_text("0.1.0-beta.2\n", encoding="utf-8")
                package.write_text("<!-- skill-version: v0.1.0-beta.1 -->\n", encoding="utf-8")
                errors = release_check.version_consistency_errors()
                self.assertEqual(len(errors), 1)
                self.assertIn("claude-code", errors[0])

    def test_tagged_release_checks_both_languages_and_head_tag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            version = "0.1.0-beta.2"
            tag = f"v{version}"
            (root / "VERSION").write_text(version + "\n", encoding="utf-8")
            for agent in ("codex", "claude-code"):
                package = root / "dist" / agent / "evidence-code-review/SKILL.md"
                package.parent.mkdir(parents=True)
                package.write_text(f"<!-- skill-version: {tag} -->\n", encoding="utf-8")
            releases = root / "docs/releases"
            releases.mkdir(parents=True)
            for suffix in ("", ".ja"):
                (root / f"CHANGELOG{suffix}.md").write_text(
                    f"## [{version}] - 2026-10-02\n"
                    f"[{version}]: https://github.com/akkie76/code-review-skills/releases/tag/{tag}\n",
                    encoding="utf-8",
                )
                (releases / f"{tag}{suffix}.md").write_text(
                    f"# Code Review Skills {tag}\n", encoding="utf-8"
                )
            with patch.object(release_check, "ROOT", root), patch.object(
                release_check, "git", return_value=tag + "\n"
            ) as git_command:
                self.assertEqual(release_check.version_consistency_errors(True), [])
                git_command.assert_called_with("tag", "--points-at", "HEAD")
                git_command.return_value = ""
                self.assertIn(
                    f"Git tag {tag} must point to HEAD",
                    release_check.version_consistency_errors(True),
                )
                git_command.return_value = tag + "\n"
                for suffix, language in (
                    ("", "English"),
                    (".ja", "Japanese"),
                ):
                    changelog = root / f"CHANGELOG{suffix}.md"
                    correct = changelog.read_text(encoding="utf-8")
                    changelog.write_text(
                        correct.replace(
                            f"/releases/tag/{tag}",
                            "/releases/tag/v0.1.0-beta.1",
                        ),
                        encoding="utf-8",
                    )
                    self.assertTrue(
                        any(
                            f"{language} changelog needs a {tag} release link"
                            in error
                            for error in release_check.version_consistency_errors(True)
                        )
                    )
                    changelog.write_text(correct, encoding="utf-8")
                (root / "CHANGELOG.ja.md").write_text("", encoding="utf-8")
                errors = release_check.version_consistency_errors(True)
                self.assertTrue(
                    any("Japanese changelog needs a dated" in error for error in errors)
                )
                self.assertTrue(
                    any(
                        "Japanese changelog needs a v0.1.0-beta.2 release link" in error
                        for error in errors
                    )
                )
                (releases / f"{tag}.ja.md").unlink()
                self.assertTrue(
                    any(
                        "missing Japanese release notes" in error
                        for error in release_check.version_consistency_errors(True)
                    )
                )

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
    def test_detects_languages_added_by_patch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory)
            for case_name in ("go-case", "java-case", "python-case"):
                repository = cases / case_name / "repository"
                repository.mkdir(parents=True)
                (repository / "README.md").write_text("baseline\n", encoding="utf-8")
                (cases / case_name / "change.diff").write_text(
                    "sample patch\n", encoding="utf-8"
                )

            def apply_fixture_patch(
                command: list[str], cwd: Path, env: dict[str, str] | None = None
            ) -> None:
                if command[:2] != ["git", "apply"]:
                    return
                if cwd.name == "go-case":
                    (cwd / "go.mod").write_text("module example.org/check\n")
                    (cwd / "check.go").write_text("package check\n")
                elif cwd.name == "java-case":
                    (cwd / "Check.java").write_text("class Check {}\n")
                elif cwd.name == "python-case":
                    (cwd / "check.py").write_text("value = 1\n")

            with patch.object(check_language_fixtures, "CASES", cases), patch.object(
                check_language_fixtures, "run", side_effect=apply_fixture_patch
            ) as run_command, patch.object(
                check_language_fixtures.subprocess, "run"
            ) as gofmt_command, redirect_stdout(StringIO()):
                gofmt_command.return_value.returncode = 0
                gofmt_command.return_value.stdout = ""
                self.assertEqual(check_language_fixtures.check_fixtures(), 0)

            commands = [invocation.args[0] for invocation in run_command.call_args_list]
            self.assertEqual([command[:2] for command in commands].count(["git", "apply"]), 3)
            self.assertIn(["go", "test", "./..."], commands)
            self.assertTrue(any(command[:3] == ["javac", "--release", "17"] for command in commands))
            self.assertTrue(any(command[1:] == ["-m", "compileall", "-q", "."] for command in commands))
            gofmt_command.assert_called_once()

    def test_rejects_added_go_source_without_module(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory)
            repository = cases / "go-case/repository"
            repository.mkdir(parents=True)
            (repository / "README.md").write_text("baseline\n", encoding="utf-8")
            (cases / "go-case/change.diff").write_text("sample patch\n", encoding="utf-8")

            def add_go_source(
                command: list[str], cwd: Path, env: dict[str, str] | None = None
            ) -> None:
                (cwd / "check.go").write_text("package check\n", encoding="utf-8")

            with patch.object(check_language_fixtures, "CASES", cases), patch.object(
                check_language_fixtures, "run", side_effect=add_go_source
            ):
                with self.assertRaisesRegex(RuntimeError, "Go sources require go.mod"):
                    check_language_fixtures.check_fixtures()

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

    def test_optional_findings_require_a_positive_findings_contract(self) -> None:
        case_path = Path("tests/cases/example/case.json")
        valid = {
            "must_report": ["Required defect"],
            "may_report": ["Optional test gap"],
            "output": "findings",
        }
        self.assertEqual(
            run_evaluations.optional_expectation_errors(valid, case_path, "positive"),
            [],
        )
        for invalid in ([], [""], [42], "Optional test gap"):
            with self.subTest(may_report=invalid):
                errors = run_evaluations.optional_expectation_errors(
                    {**valid, "may_report": invalid}, case_path, "positive"
                )
                self.assertEqual(len(errors), 1)
                self.assertIn("invalid optional may_report", errors[0])
        for overrides, expected in (
            ({"output": "no_findings"}, "findings output"),
            ({"must_report": []}, "non-empty must_report"),
        ):
            with self.subTest(overrides=overrides):
                errors = run_evaluations.optional_expectation_errors(
                    {**valid, **overrides}, case_path, "instruction-conflict"
                )
                self.assertEqual(len(errors), 1)
                self.assertIn(expected, errors[0])
        for may_report in ([], ["Optional test gap"]):
            with self.subTest(negative_may_report=may_report):
                errors = run_evaluations.optional_expectation_errors(
                    {**valid, "may_report": may_report}, case_path, "negative"
                )
                self.assertEqual(len(errors), 1)
                self.assertIn("negative case", errors[0])


if __name__ == "__main__":
    unittest.main()
