# Claude campaign revision drift — 2026-10-07

[日本語](2026-10-07-claude-revision-drift.ja.md)

Source: the maintainer's [PR #45 execution report](https://github.com/akkie76/code-review-skills/pull/45#issuecomment-6028073864).
This records the reported incident, not an independent inspection of private logs.

- Host: Claude Code `2.1.281`, `claude-opus-5-5`, committed static-only runner.
- First two primary sessions: frozen `b459626`.
- An external checkout switch was reported after that batch. The remaining
  **33 sessions** (27 primary + six repeats) used `01f73e0`.
- All 35 completed, with identical evaluation inputs/package hashes according
  to the report. Nevertheless, the frozen commit requirement was not met.
  The mixed campaign is ineligible for import; artifacts remain private and
  judgments were not drafted. There is no accepted score or semantic pass rate.
- The report's 35/35 `confirmed` labels used the previous request-only detector.
  They are not retrospectively asserted to satisfy the new successful-result rule.
  Reported prefix differences are mechanical observations, not finalized judgments.

The tooling now supports isolated `--revision` snapshots, before/after input
checks, stop-on-error, and bytecode ignores. Initialization freezes execution
settings including timeout. Claude invocation evidence requires a matching,
successful tool result; required prefixes cannot be repaired by unrelated comments.

Retain this record and the earlier Codex campaign as historical evidence. Do not
rewrite SHA/settings, import mixed records, or loosen the freeze rule retroactively.
Any replacement uses a new common committed revision and all 35 sessions per
agent, followed by human adjudication. No replacement model calls are part of
this tooling fix. Content-only freeze keys and a batch-plan driver are deferred.
