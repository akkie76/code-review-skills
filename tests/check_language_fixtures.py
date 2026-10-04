#!/usr/bin/env python3
"""Check Java, Go, and Python evaluation fixtures after applying each patch."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
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


def check_fixtures() -> int:
    counts = {"go": 0, "java": 0, "python": 0}
    for case in sorted(CASES.iterdir()):
        repository = case / "repository"
        if not repository.is_dir():
            continue
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / case.name
            shutil.copytree(repository, checkout)
            run(["git", "apply", str((case / "change.diff").resolve())], checkout)

            go_sources = sorted(checkout.rglob("*.go"))
            go_module = checkout / "go.mod"
            is_go = go_module.is_file() or bool(go_sources)
            is_java = any(checkout.rglob("*.java"))
            is_python = any(checkout.rglob("*.py"))
            if not (is_go or is_java or is_python):
                continue

            if is_go:
                if not go_module.is_file():
                    raise RuntimeError(f"{case.name}: Go sources require go.mod")
                if not go_sources:
                    raise RuntimeError(f"{case.name}: Go module contains no .go files")
                result = subprocess.run(
                    ["gofmt", "-l", *(str(source) for source in go_sources)],
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

            if is_python:
                run([sys.executable, "-m", "compileall", "-q", "."], checkout)
                if any(checkout.rglob("test_*.py")):
                    run(
                        [sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"],
                        checkout,
                    )
                counts["python"] += 1

    if not all(counts.values()):
        raise RuntimeError(f"expected Go, Java, and Python fixtures, found {counts}")
    print(
        f"Validated {counts['go']} Go, {counts['java']} Java, "
        f"and {counts['python']} Python fixtures."
    )
    return 0


def main() -> int:
    try:
        return check_fixtures()
    except (OSError, RuntimeError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
