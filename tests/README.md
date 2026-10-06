# Behavioral Evaluations

[日本語](README.ja.md)

These evaluations test the behavior of the generated skill without requiring
an exact wording match. Each case provides a review request, repository
context, a patch, and observable expectations.

## Automated fixture validation

Run:

```sh
make test
```

This verifies the generated packages, release safeguards, package cleanup,
and the structure and internal consistency of every evaluation case. It does
not call an AI service.

Negative cases record a `false_positive_category` and a concrete invalid
finding under `must_not_report`; `must_report` and `prefixes` must be empty, and
`output` must be `no_findings`. The suite checks distinct traps—behavior-
preserving refactors, tool-enforced style, pre-existing defects, verified
language guarantees, and fully updated shared contracts—rather than treating
the number of `no_findings` cases as a measure of coverage. These are
purpose-built examples, not copied OSS code. The Java fixtures assume Java 17;
the Go fixtures assume Go 1.22 and the standard behavior of `len` on nil slices.
The fixture validator checks patch applicability. CI also runs
`make language-check`: after applying each patch in an isolated temporary
directory, it compiles Java 17 sources, runs `gofmt` and `go test` for Go 1.22
modules, and compiles Python source files. Where the patched Python fixture has
`test_*.py` files, it also runs their unit tests. This check can be run locally when
those runtimes are installed; Go dependency downloads are disabled. Neither
check establishes that an agent actually suppresses false positives.

The Batch 3 fixtures isolate documentation and test-coverage findings through
repository contracts. `must-stale-documentation` states that requiring
`API_TOKEN` is an approved change; its setup guide still describes anonymous
mode. `should-missing-test` documents an idempotent read and its retry contract,
and its patch preserves null and undefined rejection reasons. Its existing
test remains success-only. These fixture clarifications do not change the
required findings or retroactively change earlier evaluation results. Record
the revision when comparing runs.

The mixed-noise cases (`realistic-go-directory`, `realistic-java-fulfillment`,
`realistic-python-profile`, `realistic-python-retry-audit`, and
`realistic-python-notice-batch`) combine actionable changes with unrelated,
plausible changes. The retry/audit case requires following an interaction
between two changed files. The notice-batch case has a larger, nine-file patch
with 173 changed lines: pagination, audit events, display refactors, and tests
must be reviewed together. Its defect requires tracing how sent notices leave
the pending set between pages. These are relative fixture sizes, not a quality
threshold. Each `case.json` records the ecosystem, assumptions, expected
cross-file evidence, source, and limitations. All five are original synthetic
examples; no external OSS source is redistributed. Evaluate every
concern, including candidates listed under `must_not_report`, rather than
using diff size or the number of findings as a quality measure. The wider
suite also contains JavaScript cases, giving meaningful examples in four
languages overall.

## Opt-in local agent runs

Codex is the default. Use `--agent claude` to install the Claude package and run
its non-interactive static-only protocol. Claude authentication and the chosen
model must be available on the executing PC. The Codex-specific details below
do not imply equivalent Claude sandbox behavior; see the shared
[campaign protocol](EVALUATION_RUBRIC.md).

`make test` remains offline and never calls a model. To plan a Codex run without
using tokens, specify one or more case IDs (or explicitly select `--all`):

```sh
make eval EVAL_ARGS="--case negative-refactor --runs 2"
```

For a token-conscious first pass over the full suite, use the
[four-group batch plan](EVALUATION_BATCHES.md). It keeps each actual invocation
to at most two cases and requires an allowance check before the next batch.

The default language is English when a case has an English request, otherwise
Japanese. Use `--language en` or `--language ja` for an explicit language.
Add `--execute` to make the model calls. Each run uses a new temporary Git
repository containing the fixture baseline and the generated Codex Skill under
`.agents/skills/`. The workspace uses a neutral random `repo-` name and a
`Developer` baseline author; case IDs stay in the local result directory.
The patch remains an uncommitted, visible working-tree diff.
Codex runs in read-only, non-interactive, ephemeral mode. The runner does not
use the dangerous sandbox-bypass option. You can set `--model` and `--timeout`;
otherwise it uses the local CLI default model and a ten-minute timeout per run.
The default output is a newly created, private local directory outside this
repository; use `--output-dir` to choose a new directory elsewhere. The runner
rejects both explicit paths and a default temporary location (`TMPDIR`) that
resolve inside this repository, including symlinks, before creating output.
Choose an outside-repository `--output-dir` if your temporary location is rejected.
The runner prints its location. It saves `events.jsonl`, `answer.txt`, and `stderr.txt` for
each run, plus `summary.json`. Do not commit these raw files. Remove the local
directory when it is no longer needed, and check its contents before sharing.

