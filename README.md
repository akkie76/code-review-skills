# Code Review Skills

[日本語](README.ja.md)

An evidence-driven code-review workflow for Codex and Claude Code.

This Skill is based on ideas from [*コードレビューの教科書*](https://gihyo.jp/book/2026/978-4-297-15768-5)
and independently adapts them for AI coding agents. It does not reproduce or
replace the book.

**Version:** `v1.0.0` · **License:** MIT

The documented review-output format is stable from 1.0.0. Review decisions are
still model- and context-dependent: this Skill does not guarantee that every
defect will be found or that repeated reviews will produce identical findings.

## Get started

Clone the release tag so the installed package has a known version:

```sh
git clone --depth 1 --branch v1.0.0 https://github.com/akkie76/code-review-skills.git
cd code-review-skills
```

### Codex

```sh
mkdir -p ~/.codex/skills
cp -R dist/codex/evidence-code-review ~/.codex/skills/
```

Then start a new Codex task and ask, for example:

> Use the `evidence-code-review` skill to review the changes on this branch against `main`. Focus on correctness, regressions, and tests. Do not modify files.

### Claude Code

```sh
mkdir -p ~/.claude/skills
cp -R dist/claude-code/evidence-code-review ~/.claude/skills/
```

Start a new Claude Code session and invoke the Skill, for example:

```text
/evidence-code-review Review the changes on this branch against main. Focus on correctness, regressions, and tests. Do not modify files.
```

For project-only installation, Windows instructions, verification, updates,
removal, and troubleshooting, see the [installation guide](docs/INSTALLATION.md).

## What it reviews

- Establishes the requested scope and repository-specific rules.
- Traces changed behavior through affected code paths, not only changed lines.
- Checks correctness, interfaces, design, security, reliability, tests, and
  documentation according to risk.
- Reviews code without modifying it unless you separately ask for changes.

## What a review looks like

Actionable comments start with an action level and viewpoint:

- `MUST`: a demonstrated issue that must be resolved before merge.
- `SHOULD`: a concrete risk that normally should be addressed, but may be
  deferred by an explicit decision.
- `BETTER`: an optional alternative with a specific benefit.
- `NITS`: a minor, non-blocking correction.

The viewpoint explains the concern, such as `Functionality`, `Test`,
`Simplicity`, or `Document`. A finding should give its location and concrete
evidence, explain when it occurs and its impact, and suggest a proportionate
direction.

```text
MUST(Functionality): Advance the page before requesting the next result set

Location: `src/client.ts:42`
When the API returns a full page, this loop requests the same page again because
`page` never changes. That duplicates results and increases request volume;
advance the page before the next request.
```

This is an illustrative example. See the [review comment convention](docs/REVIEW_COMMENTS.md)
for the full action-level, viewpoint, evidence, and communication rules.

## Project-specific context

Languages, frameworks, architecture, and test commands differ by repository.
Put the information needed for an accurate review in that repository's
`AGENTS.md`, `CLAUDE.md`, or a project document referenced by those files. Useful
context includes version constraints, lifecycle or concurrency rules,
architecture conventions, and verification commands. Do not store project
information in the installed package; updates may replace it.

## Limits and expectations

- Results depend on the model, agent version, available tools, review scope, and
  project information. A stronger model may help, but does not guarantee a
  correct or complete review.
- Use this Skill alongside tests and human review; it is not a substitute for
  either and cannot guarantee zero missed defects or false positives.
- The Skill does not grant additional permissions. File access and approval
  behavior are controlled by the host agent and its settings.
- Reviewing large changes may consume substantial model tokens.
- The [latest evaluation report](tests/results/2026-10-08-issue-24-v2-evaluation.md)
  describes a small synthetic fixture campaign, not production review accuracy;
  see the [evaluation guide](tests/README.md) for context and other reports.

## Updates and support

- The [versioning policy](docs/VERSIONING.md) describes the stable output
  contract and how changes map to versions.
- See the [installation guide](docs/INSTALLATION.md) for updating or removing
  an installation.
- Evidence-backed bug and accuracy reports are welcome under the
  [support policy](SUPPORT.md). Pull requests require prior agreement.
- Report suspected vulnerabilities privately as described in
  [SECURITY.md](SECURITY.md).

## License

The original material in this repository is licensed under the
[MIT License](LICENSE).
