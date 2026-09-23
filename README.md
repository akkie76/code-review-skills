# Code Review Skills

[日本語](README.ja.md)

Code Review Skills is an evidence-driven code-review workflow for AI coding
agents. It helps Codex and Claude Code find actionable defects while avoiding
style-only comments and unsupported speculation.

> **Beta:** The review methodology and packaging are under evaluation. Expect
> changes before the first stable release.

## What it does

- Establishes the requested review scope and repository-specific rules.
- Traces changed behavior beyond the modified lines.
- Checks correctness, interfaces, design, security, reliability, tests, and
  documentation according to risk.
- Requires a concrete trigger and impact for every finding.
- Produces prioritized findings in English or Japanese.

The skill reviews code; it does not modify the reviewed code unless the user
separately asks for changes.

## Install

Clone this repository and choose the package for your agent.

### Codex

For all local projects:

```sh
mkdir -p ~/.codex/skills/code-review
cp dist/codex/code-review/SKILL.md ~/.codex/skills/code-review/SKILL.md
```

For one repository, copy the package to
`.agents/skills/code-review/SKILL.md` inside that repository instead. Start a
new Codex task after installation, then ask it to review a diff, commit,
branch, pull request, or working tree.

### Claude Code

For all local projects:

```sh
mkdir -p ~/.claude/skills/code-review
cp dist/claude-code/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md
```

For one repository, copy the package to
`.claude/skills/code-review/SKILL.md` inside that repository instead. Invoke it
with `/code-review` or ask Claude Code to review a change.

Review a skill before installing it. A skill supplies instructions to an
agent and should be treated like other executable development configuration.

## Development

The files under `src/core/` are the canonical, vendor-neutral methodology.
Files under `dist/` are generated and must not be edited directly.

```sh
make build  # regenerate every agent package
make check  # validate frontmatter, links, and generated freshness
make test   # also validate behavioral evaluation fixtures
```

`make build` uses only the Python standard library and does not require
network access. See [the evaluation guide](tests/README.md) for manual testing
with each agent.

## Project policy

This project currently follows a maintainer-led beta process. Unsolicited
Issues and pull requests are not accepted. See [SUPPORT.md](SUPPORT.md) for the
feedback policy and [SECURITY.md](SECURITY.md) for private vulnerability
reporting guidance.

The repository contains independently authored material. Its source and
publication boundaries are described in
[docs/CONTENT_POLICY.md](docs/CONTENT_POLICY.md).

## License

The original material in this repository is licensed under the
[MIT License](LICENSE).
