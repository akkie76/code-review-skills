#!/usr/bin/env python3
"""Run repository checks that must pass before a public release."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISALLOWED_SUFFIXES = {".pdf", ".doc", ".docx", ".pages"}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[oprsu]_[A-Za-z0-9_]{30,}\b"),
    "OpenAI key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def main() -> int:
    errors: list[str] = []
    tracked = [Path(path) for path in git("ls-files").splitlines()]
    history_names = [
        Path(path)
        for path in git("log", "--all", "--name-only", "--format=").splitlines()
        if path.strip()
    ]

    for label, paths in (("tracked", tracked), ("history", history_names)):
        for path in paths:
            if path.suffix.lower() in DISALLOWED_SUFFIXES or path.name == ".DS_Store":
                errors.append(f"disallowed {label} file: {path}")

    local_home_prefix = "/" + "Users/"
    for path in tracked:
        absolute = ROOT / path
        if not absolute.is_file():
            continue
        try:
            text = absolute.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if local_home_prefix in text:
            errors.append(f"local absolute path in {path}")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {name} in {path}")

    required = {
        "README.md",
        "README.ja.md",
        "LICENSE",
        "SECURITY.md",
        "SECURITY.ja.md",
        "SUPPORT.md",
        "SUPPORT.ja.md",
        "CHANGELOG.md",
        "CHANGELOG.ja.md",
        "docs/CONTENT_POLICY.md",
        "docs/CONTENT_POLICY.ja.md",
        "docs/DEVELOPMENT.md",
        "docs/DEVELOPMENT.ja.md",
        "docs/RELEASE_CHECKLIST.md",
        "docs/RELEASE_CHECKLIST.ja.md",
        "docs/releases/v0.1.0.md",
        "docs/releases/v0.1.0.ja.md",
        "tests/README.md",
        "tests/README.ja.md",
    }
    missing = required - {path.as_posix() for path in tracked}
    errors.extend(f"missing release file: {path}" for path in sorted(missing))

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"Release checks passed for {len(tracked)} tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
