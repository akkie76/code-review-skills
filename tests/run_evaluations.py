#!/usr/bin/env python3
"""Validate behavioral evaluation fixtures without invoking an AI service."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests/cases"
REQUIRED_EXPECTATIONS = {"must_report", "must_not_report", "prefixes", "output"}
VALID_RESULTS = {"findings", "no_findings"}
REQUIRED_FALSE_POSITIVE_CATEGORIES = {
    "behavior-preserving-refactor",
    "tool-enforced-style",
    "pre-existing-defect",
    "verified-language-guarantee",
    "fully-updated-shared-contract",
}


def main() -> int:
    errors: list[str] = []
    identifiers: set[str] = set()
    case_files = sorted(CASES.glob("*/case.json"))
    if not case_files:
        errors.append("no evaluation cases found")

    kinds: set[str] = set()
    languages: set[str] = set()
    observed_action_levels: set[str] = set()
    observed_viewpoints: set[str] = set()
    negative_categories: set[str] = set()
    for case_file in case_files:
        relative = case_file.relative_to(ROOT)
        try:
            case = json.loads(case_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            errors.append(f"cannot read {relative}: {error}")
            continue

        identifier = case.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"missing id: {relative}")
        elif identifier in identifiers:
            errors.append(f"duplicate id {identifier}: {relative}")
        else:
            identifiers.add(identifier)

        kind = case.get("kind")
        if kind not in {"positive", "negative", "instruction-conflict"}:
            errors.append(f"invalid kind in {relative}: {kind!r}")
        else:
            kinds.add(kind)

        requests = case.get("requests")
        if not isinstance(requests, list) or not requests:
            errors.append(f"requests must be a non-empty list: {relative}")
        else:
            for request in requests:
                if not isinstance(request, dict) or not request.get("prompt"):
                    errors.append(f"invalid request in {relative}")
                    continue
                languages.add(request.get("language", ""))

        expectations = case.get("expectations", {})
        if kind == "negative":
            category = case.get("false_positive_category")
            if not isinstance(category, str) or not category.strip():
                errors.append(f"negative case needs a false-positive category: {relative}")
            else:
                negative_categories.add(category)
            suppressed = expectations.get("must_not_report")
            if not isinstance(suppressed, list) or not suppressed or not all(
                isinstance(item, str) and item.strip() for item in suppressed
            ):
                errors.append(f"negative case needs non-empty must_not_report: {relative}")
        missing = REQUIRED_EXPECTATIONS - expectations.keys()
        if missing:
            errors.append(f"missing expectations {sorted(missing)}: {relative}")
        if expectations.get("output") not in VALID_RESULTS:
            errors.append(f"invalid expected output in {relative}")
        prefixes = expectations.get("prefixes")
        if not isinstance(prefixes, list) or not all(
            isinstance(prefix, str)
            and re.fullmatch(
                r"(?:MUST|SHOULD|BETTER|NITS)\((?:Design|Simplicity|Naming|Style|Functionality|Test|Document)\)",
                prefix,
            )
            for prefix in prefixes
        ):
            errors.append(f"invalid expected prefixes in {relative}")
        else:
            for prefix in prefixes:
                action, viewpoint = prefix[:-1].split("(", 1)
                observed_action_levels.add(action)
                observed_viewpoints.add(viewpoint)

        patch = case_file.parent / "change.diff"
        if not patch.is_file() or not patch.read_text(encoding="utf-8").strip():
            errors.append(f"missing or empty change.diff beside {relative}")
        repository = case_file.parent / "repository"
        if not repository.is_dir() or not any(path.is_file() for path in repository.rglob("*")):
            errors.append(f"missing repository context beside {relative}")
        else:
            with tempfile.TemporaryDirectory() as temporary:
                checkout = Path(temporary) / "repository"
                shutil.copytree(repository, checkout)
                result = subprocess.run(
                    ["git", "apply", "--check", str(patch.resolve())],
                    cwd=checkout,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if result.returncode:
                    errors.append(
                        f"change.diff does not apply beside {relative}: "
                        f"{result.stderr.strip()}"
                    )

    required_kinds = {"positive", "negative", "instruction-conflict"}
    if kinds != required_kinds:
        errors.append(f"case kinds must include {sorted(required_kinds)}")
    if not {"en", "ja"}.issubset(languages):
        errors.append("evaluation requests must cover both English and Japanese")
    required_action_levels = {"MUST", "SHOULD", "BETTER", "NITS"}
    if observed_action_levels != required_action_levels:
        errors.append(
            f"expected prefixes must cover action levels {sorted(required_action_levels)}"
        )
    required_viewpoints = {
        "Design", "Simplicity", "Naming", "Style", "Functionality", "Test", "Document"
    }
    if observed_viewpoints != required_viewpoints:
        errors.append(
            f"expected prefixes must cover viewpoints {sorted(required_viewpoints)}"
        )
    missing_categories = REQUIRED_FALSE_POSITIVE_CATEGORIES - negative_categories
    if missing_categories:
        errors.append(
            f"negative cases must cover {sorted(missing_categories)}"
        )

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"Validated {len(case_files)} behavioral evaluation cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
