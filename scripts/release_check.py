#!/usr/bin/env python3
"""Run repository checks that must pass before a public release."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
DISALLOWED_SUFFIXES = {".pdf", ".doc", ".docx", ".pages"}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(
        r"\b(?:gh[oprsu]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{20,})\b"
    ),
    "OpenAI key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
}
LOCAL_HOME_PATTERNS = {
    "macOS": re.compile("/" + r"Users/[^/\s]+/"),
    "Linux": re.compile("/" + r"home/[^/\s]+/"),
    "Windows": re.compile(
        r"\b[A-Za-z]:[\\/]+Users[\\/]+[^\\/\r\n]+[\\/]", re.IGNORECASE
    ),
}


def contains_local_home_path(text: str) -> bool:
    return any(pattern.search(text) for pattern in LOCAL_HOME_PATTERNS.values())


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


def version_consistency_errors(check_tag: bool = False) -> list[str]:
    """Check the source version, packages, and (after tagging) release artifacts."""
    errors: list[str] = []
    version_file = ROOT / "VERSION"
    if not version_file.is_file():
        return ["missing VERSION"]
    version = version_file.read_text(encoding="utf-8").strip()
    if not SEMVER_PATTERN.fullmatch(version):
        return [f"VERSION is not a valid SemVer version: {version!r}"]

    tag = f"v{version}"
    marker = f"<!-- skill-version: {tag} -->"
    for agent in ("codex", "claude-code"):
        package = ROOT / "dist" / agent / "evidence-code-review" / "SKILL.md"
        if (
            not package.is_file()
            or package.read_text(encoding="utf-8").count(marker) != 1
        ):
            errors.append(f"{agent} package must contain exactly one {marker} marker")

    if not check_tag:
        return errors

    if tag not in git("tag", "--points-at", "HEAD").splitlines():
        errors.append(f"Git tag {tag} must point to HEAD")
    for language, changelog, notes in (
        ("English", ROOT / "CHANGELOG.md", ROOT / "docs/releases" / f"{tag}.md"),
        ("Japanese", ROOT / "CHANGELOG.ja.md", ROOT / "docs/releases" / f"{tag}.ja.md"),
    ):
        if not changelog.is_file():
            errors.append(f"missing {language} changelog: {changelog.relative_to(ROOT)}")
        else:
            content = changelog.read_text(encoding="utf-8")
            dated_section = rf"(?m)^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$"
            release_link = (
                rf"(?m)^\[{re.escape(version)}\]: "
                rf"https://github\.com/akkie76/code-review-skills/releases/tag/{re.escape(tag)}$"
            )
            if not re.search(dated_section, content):
                errors.append(f"{language} changelog needs a dated {version} section")
            if not re.search(release_link, content):
                errors.append(f"{language} changelog needs a {tag} release link")
        if not notes.is_file():
            errors.append(f"missing {language} release notes: {notes.relative_to(ROOT)}")
        elif not notes.read_text(encoding="utf-8").startswith(f"# Code Review Skills {tag}\n"):
            errors.append(f"{language} release notes must identify {tag}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tag",
        action="store_true",
        help="also require the current version's tag, changelogs, and release notes",
    )
    args = parser.parse_args()
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
        if contains_local_home_path(text):
            errors.append(f"local absolute path in {path}")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {name} in {path}")

    for oid, path, text in historical_blobs():
        if contains_local_home_path(text):
            errors.append(f"local absolute path in Git history: {path} ({oid[:12]})")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {name} in Git history: {path} ({oid[:12]})")

    required = {
        "README.md",
        "README.ja.md",
        "VERSION",
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
        "docs/VERSIONING.md",
        "docs/VERSIONING.ja.md",
        "docs/releases/v0.1.0-beta.1.md",
        "docs/releases/v0.1.0-beta.1.ja.md",
        "tests/README.md",
        "tests/README.ja.md",
        "tests/RESULT_TEMPLATE.md",
        "tests/RESULT_TEMPLATE.ja.md",
    }
    missing = required - {path.as_posix() for path in tracked}
    errors.extend(f"missing release file: {path}" for path in sorted(missing))
    errors.extend(version_consistency_errors(check_tag=args.tag))

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
