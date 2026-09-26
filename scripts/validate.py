#!/usr/bin/env python3
"""Validate generated skill packages using only the Python standard library."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = tuple(sorted((ROOT / "dist").glob("*/evidence-code-review/SKILL.md")))
EXPECTED_PACKAGES = 2


def main() -> int:
    errors: list[str] = []
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        errors.append(result.stdout.strip() or result.stderr.strip())

    if len(PACKAGES) != EXPECTED_PACKAGES:
        errors.append(f"expected {EXPECTED_PACKAGES} packages, found {len(PACKAGES)}")

    for package in PACKAGES:
        relative = package.relative_to(ROOT)
        text = package.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            errors.append(f"invalid frontmatter delimiters: {relative}")
        frontmatter = text.split("---", 2)[1]
        for key in ("name", "description"):
            if not re.search(rf"^{key}:\s*\S", frontmatter, re.MULTILINE):
                errors.append(f"missing {key} in frontmatter: {relative}")
        name_match = re.search(r"^name:\s*(\S+)\s*$", frontmatter, re.MULTILINE)
        if name_match and name_match.group(1) != package.parent.name:
            errors.append(f"frontmatter name must match directory: {relative}")
        description_match = re.search(
            r"^description:\s*(.+)$", frontmatter, re.MULTILINE
        )
        if description_match and len(description_match.group(1)) > 1024:
            errors.append(f"frontmatter description exceeds 1024 characters: {relative}")
        for target in re.findall(r"\[[^]]+\]\((?!https?://|#)([^)]+)\)", text):
            resolved = package.parent / target.split("#", 1)[0]
            if not resolved.is_file():
                errors.append(f"broken package link {target}: {relative}")
        local_home_prefix = "/" + "Users/"
        technology_guide = package.parent / "references/technologies/README.md"
        if not technology_guide.is_file():
            errors.append(f"package is missing technology guidance: {relative}")
        output_contract = package.parent / "references/output-contract.md"
        if not output_contract.is_file():
            errors.append(f"package is missing output contract: {relative}")
        else:
            contract_text = output_contract.read_text(encoding="utf-8")
            for prefix in ("MUST(", "SHOULD(", "BETTER(", "NITS("):
                if prefix not in contract_text:
                    errors.append(f"missing review prefix {prefix}: {relative}")
        for bundled_file in package.parent.rglob("*"):
            if bundled_file.is_file() and local_home_prefix in bundled_file.read_text(
                encoding="utf-8"
            ):
                errors.append(
                    "package contains a local source reference: "
                    f"{bundled_file.relative_to(ROOT)}"
                )
        if len(text.splitlines()) >= 500:
            errors.append(f"SKILL.md must remain under 500 lines: {relative}")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"Validated {len(PACKAGES)} generated skill packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
