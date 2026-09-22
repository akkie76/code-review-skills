# Code Review Skills

Reusable code-review skills for AI coding agents.

This project is under development. The first release will provide a shared,
vendor-neutral review workflow and generated distributions for supported
agents, including Codex and Claude Code.

## Goals

- Produce findings that are correct, actionable, and supported by evidence.
- Respect repository-specific instructions and engineering conventions.
- Separate the shared review methodology from agent-specific packaging.
- Keep distributed skills self-contained and straightforward to install.

## Planned structure

```text
src/          Shared source material and agent adapters
dist/         Generated, installable skills
scripts/      Build and validation commands
tests/        Skill evaluations and fixtures
docs/         Development and publication documentation
```

See [the development roadmap](docs/ROADMAP.md) for the planned commits leading
to the first public release.

## Publication status

The repository is being developed privately. Publication is gated on content,
licensing, attribution, and release checks described in
[the content policy](docs/CONTENT_POLICY.md).

## License

The original material in this repository is licensed under the
[MIT License](LICENSE).