Schema 2 summaries separate the requested model from any model reported in CLI
startup events or the stderr model header. If the CLI supplies no model
metadata, `observed_model` remains null; an explicitly requested model is not
claimed as observed. Summaries also record the repository revision, whole-tree
dirty state, relevant evaluation-input dirty state, and the installed Skill's
version, generated source hash, and actual package hash. Each run hashes the
package copied into that run's repository, including its references. Unrelated
untracked files may set `worktree_dirty` without setting
`evaluation_inputs_dirty`; the latter covers `src`, `dist`, `tests/cases`, and
the runner. A revision alone does not identify uncommitted inputs.

The checks accept Markdown headings, numbered lists, emphasis, and inline-code
titles. For negative cases, `negative_output_check` only means a nonempty answer
contains no recognized finding prefix. `explicit_no_findings` separately
records a best-effort phrase match for informational use only: it can miss
no-finding statements or match partial statements alongside real findings.
It is never a pass/fail signal. An unprefixed defect claim can therefore pass
the syntax check; it still needs human adjudication. Empty output is not a pass
and causes a nonzero runner exit. Old summaries and evaluations are not
rewritten by these changes.

Settings, selected cases, run count, available token usage, and Skill-read
evidence are recorded as well. A completed command can establish a read even
when a later command in the same shell fails, if its output contains the entire
installed Skill text. Partial output from a failed command is insufficient.
Raw review text is omitted from the summary. A file read alone does not prove
that the Skill influenced the review. The runner does **not** confirm
Skill invocation, score semantic matches, classify unexpected findings,
calculate finding-level metrics, or establish an accuracy rate. Review
the raw events and answer against `case.json`, record invocation separately,
and classify unexpected claims as valid, ambiguous, duplicate, or unsupported.
Use the manual record below for that judgment. Agent calls may consume
substantial tokens; the dry run and explicit `--execute` gate are intentional.
This is the first stage of [issue #24](https://github.com/akkie76/code-review-skills/issues/24),
not a replacement for the two-agent release evaluation.

## Manual agent evaluation

For issue #24's 80-point campaign, use the [adjudication rubric and scoring
workflow](EVALUATION_RUBRIC.md). `make eval-score` freezes the input manifest,
imports raw runner summaries into unreviewed local annotations, and aggregates
human-finalized judgments. `make eval` also accepts `--agent claude` for the
documented static-only protocol. Both commands are offline unless the runner
is explicitly given `--execute`; scoring never calls a model.

Run each case separately with both Codex and Claude Code:

1. Install the generated package for the agent under test.
2. Create an isolated temporary repository containing the files under the
   case's `repository/` directory.
3. Apply `change.diff` without committing it. If the patch adds files, use
   `git add -N` on those files so `git diff` includes them without staging
   their contents.
4. Submit each request in `case.json` without adding hints about the expected
   result.
5. Record whether every item under `expectations` was satisfied. Compare
   behavior and evidence, not sentence-level wording.
6. Repeat the case in a fresh conversation to avoid context from another
   fixture.

An evaluation passes only when all `must_report`, `must_not_report`, `prefixes`,
and `output` expectations hold. `may_report` is available only for non-negative
cases with `output: findings` and at least one `must_report` item; it records
valid but optional findings and does not replace a required finding. An optional
finding can appear as its own comment or as a substantiated point within a
required finding; a separate comment is not necessary to match `may_report`.
Neither placement excuses an unsupported claim, and an optional point cannot
make a missing `must_report` pass. Any other additional finding must
independently meet the skill's evidence requirements; otherwise record it as a
false positive. Record whether the Skill was actually invoked separately from
whether the output matched fixture expectations. An unassisted output match is
not a passing result for the Skill's review behavior.
Evaluate at least one negative case with both English and Japanese requests
in each agent; do not infer cross-language behavior from the fixture schema.

When using a blind grader, record the supplied files and any exclusions or
redactions (for example, removing `.claude/` or replacing agent names). Tell
the grader explicitly that the reviewer could see those excluded files.
A repository-scope claim that cannot be verified from the reduced grading
input is indeterminate, not automatically a false positive. Reconcile it
against a sanitized file manifest or relevant trace before adjudication;
do not treat absent grading evidence as proof that a claim was invented.

### Claude Code protocol

Use the generated Claude package from the same revision at
`.claude/skills/evidence-code-review/` in a fresh neutral workspace. Use a
neutral baseline author as in the Codex runner. The primary invocation mode is
`implicit`: submit only the request from `case.json`. For an implicit run with
no observed Skill invocation, optionally rerun explicitly with
`/evidence-code-review <request>` as a diagnostic. Record the mode and never
combine implicit and explicit runs into one score.

Record invocation evidence separately from output matches:

