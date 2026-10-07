#!/usr/bin/env python3
"""Freeze a local evaluation campaign and aggregate explicitly reviewed judgments.

No model calls or automatic semantic grading. Raw answers and annotations stay
outside the repository; the aggregate omits reviewer names, paths and prose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from tests import agent_eval


AGENTS = ("codex", "claude")
PREFIX_TOKEN = re.compile(r"(?:MUST|SHOULD|BETTER|NITS)\((?:Design|Simplicity|Naming|Style|Functionality|Test|Document)\)")


def plan_path() -> Path:
    return agent_eval.ROOT / "tests/EVALUATION_PLAN.json"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path.name}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def outside(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    root = agent_eval.ROOT.resolve()
    if resolved == root or root in resolved.parents:
        raise ValueError("campaign and raw results must be outside this repository")
    return resolved


def campaign_plan() -> list[dict]:
    policy = read_json(plan_path())
    if policy["threshold_percent"] != 80 or policy["repeat_runs"] != 1:
        raise ValueError("unsupported evaluation policy")
    if policy["primary"] != "all_cases_auto_language_plus_negative_refactor_ja":
        raise ValueError("unsupported primary selection")
    primary = agent_eval.selected_cases(None, True, "auto")
    primary += agent_eval.selected_cases(["negative-refactor"], False, "ja")
    repeated = agent_eval.selected_cases(policy["repeat_cases"], False, "auto")
    return [
        {"phase": phase, "case_id": case["id"], "language": language,
         "expectations": case["expectations"]}
        for phase, cases in (("primary", primary), ("repeat", repeated))
        for _, case, _, language in cases
    ]


def init_campaign(destination: Path, models: dict[str, str], timeout: int = 300) -> dict:
    if set(models) != set(AGENTS) or any(not isinstance(value, str) or not value.strip() for value in models.values()):
        raise ValueError("explicit nonempty model IDs are required for both agents")
    if type(timeout) is not int or timeout < 1:
        raise ValueError("timeout must be a positive integer")
    if agent_eval.worktree_dirty(agent_eval.INPUT_PATHS) is not False:
        raise ValueError("commit evaluation inputs before freezing the campaign")
    revision = agent_eval.run_command(["git", "rev-parse", "HEAD"], agent_eval.ROOT)
    if revision.returncode:
        raise ValueError("cannot identify evaluation revision")
    manifest = {
        "schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
        "policy": read_json(plan_path()), "source_revision": revision.stdout.strip(),
        "fixture_sha256": agent_eval.fixture_hash(), "models": models,
        "skills": {agent: agent_eval.package_metadata(agent_eval.skill_path(agent)) for agent in AGENTS},
        "settings": {agent: agent_eval.run_settings(agent, timeout) for agent in AGENTS},
        "input_source": "revision_snapshot" if agent_eval.SNAPSHOT_ACTIVE else "live_checkout",
        "runs": campaign_plan(),
    }
    if len({skill["source_sha256"] for skill in manifest["skills"].values()}) != 1:
        raise ValueError("agent packages do not share the same source")
    directory = agent_eval.output_directory(destination)
    write_json(directory / "manifest.json", manifest)
    write_json(directory / "judgments.json", {
        "schema_version": 1, "manifest_sha256": digest(manifest), "runs": [],
    })
    return manifest


def load_campaign(directory: Path) -> tuple[dict, dict]:
    directory = outside(directory)
    manifest = read_json(directory / "manifest.json")
    judgments = read_json(directory / "judgments.json")
    if manifest.get("schema_version") != 1 or judgments.get("schema_version") != 1:
        raise ValueError("unsupported campaign schema")
    if judgments.get("manifest_sha256") != digest(manifest):
        raise ValueError("frozen manifest was changed; start a new campaign")
    return manifest, judgments


def key(record: dict) -> tuple:
    return record["agent"], record["phase"], record["case_id"], record["language"]


def import_summary(directory: Path, summary_file: Path, phase: str) -> None:
    manifest, judgments = load_campaign(directory)
    summary_file = outside(summary_file)
    summary = read_json(summary_file)
    agent = summary.get("agent")
    if agent not in AGENTS or summary.get("schema_version") != 2:
        raise ValueError("a schema-2 runner summary for codex or claude is required")
    if summary.get("evaluation_inputs_dirty") is not False:
        raise ValueError("summary has dirty or unknown evaluation inputs")
    if summary.get("input_integrity") != "verified":
        raise ValueError("summary lacks verified per-run input integrity; retain legacy records separately")
    checks = {
        "skill_revision": manifest["source_revision"],
        "fixture_sha256": manifest["fixture_sha256"],
        "requested_model": manifest["models"][agent],
        "skill": manifest["skills"][agent], "invocation_mode": "implicit",
        "input_source": manifest.get("input_source"),
    }
    for field, expected in checks.items():
        if summary.get(field) != expected:
            raise ValueError(f"summary does not match campaign: {field}")
    if not summary.get("agent_version") or summary["agent_version"] == "unavailable":
        raise ValueError("CLI version is required")
    settings = summary.get("settings", {})
    frozen_settings = manifest.get("settings", {}).get(agent)
    if frozen_settings is None or digest(settings) != digest(frozen_settings):
        raise ValueError("permissions or execution settings differ from frozen campaign")
    existing = {key(record): record for record in judgments["runs"]}
    if len(existing) != len(judgments["runs"]):
        raise ValueError("duplicate judgments")
    for record in existing.values():
        if record["agent"] == agent and record["execution"]["agent_version"] != summary["agent_version"]:
            raise ValueError("CLI version changed within the campaign")
    planned = {(run["case_id"], run["language"]): run for run in manifest["runs"] if run["phase"] == phase}
    additions = []
    for result in summary["results"]:
        plan = planned.get((result["case_id"], result["language"]))
        if plan is None or result["run_number"] != 1:
            raise ValueError("unplanned case/language/run; import one pass per phase")
        if result.get("skill") != manifest["skills"][agent] or result.get("requested_model") != manifest["models"][agent]:
            raise ValueError("per-run package or model differs from campaign")
        observed = result.get("observed_model")
        if observed and observed != manifest["models"][agent]:
            raise ValueError("CLI-reported model differs from requested model")
        raw = Path(result["raw_directory"])
        if raw.name != str(raw) or raw.name in (".", ".."):
            raise ValueError("unsafe raw-directory name")
        answer_path = (summary_file.parent / raw / "answer.txt").resolve()
        if summary_file.parent not in answer_path.parents:
            raise ValueError("answer path escapes summary directory")
        answer = answer_path.read_bytes()
        record = {
            "agent": agent, "phase": phase, "case_id": result["case_id"], "language": result["language"],
            "answer_path": str(answer_path), "answer_sha256": hashlib.sha256(answer).hexdigest(),
            "execution": {"status": result["status"], "exit_code": result.get("exit_code"),
                          "skill_evidence": result["skill_evidence"], "observed_model": observed,
                          "agent_version": summary["agent_version"], "settings": settings,
                          "usage": result.get("usage"), "cost_usd": result.get("cost_usd")},
            "judgment": {"finalized": False, "reviewer": "", "method": "human",
                         "output_contract_satisfied": None, "no_findings": None,
                         "forbidden_matches": [], "findings": [], "supporting_claims": [],
                         "grading_exclusions": [], "notes": ""},
        }
        identity = key(record)
        if identity in existing:
            raise ValueError("duplicate run; do not overwrite or select the best answer")
        existing[identity] = record
        additions.append(record)
    judgments["runs"].extend(additions)
    write_json(outside(directory) / "judgments.json", judgments)


def indices(value: object, count: int) -> set[int]:
    if not isinstance(value, list) or any(type(item) is not int or not 0 <= item < count for item in value):
        raise ValueError("expectation indices must be zero-based integers in range")
    if len(value) != len(set(value)):
        raise ValueError("duplicate expectation index")
    return set(value)


def assess(record: dict, expected: dict) -> dict:
    judgment = record["judgment"]
    answer_path = outside(Path(record["answer_path"]))
    answer = answer_path.read_bytes()
    if hashlib.sha256(answer).hexdigest() != record["answer_sha256"]:
        raise ValueError("answer changed after import; invalidate its judgment")
    execution = record["execution"]
    if execution["status"] != "completed" or execution.get("exit_code") != 0 or not answer.strip():
        return {"outcome": "incomplete", "reason": "execution_failed_or_empty"}
    if type(judgment["finalized"]) is not bool or not isinstance(judgment["reviewer"], str):
        raise ValueError("finalized must be boolean and reviewer must be a string")
    if not judgment["finalized"] or not judgment["reviewer"].strip() or judgment["method"] != "human":
        return {"outcome": "pending", "reason": "human_adjudication_required"}
    if type(judgment["output_contract_satisfied"]) is not bool or type(judgment["no_findings"]) is not bool:
        raise ValueError("final judgment needs boolean output_contract_satisfied and no_findings")
    forbidden = indices(judgment["forbidden_matches"], len(expected["must_not_report"]))
    findings = judgment["findings"]
    ids = [finding["id"] for finding in findings]
    if len(ids) != len(set(ids)) or any(not isinstance(identifier, str) or not identifier for identifier in ids):
        raise ValueError("finding IDs must be distinct nonempty strings")
    matched: set[int] = set()
    prefixes: set[str] = set()
    required_prefixes: set[str] = set()
    prefix_mismatches = 0
    counts: Counter = Counter()
    for finding in findings:
        prefix = finding.get("prefix")
        if prefix is not None and (not isinstance(prefix, str) or not PREFIX_TOKEN.fullmatch(prefix)):
            raise ValueError("prefix must be an exact action/viewpoint token or null")
        kind = finding["kind"]
        if kind not in {"required", "optional", "valid_additional", "duplicate", "unsupported", "ambiguous"}:
            raise ValueError("unknown finding classification")
        if not finding.get("evidence_note", "").strip():
            raise ValueError("every finding requires an evidence/adjudication note")
        required = indices(finding.get("expected_indices", []), len(expected["must_report"]))
        if (kind == "required" and not required) or (kind != "required" and required):
            raise ValueError("only required findings may match required expectation indices")
        if kind == "required":
            if prefix not in expected["prefixes"]:
                prefix_mismatches += 1
            else:
                required_prefixes.add(prefix)
        if kind == "optional":
            if not indices(finding.get("optional_indices", []), len(expected.get("may_report", []))):
                raise ValueError("optional finding must map to may_report")
        if kind == "duplicate":
            target = next((item for item in findings if item["id"] == finding.get("duplicate_of")), None)
            if target is None or target["id"] == finding["id"] or target["kind"] == "duplicate":
                raise ValueError("duplicate must reference a non-duplicate finding in this answer")
        else:
            counts[kind] += 1
            if finding.get("prefix"):
                prefixes.add(finding["prefix"])
        matched.update(required)
    for claim in judgment["supporting_claims"]:
        if claim["kind"] not in {"valid", "unsupported", "ambiguous"} or not claim.get("evidence_note", "").strip():
            raise ValueError("supporting claims need a classification and evidence note")
    if counts["ambiguous"] or any(claim["kind"] == "ambiguous" for claim in judgment["supporting_claims"]):
        return {"outcome": "pending", "reason": "ambiguous_claim_needs_resolution"}
    unsupported_claims = sum(claim["kind"] == "unsupported" for claim in judgment["supporting_claims"])
    evidence = execution["skill_evidence"]
    accessed = evidence == ("file_read_observed" if record["agent"] == "codex" else "confirmed")
    no_findings = judgment["no_findings"]
    if no_findings and findings:
        raise ValueError("no_findings contradicts adjudicated findings")
    passed = (
        accessed and judgment["output_contract_satisfied"] and not forbidden
        and not counts["unsupported"] and not unsupported_claims
        and len(matched) == len(expected["must_report"])
        and not prefix_mismatches and set(expected["prefixes"]).issubset(required_prefixes)
        and (no_findings if expected["output"] == "no_findings" else bool(findings) and not no_findings)
    )
    return {
        "outcome": "pass" if passed else "fail", "required_detected": len(matched),
        "required_missed": len(expected["must_report"]) - len(matched),
        "unsupported_findings": counts["unsupported"], "unsupported_supporting_claims": unsupported_claims,
        "valid_additional": counts["valid_additional"], "optional": counts["optional"],
        "duplicates": sum(finding["kind"] == "duplicate" for finding in findings),
        "required_prefix_mismatches": prefix_mismatches,
        "forbidden_matches": len(forbidden), "prefixes": sorted(prefixes),
        "skill_evidence": evidence,
    }


def aggregate(directory: Path) -> dict:
    manifest, judgments = load_campaign(directory)
    records = {key(record): record for record in judgments["runs"]}
    if len(records) != len(judgments["runs"]):
        raise ValueError("duplicate judgments")
    planned = {(agent, run["phase"], run["case_id"], run["language"]): run
               for agent in AGENTS for run in manifest["runs"]}
    if set(records) - set(planned):
        raise ValueError("unplanned adjudication")
    evaluations = []
    for identity, plan in planned.items():
        assessment = assess(records[identity], plan["expectations"]) if identity in records else {
            "outcome": "incomplete", "reason": "not_run",
        }
        evaluations.append({"agent": identity[0], "phase": identity[1],
                            "case_id": identity[2], "language": identity[3], **assessment})
    agents = {}
    count_fields = ("required_detected", "required_missed", "unsupported_findings",
                    "unsupported_supporting_claims", "valid_additional", "optional", "duplicates", "forbidden_matches",
                    "required_prefix_mismatches")
    for agent in AGENTS:
        primary = [run for run in evaluations if run["agent"] == agent and run["phase"] == "primary"]
        repeat = [run for run in evaluations if run["agent"] == agent and run["phase"] == "repeat"]
        completed = all(run["outcome"] in {"pass", "fail"} for run in primary + repeat)
        passes = sum(run["outcome"] == "pass" for run in primary)
        primary_complete = all(run["outcome"] in {"pass", "fail"} for run in primary)
        score = 100 * passes / len(primary) if primary_complete else None
        variations = []
        for rerun in repeat:
            baseline = next(run for run in primary if run["case_id"] == rerun["case_id"] and run["language"] == rerun["language"])
            judged = baseline["outcome"] in {"pass", "fail"} and rerun["outcome"] in {"pass", "fail"}
            variations.append({"case_id": rerun["case_id"], "language": rerun["language"],
                               "pass_count": sum(run["outcome"] == "pass" for run in (baseline, rerun)) if judged else None,
                               "runs": 2, "outcome_changed": baseline["outcome"] != rerun["outcome"] if judged else None,
                               "classification_changed": any(baseline.get(field) != rerun.get(field) for field in count_fields + ("prefixes",)) if judged else None})
        agents[agent] = {
            "primary_planned": len(primary), "primary_passes": passes,
            "primary_score": score, "repeat_planned": len(repeat),
            "repeat_passes": sum(run["outcome"] == "pass" for run in repeat),
            "complete": completed,
            "accepted": completed and passes * 100 >= len(primary) * manifest["policy"]["threshold_percent"],
            "finding_counts": {field: sum(run.get(field, 0) for run in primary) for field in count_fields},
            "variation": variations,
        }
    return {
        "schema_version": 1, "source_revision": manifest["source_revision"],
        "manifest_sha256": digest(manifest), "fixture_sha256": manifest["fixture_sha256"],
        "models": manifest["models"], "skills": manifest["skills"],
        "threshold_percent": manifest["policy"]["threshold_percent"], "agents": agents,
        "accepted": all(agent["accepted"] for agent in agents.values()),
        "results": evaluations,
        "notes": "Strict case score, not general accuracy or finding-level precision. "
                 "Counts cover finalized primary judgments only. Repeats are diagnostic, not pooled. "
                 "Codex file reads are weaker evidence than Claude Skill calls. "
                 "A passing score does not replace release-risk adjudication or final release approval.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Freeze inputs and the 80-point rule before evaluation")
    init.add_argument("--campaign", type=Path, required=True)
    init.add_argument("--codex-model", required=True)
    init.add_argument("--claude-model", required=True)
    init.add_argument("--timeout", type=int, default=300, help="Freeze this per-run timeout for both agents")
    init.add_argument("--revision", help="Freeze inputs from a private snapshot of this commit/ref")
    ingest = commands.add_parser("import", help="Import traces and initialize unreviewed annotations")
    ingest.add_argument("--campaign", type=Path, required=True)
    ingest.add_argument("--summary", type=Path, required=True)
    ingest.add_argument("--phase", choices=("primary", "repeat"), default="primary")
    score = commands.add_parser("score", help="Aggregate judgments without calling models")
    score.add_argument("--campaign", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            models = {"codex": args.codex_model, "claude": args.claude_model}
            if args.revision:
                with agent_eval.revision_snapshot(args.revision):
                    manifest = init_campaign(args.campaign, models, args.timeout)
            else:
                manifest = init_campaign(args.campaign, models, args.timeout)
            print(f"Frozen {len(manifest['runs'])} runs per agent; threshold 80 points.")
        elif args.command == "import":
            import_summary(args.campaign, args.summary, args.phase)
            print("Imported. Review judgments.json; no semantic judgments were made.")
        else:
            report = aggregate(args.campaign)
            write_json(outside(args.campaign) / "aggregate.json", report)
            for agent, result in report["agents"].items():
                print(f"{agent}: {result['primary_passes']}/{result['primary_planned']}, "
                      f"score={result['primary_score']}, complete={result['complete']}")
            return 0 if report["accepted"] else 1
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
