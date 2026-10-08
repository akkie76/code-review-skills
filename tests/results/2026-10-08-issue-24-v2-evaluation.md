# Issue #24 v2 evaluation results — 2026-10-08

[日本語](2026-10-08-issue-24-v2-evaluation.ja.md)

This report records the completed, human-adjudicated v2 evaluation campaign for the generated
Code Review Skill packages. It uses versioned synthetic fixtures and a strict 80% primary-case
threshold. It does not claim real-world review accuracy.

## Campaign and evaluated artifacts

- Campaign policy: `issue-24-human-adjudication-v2`.
- The final dataset contains 29 primary cases and six predefined repeats per agent (35 runs per
  agent; 70 records total), but it is a replacement campaign rather than one uninterrupted set.
- In the first v2 campaign, Codex `realistic-python-notice-batch` timed out at 300 seconds after a
  transient connection failure. It was not retried under that campaign. A replacement campaign
  was initialized with the same revision and settings, and all 35 Codex runs were executed again.
- All 35 Claude runs from the first campaign were reused unchanged: the revision, settings, model,
  and package hashes matched, with no recorded drift. The maintainer approved this reuse; the
  frozen rubric does not define a general reuse rule. See the [campaign history](https://github.com/akkie76/code-review-skills/issues/24#issuecomment-6040546937).
- Acceptance threshold: at least 80% of primary cases, or 24 of 29, for each agent. Repeats are
  diagnostic and are not pooled into the primary score.
- Frozen source revision: `05307082490bfd8416a60ce511faadf02998e5c4`.
- The generated packages retain the `v0.1.0-beta.2` version marker, but their contents include
  post-release changes from PRs #44 and #45. The marker alone does not identify the evaluated
  content; use the source and package hashes below.
- Shared generated-source SHA-256: `104fe8438c7e44011ebd3f748c701550eccdbec8d36665089a604becf4e8f719`.
- Shared package SHA-256: `cfb3047f846a8949d23572e0fb5dae69f2e69bbd03bdd7d462507d03153a3b3b`.
- Fixture-set SHA-256: `4de4361ee1fd0bbc2e96fb480b397acbcb21f9ba15e340eaaae8f85425459c37`.
- Codex CLI `0.160.0`; requested model `gpt-6.1-sol`. Run metadata did not report an observed
  model identifier. Skill-file reads were observed, which is weaker evidence than a confirmed
  invocation.
- Claude Code `2.1.281`; model `claude-opus-5-5`. A successful `Skill` tool result was observed in
  all 35 runs.

## Usage, permissions, and isolation

- Codex usage across 35 runs: 2,954,159 input tokens (2,469,504 cached) and 20,665 output tokens.
  Cost was unavailable.
- Claude usage across 35 runs: 328 uncached input tokens, 648,106 cache-creation input tokens,
  1,620,312 cache-read input tokens, and 50,455 output tokens. The recorded estimated cost was
  USD 6.52.
- Codex used an ephemeral read-only sandbox with user configuration ignored and approval disabled.
  Read-only limits filesystem writes; it does not itself establish that command execution was
  impossible. Actual model identity and Skill invocation were not independently confirmed.
- Claude used a static permission allowlist with fixture-code execution disabled and strict MCP
  configuration. Some attempted commands were denied and recorded as `permission_denied`. Project
  setting sources were selected, but user Skills/memory and managed settings could still be
  visible; this was not full host isolation.
- The agents therefore ran with different host permission and isolation configurations.

## Results

| Agent | Primary passes | Score | Repeat passes | Complete | Meets threshold |
| --- | ---: | ---: | ---: | --- | --- |
| Codex | 27/29 | 93.10% | 6/6 | Yes | Yes |
| Claude Code | 26/29 | 89.66% | 5/6 | Yes | Yes |

The frozen scorer reports the campaign as accepted: both agents exceed the 80% threshold. The
case-level strict mismatches remain in the results:

- Codex: `nits-project-style` used `MUST(Style)` where the expectation was `NITS(Style)`;
  `better-simplify-guard` proposed a valid test improvement but omitted the required
  `BETTER(Simplicity)` finding.
- Claude Code: `should-ineffective-regression-test` detected the test gap but used `MUST(Test)`
  instead of the expected `SHOULD(Test)`. The maintainer considered this practically tolerable;
  the frozen scorer still counts the prefix mismatch as a failed case. In
  `must-multi-agent-reconciliation`, the required defects were found but the answer included an
  incorrect statement about baseline behavior. In `must-multi-concern-depth`, an additional
  whitespace-nickname concern lacked a project requirement establishing it as a defect, and the
  answer also misstated baseline behavior.

These numerical outcomes follow the frozen strict rubric. The maintainer's practical judgments,
including tolerating the `SHOULD(Test)`/`MUST(Test)` difference, are explanatory context and do not
override the scorer's case outcomes.

The strict primary outcome for each case is:

| Case | Request language | Codex | Claude Code |
| --- | --- | --- | --- |
| `better-simplify-guard` | en | Fail | Pass |
| `instruction-boundary` | en | Pass | Pass |
| `must-existing-consumer` | en | Pass | Pass |
| `must-focused-risk-variant` | en | Pass | Pass |
| `must-multi-agent-reconciliation` | en | Pass | Fail |
| `must-multi-concern-depth` | en | Pass | Fail |
| `must-same-diff-contract` | en | Pass | Pass |
| `must-shared-handler-variant` | en | Pass | Pass |
| `must-stale-documentation` | ja | Pass | Pass |
| `must-verified-supporting-evidence` | en | Pass | Pass |
| `negative-go-format` | en | Pass | Pass |
| `negative-go-runtime` | en | Pass | Pass |
| `negative-java-contract` | en | Pass | Pass |
| `negative-optional-label` | en | Pass | Pass |
| `negative-preexisting-defect` | en | Pass | Pass |
| `negative-refactor` | en | Pass | Pass |
| `negative-refactor` | ja | Pass | Pass |
| `nits-change-created-dead-code` | en | Pass | Pass |
| `nits-misspelled-local` | ja | Pass | Pass |
| `nits-project-style` | en | Fail | Pass |
| `positive-pagination` | en | Pass | Pass |
| `realistic-go-directory` | en | Pass | Pass |
| `realistic-java-fulfillment` | en | Pass | Pass |
| `realistic-python-notice-batch` | en | Pass | Pass |
| `realistic-python-profile` | en | Pass | Pass |
| `realistic-python-retry-audit` | en | Pass | Pass |
| `should-ineffective-regression-test` | en | Pass | Fail |
| `should-layer-boundary` | en | Pass | Pass |
| `should-missing-test` | en | Pass | Pass |

Finding-level counts below cover the 29 primary cases only. A required item is counted once per
case, and negatives do not add required detections.

| Agent | Required detected (TP) | Required missed (FN) | Unsupported findings (FP) | Valid additional | Optional | Duplicates | Unsupported supporting claims | Prohibited matches | Required prefix mismatches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex | 24 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 |
| Claude Code | 25 | 0 | 1 | 2 | 1 | 0 | 2 | 0 | 1 |

## Repeat observations

| Case | Codex primary → repeat | Claude Code primary → repeat |
| --- | --- | --- |
| `nits-misspelled-local` | Pass → Pass | Pass → Pass |
| `must-stale-documentation` | Pass → Pass | Pass → Pass |
| `should-missing-test` | Pass → Pass | Pass → Pass |
| `nits-change-created-dead-code` | Pass → Pass | Pass → Fail |
| `should-layer-boundary` | Pass → Pass | Pass → Pass |
| `must-verified-supporting-evidence` | Pass → Pass | Pass → Pass |

Codex had no outcome or classification changes. Claude was stable on five pairs. For
`nits-change-created-dead-code`, the repeat cited line 7 rather than the changed line 6. The
maintainer considered this one-line location error practically minor; under the frozen rubric it
remains an unsupported detail, so the repeat is recorded as failed. Repeats are diagnostic and
do not change either primary score. Six selected pairs are not enough to estimate general
repeatability.

## Interpretation and limitations

- These are results on a small, versioned synthetic fixture set, not a measurement of production
  review accuracy, precision, recall, or defect-prevention rate.
- A maintainer adjudicated the records with assistant-assisted analysis. This was not blind,
  independent grading; reviewer or model-family bias remains possible.
- Codex's model identity was not independently reported by run metadata, and file-read evidence
  does not prove that the Skill was invoked or caused the result. Claude's successful Skill call
  was observed, but this campaign still does not isolate the Skill's causal effect.
- The scores apply only to the recorded model/CLI versions, Skill package, frozen rubric, and
  fixture set. Model behavior and results may differ with other versions or project context.
- Raw answers, traces, grading contexts, and machine-local paths are intentionally excluded.

Both agents meet the campaign's agreed 80% threshold. This is evidence for the beta evaluation
criterion, not a guarantee of review quality or approval for a stable release.
