#!/usr/bin/env python3
"""Opt-in, local Codex evaluation of behavioral fixtures.

This runner never publishes transcripts or judges semantic correctness. Its
summary records observable facts for subsequent human adjudication.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests/cases"
SKILL = ROOT / "dist/codex/evidence-code-review"
PREFIX = re.compile(
    r"(?m)^\s*(?:[-*]\s*)?(?:\*\*)?"
    r"(MUST|SHOULD|BETTER|NITS)"
    r"\((Design|Simplicity|Naming|Style|Functionality|Test|Document)\)\s*:"
)
NO_FINDINGS = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:no (?:actionable )?findings|"
    r"no issues found|指摘(?:事項)?(?:は)?(?:ありません|なし))\s*[。.]*\s*$"
)


def run_command(args: list[str], cwd: Path, *, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout
    )


def selected_cases(names: list[str] | None, all_cases: bool, language: str) -> list[tuple[Path, dict, str, str]]:
    if names and len(names) != len(set(names)):
        raise ValueError("each --case may be selected only once")
    paths = sorted(CASES.glob("*/case.json")) if all_cases else [CASES / name / "case.json" for name in names or []]
    selected = []
    for path in paths:
        if not path.is_file():
            raise ValueError(f"unknown case: {path.parent.name}")
        case = json.loads(path.read_text(encoding="utf-8"))
        case_language = (
            "en" if any(request["language"] == "en" for request in case["requests"])
            else "ja"
        ) if language == "auto" else language
        requests = [request["prompt"] for request in case["requests"] if request["language"] == case_language]
        if not requests:
            raise ValueError(f"case {case['id']} has no {case_language} request")
        if len(requests) != 1:
            raise ValueError(f"case {case['id']} has more than one {case_language} request")
        selected.append((path.parent, case, requests[0], case_language))
    if not selected:
        raise ValueError("no cases selected")
    return selected


def prepare_repository(case_dir: Path, destination: Path) -> None:
    shutil.copytree(case_dir / "repository", destination)
    skill_target = destination / ".agents/skills/evidence-code-review"
    shutil.copytree(SKILL, skill_target)
    commands = [
        ["git", "init", "-q"],
        ["git", "add", "-A"],
        ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=Fixture",
         "-c", "user.email=fixture@example.invalid", "commit", "-qm", "baseline"],
        ["git", "apply", str(case_dir / "change.diff")],
    ]
    for command in commands:
        result = run_command(command, destination)
        if result.returncode:
            raise RuntimeError(f"fixture setup failed ({command[0]} {command[1]}): {result.stderr.strip()}")
    untracked = run_command(["git", "ls-files", "--others", "--exclude-standard", "-z"], destination)
    if untracked.returncode:
        raise RuntimeError(f"cannot list new fixture files: {untracked.stderr.strip()}")
    new_files = [name for name in untracked.stdout.split("\0") if name]
    if new_files:
        result = run_command(["git", "add", "-N", "--", *new_files], destination)
        if result.returncode:
            raise RuntimeError(f"cannot expose new fixture files in diff: {result.stderr.strip()}")
    diff = run_command(["git", "diff", "--name-only"], destination)
    if diff.returncode or not diff.stdout.strip():
        raise RuntimeError("fixture has no visible working-tree diff")


def event_usage(jsonl: str) -> dict | None:
    usage = None
    for line in jsonl.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    return usage


def skill_file_read_observed(jsonl: str) -> bool:
    for line in jsonl.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if (
            event.get("type") == "item.completed"
            and item.get("type") == "command_execution"
            and item.get("exit_code") == 0
            and ".agents/skills/evidence-code-review/SKILL.md" in str(item.get("command", ""))
            and "name: evidence-code-review" in str(item.get("aggregated_output", ""))
        ):
            return True
    return False


def observed_output(answer: str, expected: dict) -> dict:
    prefixes = [f"{action}({viewpoint})" for action, viewpoint in PREFIX.findall(answer)]
    expected_prefixes = expected["prefixes"]
    explicit_no_findings = bool(NO_FINDINGS.search(answer))
    return {
        "prefixes": prefixes,
        "required_prefixes_present": all(prefix in prefixes for prefix in expected_prefixes),
        "explicit_no_findings": explicit_no_findings,
        "negative_output_check": (
            not prefixes and explicit_no_findings
            if expected["output"] == "no_findings" else None
        ),
        "semantic_judgment": "pending_human_review",
    }


def evaluate_one(
    case_dir: Path, case: dict, prompt: str, language: str, run_number: int,
    output_dir: Path, model: str | None, timeout: int,
) -> dict:
    run_dir = output_dir / f"{case['id']}-{language}-{run_number}"
    run_dir.mkdir(mode=0o700)
    with tempfile.TemporaryDirectory(prefix="fixture-") as temporary:
        repo = Path(temporary) / "repository"
        prepare_repository(case_dir, repo)
        answer_file = run_dir / "answer.txt"
        command = [
            "codex", "exec", "--cd", str(repo), "--ephemeral", "--ignore-user-config",
            "--sandbox", "read-only", "--json", "--output-last-message", str(answer_file),
            "--config", 'approval_policy="never"',
        ]
        if model:
            command.extend(["--model", model])
        command.append(prompt)
        try:
            result = run_command(command, repo, timeout=timeout)
            exit_code = result.returncode
            events, stderr = result.stdout, result.stderr
        except subprocess.TimeoutExpired as error:
            exit_code = None
            events = error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else error.stdout or ""
            stderr = error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else error.stderr or ""
            stderr += f"\nEvaluation timed out after {timeout} seconds."
        (run_dir / "events.jsonl").write_text(events, encoding="utf-8")
        (run_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
        answer = answer_file.read_text(encoding="utf-8") if answer_file.exists() else ""
        if not answer_file.exists():
            answer_file.write_text("", encoding="utf-8")
        return {
            "case_id": case["id"],
            "language": language,
            "run_number": run_number,
            "exit_code": exit_code,
            "status": "completed" if exit_code == 0 and answer else (
                "no_answer" if exit_code == 0 else "agent_error"
            ),
            "usage": event_usage(events),
            "skill_file_read_observed": skill_file_read_observed(events),
            "skill_invocation": "not_verified",
            "observed": observed_output(answer, case["expectations"]),
            "raw_directory": run_dir.name,
        }


def output_directory(requested: Path | None) -> Path:
    if requested is None:
        return Path(tempfile.mkdtemp(prefix="evidence-review-eval-"))
    resolved = requested.expanduser().resolve()
    repository = ROOT.resolve()
    if resolved == repository or repository in resolved.parents:
        raise ValueError("evaluation output must be outside this repository")
    resolved.mkdir(parents=True, exist_ok=False, mode=0o700)
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--case", action="append", help="Fixture ID; repeatable")
    selection.add_argument("--all", action="store_true", help="Run every fixture")
    parser.add_argument("--language", choices=("auto", "en", "ja"), default="auto")
    parser.add_argument("--runs", type=int, default=1, help="Fresh runs per selected case")
    parser.add_argument("--model", help="Explicit Codex model; otherwise use the CLI default")
    parser.add_argument("--timeout", type=int, default=600, help="Seconds per run")
    parser.add_argument("--output-dir", type=Path, help="New local directory outside the repository")
    parser.add_argument("--execute", action="store_true", help="Confirm that model calls may consume tokens")
    args = parser.parse_args(argv)
    if args.runs < 1 or args.timeout < 1:
        parser.error("--runs and --timeout must be positive")
    try:
        cases = selected_cases(args.case, args.all, args.language)
    except (OSError, KeyError, ValueError) as error:
        parser.error(str(error))
    if not args.execute:
        print(f"Planned {len(cases) * args.runs} Codex run(s) across {len(cases)} case(s).")
        print("No model calls made. Add --execute to run the evaluation.")
        return 0
    if not SKILL.is_dir():
        parser.error("generated Codex Skill is missing; run make build")
    if shutil.which("codex") is None:
        parser.error("Codex CLI is not installed")
    try:
        destination = output_directory(args.output_dir)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    version = run_command(["codex", "--version"], ROOT)
    revision = run_command(["git", "rev-parse", "HEAD"], ROOT)
    report = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "agent": "codex",
        "agent_version": version.stdout.strip() if version.returncode == 0 else "unavailable",
        "model": args.model or "unavailable (CLI default)",
        "cost": "unavailable",
        "skill_revision": revision.stdout.strip() if revision.returncode == 0 else "unavailable",
        "settings": {"sandbox": "read-only", "ephemeral": True, "ignore_user_config": True,
                     "approval_policy": "never", "timeout_seconds": args.timeout},
        "selected_cases": [case["id"] for _, case, _, _ in cases],
        "requested_runs_per_case": args.runs,
        "results": [],
        "notes": "Prefix and no-finding checks are provisional. Semantic findings, "
                 "unexpected output, and Skill invocation require human adjudication.",
    }
    try:
        for case_dir, case, prompt, case_language in cases:
            for run_number in range(1, args.runs + 1):
                print(f"Evaluating {case['id']} ({case_language}, run {run_number}/{args.runs})", flush=True)
                report["results"].append(evaluate_one(
                    case_dir, case, prompt, case_language, run_number,
                    destination, args.model, args.timeout,
                ))
                (destination / "summary.json").write_text(
                    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
    except (OSError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        print(f"Local evaluation files: {destination}", file=sys.stderr)
        return 1
    print(f"Local evaluation files: {destination}")
    return 0 if all(item["exit_code"] == 0 for item in report["results"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
