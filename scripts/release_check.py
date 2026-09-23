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
LOCAL_HOME_PATTERN = re.compile("/" + r"Users/[^/\s]+/")


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def historical_blobs() -> list[tuple[str, str, str]]:
    """Return unique UTF-8 Git blobs with one known historical path."""
    objects: dict[str, str] = {}
    for line in git("rev-list", "--objects", "--all").splitlines():
        oid, _, path = line.partition(" ")
        if path:
            objects.setdefault(oid, path)

    result = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        input=("\n".join(objects) + "\n").encode(),
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace").strip())

    blobs: list[tuple[str, str, str]] = []
    output = result.stdout
    position = 0
    while position < len(output):
        header_end = output.find(b"\n", position)
        if header_end < 0:
            raise RuntimeError("malformed git cat-file output")
        header = output[position:header_end].decode("ascii", errors="replace").split()
        position = header_end + 1
        if len(header) < 3:
            raise RuntimeError("unexpected git cat-file header")
        oid, object_type, size_text = header[:3]
        size = int(size_text)
        data = output[position : position + size]
        position += size + 1
        if object_type != "blob":
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        blobs.append((oid, objects.get(oid, "<unknown>"), text))
    return blobs


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

    for path in tracked:
        absolute = ROOT / path
        if not absolute.is_file():
            continue
        try:
            text = absolute.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LOCAL_HOME_PATTERN.search(text):
            errors.append(f"local absolute path in {path}")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {name} in {path}")

    for oid, path, text in historical_blobs():
        if LOCAL_HOME_PATTERN.search(text):
            errors.append(f"local absolute path in Git history: {path} ({oid[:12]})")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {name} in Git history: {path} ({oid[:12]})")

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
        "docs/INSTALLATION.md",
        "docs/INSTALLATION.ja.md",
        "docs/RELEASE_CHECKLIST.md",
        "docs/RELEASE_CHECKLIST.ja.md",
        "docs/REVIEW_COMMENTS.md",
        "docs/REVIEW_COMMENTS.ja.md",
        "docs/releases/v0.1.0.md",
        "docs/releases/v0.1.0.ja.md",
        "tests/README.md",
        "tests/README.ja.md",
        "tests/RESULT_TEMPLATE.md",
        "tests/RESULT_TEMPLATE.ja.md",
    }
    missing = required - {path.as_posix() for path in tracked}
    errors.extend(f"missing release file: {path}" for path in sorted(missing))

    link_pattern = re.compile(r"\[[^]]*\]\(([^)]+)\)")
    for path in tracked:
        if path.suffix.lower() != ".md":
            continue
        text = (ROOT / path).read_text(encoding="utf-8")
        for target in link_pattern.findall(text):
            if re.match(r"^[a-z]+://", target) or target.startswith("#"):
                continue
            relative_target = target.split("#", 1)[0]
            if relative_target and not ((ROOT / path).parent / relative_target).exists():
                errors.append(f"broken Markdown link in {path}: {target}")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"Release checks passed for {len(tracked)} tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
