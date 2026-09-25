# Changelog

[日本語](CHANGELOG.ja.md)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/akkie76/code-review-skills/compare/v0.1.0-beta.1...HEAD