| Agent/mode | Evidence | Recorded value |
| --- | --- | --- |
| Claude, implicit | `Skill` tool call with `input.skill == "evidence-code-review"` | `confirmed`; otherwise `not_observed` |
| Claude, explicit | Explicit command plus Skill present in the init event's `skills` list | `by_construction`, not a directly observed invocation |
| Codex | Skill-file read in CLI events | `file_read_observed`; invocation remains `not_verified` |

Reads of `references/` support the record but do not independently establish
invocation. A Claude `not_observed` output match is not counted as a Skill pass.

The Claude CLI `2.1.281` evaluation used a non-interactive static-review
allowlist, as reported in [PR #44](https://github.com/akkie76/code-review-skills/pull/44#issuecomment-5996575210):

```sh
claude -p "<request from case.json>" \
  --setting-sources project --strict-mcp-config --no-session-persistence \
  --allowedTools "Read" "Grep" "Glob" "Skill" \
    "Bash(git diff:*)" "Bash(git status:*)" "Bash(git log:*)" "Bash(git show:*)" \
  --disallowedTools "Edit" "Write" "NotebookEdit" "WebFetch" "WebSearch" \
  --output-format stream-json --verbose
```

Select and record a model supported by the installed CLI and account. Record
the fixed permissions, denied verification attempts, and observed CLI metadata.
This Claude protocol does not allow fixture-code execution. Codex's read-only
sandbox restricts writes but can permit execution, including focused Python
checks; the two permission settings are not equivalent. Record this difference
when comparing results. `--setting-sources project` does not prove that
user-level Skills or memory were excluded; record that limitation or use a
separately isolated environment if the comparison requires it.

The public repository may contain dated, sanitized evaluation summaries.
Keep raw model transcripts outside the repository. Never commit machine paths,
private repository content, credentials, or unpublished correspondence.

Use [the manual evaluation record](RESULT_TEMPLATE.md) so product, model,
revision, language, and unexpected output are recorded consistently.
See the [2026-10-01 evaluation summary](results/2026-10-01.md) for the first
fresh-session Codex sample. The [2026-10-02 summary](results/2026-10-02.md)
records the Claude Code sample, including runs in which the Skill was not
invoked and issues found outside the fixture expectations.
The [2026-10-04 Codex release-candidate sample](results/2026-10-04.md)
records selected beta.2 runs and explicitly does not claim all-fixture coverage.
The [2026-10-04 Codex all-fixture evaluation](results/2026-10-04-codex-full.md)
records 29 fresh runs, a 25/29 strict fixture score, and the four adjudicated
deviations without converting them into passes.
The [2026-10-04 Claude Code release-candidate evaluation](results/2026-10-04-claude.md)
records all 28 fixtures, one additional Japanese negative run, and the two
prefix mismatches. The strict score remains 27/29 even if the beta release
decision accepts the documented deviations.
The [2026-10-06 Codex remaining-batch evaluation](results/2026-10-06-codex-remaining.md)
records 19 remaining cases at one revision (16/19 strict matches), plus a
successful targeted test-gap rerun after clarifying verification-risk findings.
The [2026-10-06 Claude Code report](https://github.com/akkie76/code-review-skills/pull/44#issuecomment-6007929541)
records 29 runs at `5fb7864`, after the Skill and fixture changes: 26/29 strict
matches and 29/29 confirmed Skill invocations. All required content was reported
(negative cases have no required findings); three prefix disagreements remain.
This is a maintainer-reported sample, not an independent verification or a
same-input repeat of the earlier revision. Its unchanged score does not establish
an accuracy improvement or regression. A claim initially flagged as unsupported
was adjudicated as a grading artifact because installed Skill files were excluded
from the grader's input.
It also preserves classification differences and the unvalidated delegation
boundary; it is not a full 28-case run at the final revision.

## Multi-agent evaluation boundary

The optional multi-agent decomposition guidance depends on whether the host
environment permits delegation and on how it exposes sub-agent execution. The
current `case.json` plus `change.diff` fixture format observes only the final
review output, so `make test` and the fixture count do not demonstrate that
delegation, independent sub-review validation, or final reconciliation
occurred.

Evaluate this guidance manually in a host that supports delegation, using a
diff with multiple independent concerns. In addition to the normal evaluation
record, confirm that:

- decomposition is skipped when its coordination cost is not justified;
- each assigned reviewer can inspect the complete diff and required context;
- each candidate finding is independently validated;
- a complex focused check is delegated only when its coordination cost is
  justified, and the verifier receives one exact claim, its evidence, the
  complete diff, and a question to confirm or refute;
- the final reviewer checks unowned interactions and reconciles duplicates,
  action levels, and viewpoints, and inspects any delegated verification
  evidence rather than accepting the verifier's conclusion by itself; and
- only reconciled findings appear in the final output.

When comparing single-reviewer and decomposed runs, use fresh sessions and the
same diff, request, model, and skill revision. Record both missed defects and
false positives; a higher finding count alone is not evidence of improvement.
