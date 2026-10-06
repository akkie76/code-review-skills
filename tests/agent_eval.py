#!/usr/bin/env python3
"""Opt-in, local Codex evaluation of behavioral fixtures.

This runner never publishes transcripts or judges semantic correctness. Its
summary records observable facts for subsequent human adjudication.
"""

from __future__ import annotations

import argparse
import hashlib
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
    r"(?m)^[ \t]*(?:(?:#{1,6}|[-*+]|\d+[.)])[ \t]+|>[ \t]*)*"
    r"(?:\*\*|__|`)?"
    r"(MUST|SHOULD|BETTER|NITS)"
    r"\((Design|Simplicity|Naming|Style|Functionality|Test|Document)\)"
    r"(?:\*\*|__|`)?[ \t]*:"
)
NO_FINDINGS = re.compile(
    r"(?i)\b(?:no (?:actionable )?(?:findings|issues|defects)(?: found)?|"
    r"nothing that needs to change)\b|"
    r"(?:修正が必要な)?指摘(?:事項)?(?:は)?(?:ありません|なし)|"
    r"(?:修正が必要な)?不具合(?:は|が)?(?:見つかりませんでした|ありません)"
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
        ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=Developer",
         "-c", "user.email=dev@example.invalid", "commit", "-qm", "baseline"],
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


def reported_model(jsonl: str, stderr: str) -> dict:
    """Use CLI metadata only, never model names mentioned in review prose."""
    for line in jsonl.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") not in {
            "thread.started", "session.started", "turn.started"
        }:
            continue
        value = event.get("model")
        if isinstance(value, str) and value.strip():
            return {"model": value.strip(), "source": "event"}
    match = re.search(r"(?m)^[ \t]*model:[ \t]*(\S+)[ \t]*$", stderr)
    return {"model": match.group(1), "source": "stderr"} if match else {
        "model": None, "source": "unavailable"
    }


def package_metadata(package: Path) -> dict:
    text = (package / "SKILL.md").read_text(encoding="utf-8")
    version = re.search(r"<!-- skill-version:\s*(\S+)\s*-->", text)
    source = re.search(r"<!-- source-sha256:\s*([0-9a-f]{64})\s*-->", text)
    digest = hashlib.sha256()
    for path in sorted(path for path in package.rglob("*") if path.is_file()):
        digest.update(path.relative_to(package).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return {
        "version": version.group(1) if version else None,
        "source_sha256": source.group(1) if source else None,
        "package_sha256": digest.hexdigest(),
    }


def worktree_dirty(paths: list[str] | None = None) -> bool | None:
    command = ["git", "status", "--porcelain", "--untracked-files=all"]
    if paths:
        command.extend(["--", *paths])
    result = run_command(command, ROOT)
    return bool(result.stdout.strip()) if result.returncode == 0 else None


def skill_file_read_observed(jsonl: str, skill_text: str | None = None) -> bool:
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
            and ".agents/skills/evidence-code-review/SKILL.md" in str(item.get("command", ""))
            and "name: evidence-code-review" in str(item.get("aggregated_output", ""))
        ):
            output = str(item.get("aggregated_output", ""))
            # A later command can fail after cat successfully printed the Skill.
            if item.get("exit_code") == 0 or (
                skill_text and skill_text.strip() in output
            ):
                return True
    return False


