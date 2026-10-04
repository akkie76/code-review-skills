# Codex beta.2 release-candidate evaluation: 2026-10-04

[日本語](2026-10-04-codex-full.ja.md)

## Scope and method

- Source: PR #41 at `7e3427e`; generated Codex Skill `v0.1.0-beta.2`. The Skill source and generated package were unchanged from the earlier release-branch sample.
- Agent: Codex CLI `0.158.0-alpha.2.1`, model `gpt-6-luna`, high reasoning effort.
- All 28 fixtures were run once in separate, isolated, ephemeral, read-only sessions. The English request was used where available and the Japanese request otherwise. `negative-refactor` was also run in Japanese, for 29 runs total.
- Each temporary repository contained the fixture's baseline files and the project-scoped generated Skill. Its `change.diff` was applied as an uncommitted change, with intent-to-add for any new files. Requests were copied from `case.json` without hints. User configuration was ignored.
- For every run, the captured execution trace showed a successful read of the generated `SKILL.md` and a Git-visible diff. Skill-file reading is observable here; a separate dedicated Skill-invocation event was not available. The evaluator manually compared final output with `must_report`, `must_not_report`, `prefixes`, and `output`. This was not blind or independently graded.
- The first attempt was discarded because log files were placed inside the temporary review repositories. The recorded 29 runs were restarted with logs outside those repositories; only those uncontaminated runs are counted. Raw traces and temporary repositories were not committed.

## Results

| Measure | Result |
| --- | --- |
| Completed runs; Skill-file read; visible diff | 29/29 each |
| Exact fixture passes | 25/29 |
| Cases with required `MUST` content reported | 15/15 |
| `kind: negative` no-finding runs | 7/7 (six fixtures plus Japanese `negative-refactor`) |
| Prohibited findings | 0 observed |
| Additional finding outside the expected one | 1, classified as a valid retry/idempotency concern |
| Clearly unsupported supporting claims found by manual inspection | 0 observed |

| Case | Language | Exact fixture result |
| --- | --- | --- |
| `better-simplify-guard` | English | Fail: no `BETTER(Simplicity)` finding |
| `instruction-boundary` | English | Pass |
| `must-existing-consumer` | English | Pass |
| `must-focused-risk-variant` | English | Pass |
| `must-multi-agent-reconciliation` | English | Pass |
| `must-multi-concern-depth` | English | Pass |
| `must-same-diff-contract` | English | Pass |
| `must-shared-handler-variant` | English | Pass |
| `must-stale-documentation` | Japanese | Fail: `MUST(Functionality)` instead of `MUST(Document)` |
| `must-verified-supporting-evidence` | English | Pass |
| `negative-go-format` | English | Pass |
| `negative-go-runtime` | English | Pass |
| `negative-java-contract` | English | Pass |
| `negative-optional-label` | English | Pass |
| `negative-preexisting-defect` | English | Pass |
| `negative-refactor` | English | Pass |
| `negative-refactor` | Japanese | Pass; same no-finding decision |
| `nits-change-created-dead-code` | English | Pass |
| `nits-misspelled-local` | Japanese | Pass |
| `nits-project-style` | English | Pass |
| `positive-pagination` | English | Pass |
| `realistic-go-directory` | English | Pass |
| `realistic-java-fulfillment` | English | Pass |
| `realistic-python-notice-batch` | English | Pass |
| `realistic-python-profile` | English | Pass |
| `realistic-python-retry-audit` | English | Pass |
| `should-ineffective-regression-test` | English | Pass |
| `should-layer-boundary` | English | Fail: `MUST(Design)` instead of `SHOULD(Design)` |
| `should-missing-test` | English | Fail: expected `SHOULD(Test)` omitted; an additional `MUST(Functionality)` concern was reported |

## Adjudication and release interpretation

1. `better-simplify-guard` missed an optional, behavior-preserving simplification. This is a real fixture miss but not a missed defect or false-positive finding.
2. `must-stale-documentation` reported the required `API_TOKEN`/`SETUP.md` contradiction and a valid `MUST` action, but treated the documented anonymous-mode regression as `Functionality`. Keep the strict prefix mismatch on record; either viewpoint can describe the same root cause.
3. `should-layer-boundary` reported the dependency violation as `MUST(Design)`. The fixture repository explicitly says domain files *must not* depend on UI files, making the stronger action level defensible. Do not retroactively change the expected prefix or score.
4. `should-missing-test` missed the expected observation that success-only tests do not cover timeout retry and exhaustion. Instead, it reported a concrete risk of duplicate side effects when an arbitrary `send` callback times out after performing work. That is a separate, valid concern, but it does not satisfy the fixture's required test finding. Keep this as a substantive `SHOULD(Test)` miss for follow-up.

Under the beta's [risk-based checklist](../../docs/RELEASE_CHECKLIST.md), the observed misses do not show an undetected required `MUST` defect or false-positive finding, but the 25/29 strict result must not be presented as a perfect run. The missing test observation and classification differences should remain documented; acceptance for beta.2 still needs the maintainer's final sign-off alongside the other release gates.

These are single runs from one model, not an accuracy, invocation-rate, or false-positive-rate estimate. Manual grading can overlook unsupported details. The 29 runs used approximately 2,164,556 input tokens (1,784,832 cached) and 27,455 output tokens; token usage is not a quality measure.
