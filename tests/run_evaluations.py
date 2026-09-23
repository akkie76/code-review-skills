#!/usr/bin/env python3
"""Validate behavioral evaluation fixtures without invoking an AI service."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests/cases"
REQUIRED_EXPECTATIONS = {"must_report", "must_not_report", "prefixes", "output"}
VALID_RESULTS = {"findings", "no_findings"}


def main() -> int:
    errors: list[str] = []
    identifiers: set[str] = set()
    case_files = sorted(CASES.glob("*/case.json"))
    if not case_files:
        errors.append("no evaluation cases found")

    kinds: set[str] = set()
    languages: set[str] = set()
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

        patch = case_file.parent / "change.diff"
        if not patch.is_file() or not patch.read_text(encoding="utf-8").strip():
            errors.append(f"missing or empty change.diff beside {relative}")
        repository = case_file.parent / "repository"
        if not repository.is_dir() or not any(path.is_file() for path in repository.rglob("*")):
            errors.append(f"missing repository context beside {relative}")

    required_kinds = {"positive", "negative", "instruction-conflict"}
    if kinds != required_kinds:
        errors.append(f"case kinds must include {sorted(required_kinds)}")
    if not {"en", "ja"}.issubset(languages):
        errors.append("evaluation requests must cover both English and Japanese")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"Validated {len(case_files)} behavioral evaluation cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
