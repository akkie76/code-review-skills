# Changelog

[日本語](CHANGELOG.ja.md)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-10

### Added

- A local evaluation runner for Codex and Claude Code, plus a human-adjudicated
  scoring workflow with an 80-point per-agent acceptance threshold.
- A sanitized v2 evaluation report covering 29 primary cases and six diagnostic
  repeats per agent, with campaign provenance and limitations.
- Stable-release documentation, installation guidance, and security reporting
  instructions for the 1.0.0 release.

### Changed

- Clarified review behavior for verifying supporting claims, handling accurate
  non-actionable scope notes, identifying mandatory repository-rule violations
  and startup-blocking setup instructions, and reporting change-created dead
  helpers and behavior-specific test gaps.
- Declared the documented finding-output contract stable while explicitly
  leaving finding decisions, detection rates, and repeated-run wording dependent
  on the model and project context.
- Updated the READMEs and support policies for the stable release.

## [0.1.0-beta.2] - 2026-10-04

### Added

- Ten negative and realistic behavioral fixtures, including larger mixed-noise
  changes in Go, Java, and Python. The suite now contains 28 cases.
- Java, Go, and Python fixture checks in CI after applying each case's patch.
- A canonical version file and version marker in both generated Skill packages.
- English and Japanese versioning and output-compatibility policies, with
  release checks for package versions and tagged release artifacts.
- Sanitized Codex and Claude Code evaluation records that distinguish fixture
  matches from Skill invocation and document their limitations.
- An accuracy-improvement proposal Issue form for evidence-backed suggestions
  that have not yet been tested with the Skill.

### Changed

- Clarified that repository review instructions complement the Skill rather
  than replace it when selecting the Skill for a review request.
- Documented explicit Claude Code invocation when automatic selection varies.
- Clarified how optional findings are scored without weakening the evidence
  required for every factual claim.
- Linked the publisher's official page for *コードレビューの教科書* from both READMEs.

## [0.1.0-beta.1] - 2026-09-27

### Added

- A vendor-neutral, evidence-driven code-review workflow.
- Self-contained skill packages for Codex and Claude Code.
- English and Japanese review output rules and installation documentation.
- Behavioral fixtures for defect detection, false-positive control, and
  instruction boundaries.
- Offline build, validation, and release-readiness checks.
- Action-level and review-viewpoint prefixes for every review comment.
- Constructive comment-writing rules that preserve clarity and respect.
- A collision-resistant `evidence-code-review` skill name and complete-package
  installation instructions.
- Progressive loading of focused review references, expanded evaluation
  coverage, CI, and complete-history release checks.
- Explicit tracing of existing callers and consumers when a shared contract
  changes, including disclosure when complete enumeration is not possible.
- Cross-variant tracing for unconditional effects inside shared dispatch
  handlers, with regression fixtures for variant safety and ineffective tests.
- Direct verification of every cited supporting fact, including precedents,
  nearby patterns, unchanged behavior, and specific source locations.
- Per-concern review coverage for bundled changes and same-diff consistency
  checks for conceptually equivalent implementations.
- Optional multi-agent review decomposition by concern or viewpoint, with
  independent validation and a required reconciliation pass.
- Change-map tracking for repeated decisions and safe focused verification of
  the specific risky input or path behind a candidate finding.
- Optional delegation of a complex candidate check to a single-purpose
  verifier while retaining final-reviewer ownership of the evidence and result.
- Review guidance and a behavioral fixture for dead code introduced by the
  reviewed change, with required consumer verification before reporting it.
- Structured Issue forms and a support policy for evidence-backed beta
  feedback while keeping pull requests subject to prior agreement.

[1.0.0]: https://github.com/akkie76/code-review-skills/releases/tag/v1.0.0
[0.1.0-beta.2]: https://github.com/akkie76/code-review-skills/releases/tag/v0.1.0-beta.2
[0.1.0-beta.1]: https://github.com/akkie76/code-review-skills/releases/tag/v0.1.0-beta.1
