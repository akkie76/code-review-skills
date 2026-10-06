# Codex remaining-batch evaluation: 2026-10-06

[日本語](2026-10-06-codex-remaining.ja.md)

This records 19 cases in sequential batches 6–16 of the [batch plan](../EVALUATION_BATCHES.md), plus one targeted rerun of `should-missing-test`. All 20 runs completed. The remaining cases matched their strict fixture expectations in 16/19 runs; the targeted test-gap rerun also matched. These are observed fixture matches, not an estimate of general review accuracy.

## Conditions and change

- Source: `b2a1ea2ac833f34aa64638a44e5f0b89d686c5ab`.
- Agent: Codex CLI `0.159.2`, model `gpt-6.1-sol`.
- One fresh English session per case, isolated repository, visible uncommitted fixture diff, read-only, ephemeral, user configuration ignored, 300-second timeout.
- At most two cases per invocation; allowance checked between batches.
- The shared workflow now admits verified quality and verification risks alongside runtime defects. The test criteria explain that inspected tests failing to detect a concrete regression can justify `SHOULD(Test)` even when the implementation appears correct. Inability to execute tests alone does not establish missing coverage. Both generated packages were rebuilt.
- The reviewer requests and expected findings were not changed for these runs. Earlier Batch 3 fixture clarification remains part of the recorded source revision.

The assistant compared final answers and relevant execution records with `must_report`, `must_not_report`, `prefixes`, and `output`. This was not blind or independently graded. The raw runner's semantic judgment remains pending; the manual observations below are recorded separately.

## Remaining cases

| Batch | Case | Strict fixture match |
| --- | --- | --- |
| 6 | `must-focused-risk-variant` | Pass |
| 6 | `nits-change-created-dead-code` | Prefix mismatch: `BETTER(Simplicity)` instead of `NITS(Simplicity)` |
| 7 | `must-existing-consumer` | Pass |
| 7 | `realistic-go-directory` | Pass |
| 8 | `realistic-java-fulfillment` | Pass; both required defects reported |
| 9 | `negative-preexisting-defect` | Pass by manual output comparison |
| 9 | `instruction-boundary` | Pass; reviewed without executing the fixture |
| 10 | `must-same-diff-contract` | Pass |
| 10 | `must-shared-handler-variant` | Pass |
| 11 | `should-ineffective-regression-test` | Pass |
| 11 | `realistic-python-profile` | Pass; both required defects reported |
| 12 | `realistic-python-retry-audit` | Pass |
| 13 | `negative-refactor` | Pass by manual output comparison |
| 13 | `better-simplify-guard` | Required `BETTER(Simplicity)` suggestion omitted |
| 14 | `must-multi-agent-reconciliation` | Final output matches; actual delegation not validated |
| 14 | `must-multi-concern-depth` | Pass |
| 15 | `must-verified-supporting-evidence` | Pass |
| 15 | `should-layer-boundary` | Prefix mismatch: `MUST(Design)` instead of `SHOULD(Design)` |
| 16 | `realistic-python-notice-batch` | Pass |

## Adjudication and targeted rerun

1. `nits-change-created-dead-code` correctly identified the private helper left unused by the change and described removal as optional, but used `BETTER`. Keep the strict prefix mismatch; there was no missed functional defect.
2. `better-simplify-guard` omitted the optional suggestion to name the repeated active-admin condition. It instead reported a concrete `SHOULD(Test)` gap for the newly added authorization branches, proposing role and active-state boundary checks. Repository inspection confirmed that the fixture contains no tests. This is a valid additional verification-risk finding, but it does not satisfy the required simplification finding.
3. `should-layer-boundary` correctly found the domain-to-UI dependency, but classified the explicit repository rule that domain files **must not** depend on UI as `MUST`. Keep the strict mismatch; do not alter the fixture expectation to fit this run.

After the Skill clarification, the separate `should-missing-test` rerun produced the required `SHOULD(Test)` for timeout recovery, attempt exhaustion, and preservation of rejection reasons. `should-ineffective-regression-test` also produced `SHOULD(Test)` for an assertion that would pass after reverting the intended behavior. These observations support the clarification, but one run per case does not establish causality or reliable repeatability. No required `MUST(Functionality)` defect was missed in the remaining cases.

## Limits and usage

- A successful Skill-file read was observed in all 20 runs; a dedicated Skill-invocation event was not available.
- The multi-agent case reported failed sub-agent initialization. Its final findings matched, but this is not a successful test of independent delegation and reconciliation.
- Negative answers used forms such as `No actionable findings` followed by explanation, or `No actionable defects found`. The runner's narrow no-finding expression check returned false; manual reading confirmed no formal findings. Raw summaries were not rewritten.
- Node.js and Go were unavailable to several agent checks, and Java validation remained static. Selected Python checks ran. The profile reproduction used postponed annotation evaluation because the available Python was older than the fixture's intended runtime; this is a focused behavior check, not a full target-runtime test.
- The large notice case's three existing tests passed, and a separate five-notice reproduction demonstrated skipped notices. Passing the existing tests alone would not establish correctness.
- Earlier batches used other revisions. This report is not a complete 28-case run on the final revision, and earlier outcomes were not retroactively rescored.
- Total for 20 runs: 1,619,760 input tokens (1,383,296 cached), 11,898 output tokens. Raw transcripts remain outside the repository; CLI monetary cost was unavailable.
- `make release-check` passed: 19 tooling tests and 28 fixture structures. The skill-creator standalone validator could not run because PyYAML was unavailable; repository package validation passed.

The prior Document case's `SHOULD(Document)` versus expected `MUST(Document)` remains a separate classification question. This report and the test-gap improvement do not resolve it or imply release acceptance.
