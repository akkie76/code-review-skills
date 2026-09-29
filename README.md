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
- Optionally decomposes complex reviews across independent sub-agents when the
  environment supports delegation, followed by a required integration pass.
- Requires a concrete trigger and impact for every finding.
- Prefixes each comment with its action level and viewpoint, such as
  `MUST(Functionality):` or `BETTER(Simplicity):`.
- Produces prioritized findings in English or Japanese.

The skill reviews code; it does not modify the reviewed code unless the user
separately asks for changes.

See the [review comment convention](docs/REVIEW_COMMENTS.md) for action levels,
viewpoints, and communication rules.

## Install

Clone this repository and copy the complete package directory for your agent.
Copying only `SKILL.md` omits required references.

### Codex

For all local projects:

```sh
mkdir -p ~/.codex/skills
cp -R dist/codex/evidence-code-review ~/.codex/skills/
```

For one repository, copy the package to
`.agents/skills/evidence-code-review/` inside that repository instead. Start a
new Codex task after installation, then ask it to use `evidence-code-review` to
review a diff, commit, branch, pull request, or working tree.

### Claude Code

For all local projects:

```sh
mkdir -p ~/.claude/skills
cp -R dist/claude-code/evidence-code-review ~/.claude/skills/
```

For one repository, copy the package to
`.claude/skills/evidence-code-review/` inside that repository instead. Invoke
it with `/evidence-code-review` or ask Claude Code to use the
`evidence-code-review` skill.

The installed package records its version in a `skill-version` comment near
the top of `SKILL.md`. This repository's current version is in `VERSION`.

Review a skill before installing it. A skill supplies instructions to an
agent and should be treated like other executable development configuration.
See the [installation guide](docs/INSTALLATION.md) for project installation,
Windows commands, verification, updates, removal, and troubleshooting.

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

### Project technology guidance

Language, framework, SDK, and tool requirements vary by project. Store the
information needed for accurate reviews in the reviewed repository's
`AGENTS.md`, `CLAUDE.md`, or a project document referenced by those files. Do
not edit the installed Skill; updates may replace it.

Relevant material can include version constraints, lifecycle or concurrency
rules, architecture conventions, and verification commands. If no guidance is
supplied, the reviewer uses repository evidence and avoids assuming
technology-specific guarantees.

## Project policy

This project currently follows a maintainer-led beta process. Evidence-backed
Issues about defects, review accuracy, agent compatibility, and documentation
are welcome. Pull requests require prior agreement. See
[SUPPORT.md](SUPPORT.md) for the scope and evidence expected, and
[SECURITY.md](SECURITY.md) for private vulnerability reporting guidance.

The repository contains independently authored material. Its source and
publication boundaries are described in
[docs/CONTENT_POLICY.md](docs/CONTENT_POLICY.md).

## License

The original material in this repository is licensed under the
[MIT License](LICENSE).
