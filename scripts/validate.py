#!/usr/bin/env python3
"""Validate generated skill packages using only the Python standard library."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = tuple(sorted((ROOT / "dist").glob("*/code-review/SKILL.md")))
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
        if re.search(r"\[[^]]+\]\((?!https?://|#)[^)]+\)", text):
            errors.append(f"package contains a non-self-contained relative link: {relative}")
        local_home_prefix = "/" + "Users/"
        if local_home_prefix in text:
            errors.append(f"package contains a local or private source reference: {relative}")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"Validated {len(PACKAGES)} generated skill packages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
