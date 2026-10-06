# Batching the Codex fixture evaluation

[日本語](EVALUATION_BATCHES.ja.md)

This is a primary-pass execution plan for the 28 fixtures in `tests/cases/`, not
a substitute for human adjudication. The [80-point campaign](EVALUATION_RUBRIC.md)
adds one Japanese negative and six predefined repeat sessions. It limits the size of each
opt-in CLI invocation so usage can be checked between batches. Do not launch
the four groups or all 28 fixtures in parallel.

## Before executing

1. Finish review of the evaluation runner and record the exact Skill commit,
   Codex CLI version, and an explicitly chosen model. Use the same Skill
   revision, model, and settings for comparable runs.
   Record dirty-state flags and the actual installed Skill package hash; a
   commit alone is insufficient when evaluation inputs have local changes.
2. Start with one run per case. Re-run only cases selected for variation checks
   after the first pass. Each batch contains at most two cases; run batches
   sequentially and check the remaining account allowance after each batch.
3. Dry-run the selected batch before adding `--execute`. The runner does not
   know the account's remaining allowance and cannot stop before a rate limit.
   Stop the sequence if a run fails to start, its output is incomplete, or the
   remaining allowance is insufficient for another run.
4. Keep raw traces and the directory-to-batch mapping locally, outside the
   repository. Before publishing any aggregate result, adjudicate each answer
   against `case.json` and remove sensitive or machine-specific details.

For example, the first batch can be previewed without a model call:

```sh
make eval EVAL_ARGS="--case negative-go-format --case negative-optional-label --runs 1"
```

After choosing a supported model, add `--model MODEL_ID --execute` to that
command. Replace `MODEL_ID` with the actual CLI model identifier; do not run
the placeholder verbatim. The runner prints the local output directory after
execution. Review its `summary.json`, each `answer.txt`, and the relevant
`case.json` before continuing. Record whether the Skill was invoked separately
from whether the answer met the fixture expectations. A successful file read or
prefix match alone is not a pass.

Use the [Claude Code protocol](README.md#claude-code-protocol) for the other
agent: implicit invocation first, explicit diagnostics separately, neutral
workspace names, fixed permissions, and separate invocation evidence. Codex
read-only execution and Claude's static-only allowlist are different settings.

## Four groups, four small batches each

Run batches from top to bottom. The groups become progressively more demanding;
patch length is only a rough planning aid and does not predict token usage.
Every fixture appears once in this first-pass plan.

| Group | Batch | Cases |
| --- | --- | --- |
| 1 — calibration | 1 | `negative-go-format`, `negative-optional-label` |
| 1 — calibration | 2 | `nits-misspelled-local`, `nits-project-style` |
| 1 — calibration | 3 | `must-stale-documentation`, `should-missing-test` |
| 1 — calibration | 4 | `positive-pagination` |
| 2 — contracts and languages | 1 | `negative-go-runtime`, `negative-java-contract` |
| 2 — contracts and languages | 2 | `must-focused-risk-variant`, `nits-change-created-dead-code` |
| 2 — contracts and languages | 3 | `must-existing-consumer`, `realistic-go-directory` |
| 2 — contracts and languages | 4 | `realistic-java-fulfillment` |
| 3 — cross-file behavior | 1 | `negative-preexisting-defect`, `instruction-boundary` |
| 3 — cross-file behavior | 2 | `must-same-diff-contract`, `must-shared-handler-variant` |
| 3 — cross-file behavior | 3 | `should-ineffective-regression-test`, `realistic-python-profile` |
| 3 — cross-file behavior | 4 | `realistic-python-retry-audit` |
| 4 — evidence and large diff | 1 | `negative-refactor`, `better-simplify-guard` |
| 4 — evidence and large diff | 2 | `must-multi-agent-reconciliation`, `must-multi-concern-depth` |
| 4 — evidence and large diff | 3 | `must-verified-supporting-evidence`, `should-layer-boundary` |
| 4 — evidence and large diff | 4 | `realistic-python-notice-batch` |

The previous single `must-stale-documentation` smoke run tested the runner and
does not replace its first-pass run after the evaluation revision and model are
fixed. After each group, record completed case IDs, local output directories,
agent errors, token usage, and pending human judgments. Compare findings, not
only prefix strings, before deciding which cases need repeated runs. The
existing [manual evaluation record](RESULT_TEMPLATE.md) remains useful for notes;
use the [local adjudication workflow](EVALUATION_RUBRIC.md) for finding-level aggregation.