def observed_output(answer: str, expected: dict) -> dict:
    prefixes = [f"{action}({viewpoint})" for action, viewpoint in PREFIX.findall(answer)]
    expected_prefixes = expected["prefixes"]
    explicit_no_findings = bool(NO_FINDINGS.search(answer))
    return {
        "answer_present": bool(answer.strip()),
        "prefixes": prefixes,
        "required_prefixes_present": all(prefix in prefixes for prefix in expected_prefixes),
        "explicit_no_findings": explicit_no_findings,
        "negative_output_check": (
            bool(answer.strip()) and not prefixes
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
    with tempfile.TemporaryDirectory(prefix="repo-") as temporary:
        repo = Path(temporary) / "repository"
        prepare_repository(case_dir, repo)
        installed_skill = repo / ".agents/skills/evidence-code-review"
        skill = package_metadata(installed_skill)
        skill_text = (installed_skill / "SKILL.md").read_text(encoding="utf-8")
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
        model_evidence = reported_model(events, stderr)
        read_observed = skill_file_read_observed(events, skill_text)
        return {
            "case_id": case["id"],
            "language": language,
            "run_number": run_number,
            "exit_code": exit_code,
            "status": "completed" if exit_code == 0 and answer.strip() else (
                "no_answer" if exit_code == 0 else "agent_error"
            ),
            "usage": event_usage(events),
            "requested_model": model,
            "observed_model": model_evidence["model"],
            "model_evidence": model_evidence["source"],
            "skill": skill,
            "invocation_mode": "implicit",
            "skill_file_read_observed": read_observed,
            "skill_evidence": "file_read_observed" if read_observed else "not_observed",
            "skill_invocation": "not_verified",
            "observed": observed_output(answer, case["expectations"]),
            "raw_directory": run_dir.name,
        }


def output_directory(requested: Path | None) -> Path:
    repository = ROOT.resolve()

    def outside_repository(path: Path) -> Path:
        resolved = path.expanduser().resolve()
        if resolved == repository or repository in resolved.parents:
            raise ValueError("evaluation output must be outside this repository")
        return resolved

    if requested is None:
        # TMPDIR may be inside the checkout, including through a symlink.
        temporary_root = outside_repository(Path(tempfile.gettempdir()))
        created = Path(tempfile.mkdtemp(prefix="evidence-review-eval-", dir=temporary_root))
        try:
            return outside_repository(created)
        except ValueError:
            created.rmdir()  # Only the newly created, still-empty directory.
            raise
    resolved = outside_repository(requested)
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
    try:
        skill = package_metadata(SKILL)
    except OSError as error:
        parser.error(f"cannot read generated Skill metadata: {error}")
    report = {
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "agent": "codex",
        "agent_version": version.stdout.strip() if version.returncode == 0 else "unavailable",
        "model": args.model or "unavailable (CLI default)",
        "model_source": "requested" if args.model else "unavailable",
        "requested_model": args.model,
        "observed_models": [],
        "cost": "unavailable",
        "skill_revision": revision.stdout.strip() if revision.returncode == 0 else "unavailable",
        "worktree_dirty": worktree_dirty(),
        "evaluation_inputs_dirty": worktree_dirty([
            "src", "dist", "tests/cases", "tests/agent_eval.py"
        ]),
        "skill": skill,
        "invocation_mode": "implicit",
        "settings": {"sandbox": "read-only", "ephemeral": True, "ignore_user_config": True,
                     "approval_policy": "never", "timeout_seconds": args.timeout},
        "selected_cases": [case["id"] for _, case, _, _ in cases],
        "requested_runs_per_case": args.runs,
        "results": [],
        "notes": "Prefix and negative-output checks are syntax-only and provisional. "
                 "explicit_no_findings is an informational, best-effort phrase match: "
                 "it can miss no-finding statements or match partial statements alongside "
                 "findings, and is never a pass/fail signal. Semantic findings, "
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
                observed_models = sorted({
                    item["observed_model"] for item in report["results"]
                    if item.get("observed_model")
                })
                report["observed_models"] = observed_models
                if observed_models:
                    report["model"] = observed_models[0] if len(observed_models) == 1 else "multiple CLI-reported models"
                    report["model_source"] = "cli_reported"
                (destination / "summary.json").write_text(
                    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
    except (OSError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        print(f"Local evaluation files: {destination}", file=sys.stderr)
        return 1
    print(f"Local evaluation files: {destination}")
    return 0 if all(item["status"] == "completed" for item in report["results"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
