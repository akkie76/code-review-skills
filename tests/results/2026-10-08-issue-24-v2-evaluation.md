# Issue #24 v2 evaluation results — 2026-10-08

[日本語](2026-10-08-issue-24-v2-evaluation.ja.md)

This report records the completed, human-adjudicated v2 evaluation campaign for the generated
Code Review Skill packages. It uses versioned synthetic fixtures and a strict 80% primary-case
threshold. It does not claim real-world review accuracy.

## Campaign and evaluated artifacts

- Campaign policy: `issue-24-human-adjudication-v2`.
- Each agent completed 29 primary cases and six predefined repeats (35 runs per agent; 70 total).
- Acceptance threshold: at least 80% of primary cases, or 24 of 29, for each agent. Repeats are
  diagnostic and are not pooled into the primary score.
- Frozen source revision: `05307082490bfd8416a60ce511faadf02998e5c4`.
- Skill version: `v0.1.0-beta.2` for both packages.
- Shared generated-source SHA-256: `104fe8438c7e44011ebd3f748c701550eccdbec8d36665089a604becf4e8f719`.
- Shared package SHA-256: `cfb3047f846a8949d23572e0fb5dae69f2e69bbd03bdd7d462507d03153a3b3b`.
- Fixture-set SHA-256: `4de4361ee1fd0bbc2e96fb480b397acbcb21f9ba15e340eaaae8f85425459c37`.
- Codex CLI `0.160.0`; requested model `gpt-6.1-sol`. Run metadata did not report an observed
  model identifier. Skill-file reads were observed, which is weaker evidence than a confirmed
  invocation.
- Claude Code `2.1.281`; model `claude-opus-5-5`. A successful `Skill` tool result was observed in
  all 35 runs.

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

## Repeat observations

Codex passed all six primary/repeat pairs with no outcome or classification changes. Claude was
stable on five pairs. For `nits-change-created-dead-code`, the primary run passed and the repeat
failed because it cited line 7 rather than the changed line 6. The maintainer considered the
one-line location error practically minor; under the frozen rubric it remains an unsupported
detail, so this repeat is recorded as failed. Repeats are diagnostic and do not change either
primary score. Six selected pairs are not enough to estimate general repeatability.

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
