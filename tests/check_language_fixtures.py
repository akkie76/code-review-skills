#!/usr/bin/env python3
"""Compile Java and test Go evaluation fixtures after applying each patch."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


CASES = Path(__file__).resolve().parent / "cases"


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"{cwd.name}: {' '.join(command)} failed:\n{result.stdout}"
        )


def main() -> int:
    counts = {"go": 0, "java": 0}
    for case in sorted(CASES.iterdir()):
        repository = case / "repository"
        if not repository.is_dir():
            continue
        is_go = (repository / "go.mod").is_file()
        is_java = any(repository.rglob("*.java"))
        if not is_go and not is_java:
            continue

        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / case.name
            shutil.copytree(repository, checkout)
            run(["git", "apply", str((case / "change.diff").resolve())], checkout)

            if is_go:
                sources = sorted(checkout.rglob("*.go"))
                if not sources:
                    raise RuntimeError(f"{case.name}: Go module contains no .go files")
                result = subprocess.run(
                    ["gofmt", "-l", *(str(source) for source in sources)],
                    cwd=checkout,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if result.returncode or result.stdout.strip():
                    raise RuntimeError(
                        f"{case.name}: gofmt check failed:\n"
                        f"{result.stdout}{result.stderr}"
                    )
                go_env = os.environ.copy()
                go_env.update(GOPROXY="off", GOSUMDB="off", GOTOOLCHAIN="local")
                run(["go", "test", "./..."], checkout, go_env)
                counts["go"] += 1

            if is_java:
                sources = sorted(checkout.rglob("*.java"))
                classes = checkout / "classes"
                classes.mkdir()
                run(
                    ["javac", "--release", "17", "-d", str(classes),
                     *(str(source) for source in sources)],
                    checkout,
                )
                counts["java"] += 1

    if not all(counts.values()):
        raise RuntimeError(f"expected both Go and Java fixtures, found {counts}")
    print(f"Validated {counts['go']} Go and {counts['java']} Java fixtures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
