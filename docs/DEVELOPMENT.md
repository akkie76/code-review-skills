# Development Guide

## Source model

Edit the shared review methodology under `src/core/`. The optional technology
guidance entry point lives under `src/technologies/`. The generator combines
these sources into self-contained packages under `dist/` for every supported
agent. Do not edit generated package files directly.

## Change procedure

1. Make the smallest vendor-neutral change under `src/core/` or
   `src/technologies/`.
2. Add or update a behavioral evaluation under `tests/cases/`.
3. Run `make build`.
4. Run `make test`.
5. Inspect the generated diff for unintended or source-specific content.
6. Run the affected cases manually in both Codex and Claude Code.

The maintainer records manual results outside the public repository while the
project is private. A generated-file-only change is invalid because the next
build overwrites it.

## Distribution guarantees

- Generation works offline with the Python standard library.
- Every package has valid `name` and `description` frontmatter.
- Each package is self-contained and contains no relative documentation link.
- Repeated generation produces the same bytes.
- Local paths and private source-material identifiers are rejected.

## External changes

Development is currently maintainer-led. Do not open an Issue or pull request
without prior agreement. See [the support policy](../SUPPORT.md) for the
evidence expected during an announced evaluation round.
