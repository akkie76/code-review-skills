"""Offline regression tests for human-adjudicated evaluation scoring."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import agent_eval, eval_score


EXPECTED = {"must_report": ["The changed code breaks the documented contract."],
            "must_not_report": ["Invent an unrelated defect."],
            "prefixes": ["MUST(Functionality)"], "output": "findings"}
SKILL = {"version": "v-test", "source_sha256": "a" * 64, "package_sha256": "b" * 64}


class EvaluationScoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.manifest = {
            "schema_version": 1, "source_revision": "c" * 40, "fixture_sha256": "d" * 64,
            "models": {"codex": "codex-model", "claude": "claude-model"},
            "skills": {agent: SKILL for agent in eval_score.AGENTS},
            "policy": {"threshold_percent": 80},
            "runs": [{"phase": "primary", "case_id": f"case-{i}", "language": "en",
                      "expectations": EXPECTED} for i in range(5)] + [
                          {"phase": "repeat", "case_id": "case-0", "language": "en", "expectations": EXPECTED}],
        }
        self.judgments = {"schema_version": 1, "manifest_sha256": eval_score.digest(self.manifest), "runs": []}
        self.save()

    def save(self) -> None:
        eval_score.write_json(self.directory / "manifest.json", self.manifest)
        self.judgments["manifest_sha256"] = eval_score.digest(self.manifest)
        eval_score.write_json(self.directory / "judgments.json", self.judgments)

    def record(self, agent="codex", case_id="case-0", phase="primary") -> dict:
        answer_path = self.directory / f"{agent}-{case_id}-{phase}.txt"
        answer = b"MUST(Functionality): observed contract violation\n"
        answer_path.write_bytes(answer)
        return {
            "agent": agent, "case_id": case_id, "phase": phase, "language": "en",
            "answer_path": str(answer_path), "answer_sha256": hashlib.sha256(answer).hexdigest(),
            "execution": {"status": "completed", "exit_code": 0,
                          "skill_evidence": "file_read_observed" if agent == "codex" else "confirmed"},
            "judgment": {"finalized": True, "reviewer": "LocalReviewer", "method": "human",
                         "output_contract_satisfied": True, "no_findings": False,
                         "forbidden_matches": [], "supporting_claims": [],
                         "notes": "private annotation", "grading_exclusions": [],
                         "findings": [{"id": "f1", "kind": "required", "expected_indices": [0],
                                       "prefix": "MUST(Functionality)", "evidence_note": "Verified at changed lines."}]},
        }

    def complete(self) -> None:
        self.judgments["runs"] = [self.record(agent, plan["case_id"], plan["phase"])
                                  for agent in eval_score.AGENTS for plan in self.manifest["runs"]]

    def test_actual_plan_has_29_primary_and_6_fixed_repeats(self) -> None:
        plan = eval_score.campaign_plan()
        self.assertEqual(sum(run["phase"] == "primary" for run in plan), 29)
        self.assertEqual(sum(run["phase"] == "repeat" for run in plan), 6)
        self.assertEqual(len({(run["phase"], run["case_id"], run["language"]) for run in plan}), 35)

    def test_freeze_requires_clean_inputs_and_writes_pending_records(self) -> None:
        with patch.object(agent_eval, "worktree_dirty", return_value=True):
            with self.assertRaisesRegex(ValueError, "commit evaluation inputs"):
                eval_score.init_campaign(self.directory / "dirty", self.manifest["models"])
        with patch.object(agent_eval, "worktree_dirty", return_value=False), patch.object(
            agent_eval, "run_command", return_value=subprocess.CompletedProcess([], 0, "source-revision\n", "")
        ):
            manifest = eval_score.init_campaign(self.directory / "frozen", self.manifest["models"])
        self.assertEqual(manifest["policy"]["threshold_percent"], 80)
        self.assertEqual(manifest["source_revision"], "source-revision")
        self.assertEqual(eval_score.load_campaign(self.directory / "frozen")[1]["runs"], [])

    def test_score_exactly_80_passes_and_cannot_pool_agents(self) -> None:
        self.complete()
        for agent in eval_score.AGENTS:
            record = next(run for run in self.judgments["runs"] if run["agent"] == agent and run["case_id"] == "case-4")
            record["judgment"]["findings"] = []
        self.save()
        report = eval_score.aggregate(self.directory)
        self.assertTrue(report["accepted"])
        self.assertEqual(report["agents"]["codex"]["primary_score"], 80)
        self.assertEqual(report["agents"]["codex"]["finding_counts"]["required_missed"], 1)
        for record in self.judgments["runs"]:
            if record["agent"] == "claude" and record["case_id"] == "case-3":
                record["judgment"]["findings"] = []
        self.save()
        report = eval_score.aggregate(self.directory)
        self.assertFalse(report["accepted"])
        self.assertTrue(report["agents"]["codex"]["accepted"])
        self.assertEqual(report["agents"]["claude"]["primary_score"], 60)

    def test_missing_or_unreviewed_runs_do_not_improve_score(self) -> None:
        self.complete()
        self.judgments["runs"].pop()
        self.judgments["runs"][0]["judgment"]["finalized"] = False
        self.save()
        report = eval_score.aggregate(self.directory)
        self.assertFalse(report["accepted"])
        self.assertIsNone(report["agents"]["codex"]["primary_score"])
        self.assertEqual(report["agents"]["codex"]["primary_planned"], 5)
        self.assertFalse(report["agents"]["claude"]["complete"])

    def test_repeats_are_separate_and_report_variation(self) -> None:
        self.complete()
        for record in self.judgments["runs"]:
            if record["phase"] == "repeat":
                record["judgment"]["findings"][0]["prefix"] = "SHOULD(Functionality)"
        self.save()
        report = eval_score.aggregate(self.directory)
        self.assertEqual(report["agents"]["codex"]["primary_score"], 100)
        self.assertEqual(report["agents"]["codex"]["repeat_passes"], 0)
        variation = report["agents"]["codex"]["variation"][0]
        self.assertTrue(variation["outcome_changed"])
        self.assertTrue(variation["classification_changed"])
        self.assertEqual(variation["pass_count"], 1)

    def test_additional_optional_and_duplicate_findings_are_not_false_positives(self) -> None:
        expected = copy.deepcopy(EXPECTED)
        expected["may_report"] = ["A substantiated optional simplification."]
        record = self.record()
        record["judgment"]["findings"] += [
            {"id": "extra", "kind": "valid_additional", "prefix": "SHOULD(Test)", "evidence_note": "Missing regression assertion."},
            {"id": "optional", "kind": "optional", "optional_indices": [0], "prefix": "BETTER(Simplicity)", "evidence_note": "Equivalent simpler branch."},
            {"id": "duplicate", "kind": "duplicate", "duplicate_of": "f1", "evidence_note": "Same root cause as f1."},
        ]
        result = eval_score.assess(record, expected)
        self.assertEqual(result["outcome"], "pass")
        self.assertEqual(result["required_detected"], 1)
        self.assertEqual(result["unsupported_findings"], 0)
        self.assertEqual(result["valid_additional"], 1)
        self.assertEqual(result["optional"], 1)
        self.assertEqual(result["duplicates"], 1)

    def test_unsupported_supporting_claim_fails_without_becoming_formal_false_positive(self) -> None:
        record = self.record()
        record["judgment"]["supporting_claims"] = [{"kind": "unsupported", "evidence_note": "No claimed caller exists."}]
        result = eval_score.assess(record, EXPECTED)
        self.assertEqual(result["outcome"], "fail")
        self.assertEqual(result["unsupported_supporting_claims"], 1)
        self.assertEqual(result["unsupported_findings"], 0)
        record["judgment"]["supporting_claims"][0]["kind"] = "ambiguous"
        self.assertEqual(eval_score.assess(record, EXPECTED)["outcome"], "pending")

    def test_agent_assisted_proposals_are_not_human_finalization(self) -> None:
        record = self.record()
        record["judgment"]["method"] = "agent_assisted"
        self.assertEqual(eval_score.assess(record, EXPECTED)["outcome"], "pending")

    def test_no_skill_evidence_or_empty_answer_cannot_pass(self) -> None:
        record = self.record()
        record["execution"]["skill_evidence"] = "not_observed"
        self.assertEqual(eval_score.assess(record, EXPECTED)["outcome"], "fail")
        Path(record["answer_path"]).write_bytes(b" ")
        record["answer_sha256"] = hashlib.sha256(b" ").hexdigest()
        self.assertEqual(eval_score.assess(record, EXPECTED)["outcome"], "incomplete")

    def test_negative_case_requires_semantic_no_findings_not_regex_phrase(self) -> None:
        expected = {"must_report": [], "must_not_report": ["An invented defect"], "prefixes": [], "output": "no_findings"}
        record = self.record()
        record["judgment"]["findings"] = []
        record["judgment"]["no_findings"] = True
        self.assertEqual(eval_score.assess(record, expected)["outcome"], "pass")
        record["judgment"]["forbidden_matches"] = [0]
        self.assertEqual(eval_score.assess(record, expected)["outcome"], "fail")

    def test_manifest_and_answer_changes_are_rejected(self) -> None:
        manifest_path = self.directory / "manifest.json"
        changed = copy.deepcopy(self.manifest)
        changed["policy"]["threshold_percent"] = 60
        eval_score.write_json(manifest_path, changed)
        with self.assertRaisesRegex(ValueError, "manifest was changed"):
            eval_score.load_campaign(self.directory)
        record = self.record()
        Path(record["answer_path"]).write_text("Changed output", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "answer changed"):
            eval_score.assess(record, EXPECTED)

    def summary(self) -> tuple[Path, dict]:
        raw_directory = self.directory / "raw"
        raw_directory.mkdir()
        run_dir = raw_directory / "case-0-en-1"
        run_dir.mkdir()
        (run_dir / "answer.txt").write_text("MUST(Functionality): A proven defect.", encoding="utf-8")
        summary = {
            "schema_version": 2, "agent": "codex", "agent_version": "codex-test",
            "evaluation_inputs_dirty": False, "skill_revision": self.manifest["source_revision"],
            "fixture_sha256": self.manifest["fixture_sha256"], "requested_model": "codex-model",
            "skill": SKILL, "invocation_mode": "implicit",
            "settings": {"sandbox": "read-only", "ephemeral": True, "ignore_user_config": True, "approval_policy": "never"},
            "results": [{"case_id": "case-0", "language": "en", "run_number": 1,
                         "requested_model": "codex-model", "observed_model": None, "skill": SKILL,
                         "status": "completed", "exit_code": 0, "skill_evidence": "file_read_observed",
                         "raw_directory": run_dir.name}],
        }
        return raw_directory / "summary.json", summary

    def test_import_keeps_judgments_pending_and_rejects_duplicate_runs(self) -> None:
        path, summary = self.summary()
        eval_score.write_json(path, summary)
        eval_score.import_summary(self.directory, path, "primary")
        _, judgments = eval_score.load_campaign(self.directory)
        self.assertFalse(judgments["runs"][0]["judgment"]["finalized"])
        self.assertEqual(eval_score.aggregate(self.directory)["results"][0]["outcome"], "pending")
        with self.assertRaisesRegex(ValueError, "duplicate run"):
            eval_score.import_summary(self.directory, path, "primary")

    def test_import_rejects_mixed_revision_dirty_inputs_model_and_permissions(self) -> None:
        path, original = self.summary()
        for field, value in (("skill_revision", "wrong"), ("evaluation_inputs_dirty", True),
                             ("requested_model", "different"), ("settings", {"sandbox": "danger-full-access"})):
            summary = copy.deepcopy(original)
            summary[field] = value
            eval_score.write_json(path, summary)
            with self.subTest(field=field), self.assertRaises(ValueError):
                eval_score.import_summary(self.directory, path, "primary")
            self.assertEqual(eval_score.load_campaign(self.directory)[1]["runs"], [])

    def test_aggregate_has_no_annotation_prose_paths_or_reviewer_names(self) -> None:
        self.complete()
        self.save()
        rendered = json.dumps(eval_score.aggregate(self.directory))
        for sensitive in (str(self.directory), "private annotation", "LocalReviewer", "Verified at changed lines."):
            self.assertNotIn(sensitive, rendered)

    def test_invalid_expectation_indices_and_duplicate_targets_are_rejected(self) -> None:
        record = self.record()
        record["judgment"]["findings"][0]["expected_indices"] = [1]
        with self.assertRaisesRegex(ValueError, "in range"):
            eval_score.assess(record, EXPECTED)
        record = self.record()
        record["judgment"]["findings"].append({"id": "duplicate", "kind": "duplicate", "duplicate_of": "missing", "evidence_note": "Duplicate."})
        with self.assertRaisesRegex(ValueError, "non-duplicate"):
            eval_score.assess(record, EXPECTED)


class ClaudeEvaluationTests(unittest.TestCase):
    def test_claude_evaluation_writes_runner_summary_fields_without_real_agent(self) -> None:
        original = agent_eval.run_command
        events = "\n".join(json.dumps(event) for event in [
            {"type": "system", "subtype": "init", "model": "claude-model"},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "evidence-code-review"}}]}},
            {"type": "result", "subtype": "success", "result": "No actionable findings.", "usage": {"input_tokens": 12}, "total_cost_usd": 0.1},
        ])

        def fake_command(args, cwd, **kwargs):
            if args[0] == "claude":
                self.assertTrue((cwd / ".claude/skills/evidence-code-review/SKILL.md").is_file())
                self.assertFalse((cwd / ".agents").exists())
                return subprocess.CompletedProcess(args, 0, events, "")
            return original(args, cwd, **kwargs)

        with tempfile.TemporaryDirectory() as directory, patch.object(agent_eval, "run_command", side_effect=fake_command):
            case = json.loads((agent_eval.CASES / "negative-refactor/case.json").read_text())
            result = agent_eval.evaluate_one(agent_eval.CASES / case["id"], case, "Review the working tree changes.",
                                             "en", 1, Path(directory), "claude-model", 30, "claude")
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["skill_evidence"], "confirmed")
            self.assertEqual(result["observed_model"], "claude-model")
            self.assertEqual(result["cost_usd"], 0.1)
            self.assertTrue((Path(directory) / "negative-refactor-en-1/answer.txt").is_file())

    def test_installed_skill_is_not_an_invocation_and_result_must_succeed(self) -> None:
        events = [{"type": "system", "subtype": "init", "model": "claude-model", "skills": ["evidence-code-review"]},
                  {"type": "result", "subtype": "error_max_turns", "result": "Partial answer", "is_error": True}]
        observed = agent_eval.claude_result("\n".join(json.dumps(event) for event in events))
        self.assertFalse(observed["invoked"])
        self.assertFalse(observed["completed"])
        self.assertEqual(observed["model"], "claude-model")

    def test_stream_captures_skill_call_answer_usage_and_cost(self) -> None:
        events = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": "evidence-code-review"}}]}},
                  {"type": "result", "subtype": "success", "result": "No findings.", "usage": {"input_tokens": 12}, "total_cost_usd": 0.1}]
        observed = agent_eval.claude_result("\n".join(json.dumps(event) for event in events))
        self.assertTrue(observed["invoked"])
        self.assertTrue(observed["completed"])
        self.assertEqual(observed["answer"], "No findings.")
        self.assertEqual(observed["usage"], {"input_tokens": 12})
        self.assertEqual(observed["cost"], 0.1)

    def test_claude_command_uses_static_permissions_without_bypass(self) -> None:
        command = agent_eval.agent_command("claude", Path("repo"), Path("answer.txt"), "Review the diff.", "claude-model")
        self.assertIn("dontAsk", command)
        self.assertIn("Read,Grep,Glob,Skill,Bash", command)
        self.assertIn("Bash(git diff:*)", command)
        self.assertNotIn("--dangerously-skip-permissions", command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)
        self.assertEqual(command[-1], "Review the diff.")


if __name__ == "__main__":
    unittest.main()
