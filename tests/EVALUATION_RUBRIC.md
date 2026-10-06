# Human-adjudicated evaluation

[日本語](EVALUATION_RUBRIC.ja.md)

This closes the gap between the syntax-only runner and issue #24's finding-level
evaluation. It does not change Skill instructions, fixtures, or historical scores.
The maintainer specified **80 points before this campaign's execution**.

## Frozen scope and acceptance

`EVALUATION_PLAN.json` fixes the rule. Each agent has 29 primary sessions:
one per current fixture in its default language, plus `negative-refactor` in
Japanese. One additional session for each of six predetermined cases supplies
variation evidence: typo, stale documentation, missing tests, change-created
dead code, layer boundary, and verified supporting evidence. That is 35 fresh
sessions per agent, run sequentially in batches of at most two.

Primary score = 100 × strictly passing primary sessions / planned primary
sessions. Each agent must score at least 80 independently (24/29 today).
Do not pool agents, round a below-threshold score up, drop failures, select the
best retry, or add repeats to the primary denominator. All planned primary and
repeat sessions must be completed and human-adjudicated before acceptance.
Repeat pass counts and classification changes are diagnostic, not another
threshold. This small targeted sample is not an estimate of population variance.

Use the same clean source revision and fixture hash for both agents. Freeze
explicit model IDs and installed package hashes before starting. The package
hashes may differ by agent, but generated source hashes must agree. Each agent
must retain the same CLI version and fixed permission protocol throughout the
campaign. Record runtime availability, denied checks and isolation limitations
in the local annotations and the sanitized report. Codex read-only can permit
execution; Claude uses a static-only tool allowlist. The comparison is therefore
between documented host configurations, not identical execution capabilities.
Changing source, fixtures, models or conditions requires a new campaign.

An 80-point result is an evaluation acceptance decision, **not automatic release
approval**. Apply the existing release checklist to missed security/data-loss
defects, false positives and other unresolved risks; a high score does not make
such problems harmless or close #35 automatically.

## Adjudication rules

Read the raw answer, the applied diff, repository contracts, inspected tests
and relevant execution trace. Expected items use zero-based indices in the
frozen case expectations. Match behavior and evidence, not sentence wording.

- `required`: substantiates one or more `must_report` expectations; record their
  indices and the actual prefix. Do not count the same expectation twice.
- `optional`: substantiated `may_report` item. It may be an independent comment
  or a supported point within a required comment; record its optional index.
- `valid_additional`: independently justified finding not in the expected set.
  It is not automatically a false positive and cannot replace a required item.
- `duplicate`: same cause/trigger/impact as another finding in that answer;
  point to a non-duplicate ID. Do not inflate detection or false-positive counts.
- `unsupported`: insufficient evidence, invented behavior, pre-existing defect
  outside scope, or preference presented as a defect. Count a formal finding
  separately from an unsupported supporting sentence within a valid finding.
- `ambiguous`: evidence or grading inputs are insufficient to decide. Leave
  pending until adjudicated; do not silently classify it as valid or unsupported.

Record prohibited statements in `forbidden_matches`, including unsupported
supporting details listed under `must_not_report`. Record other factual supporting
claims separately. Explain exclusions/redactions in blind-grading inputs and
reconcile missing files with a sanitized manifest/trace before classifying a claim.

A strict case pass requires all required items, expected prefixes, the requested
output type, a compliant output contract, no prohibited statement, and no
unsupported finding or supporting claim. Prefix differences remain failures,
even if the content was useful. Valid extra/optional comments do not penalize a
positive case. A negative case requires a meaningful answer with no finding,
including unprefixed defect claims; regex `explicit_no_findings` is not a judge.

Invocation evidence stays separate. Claude requires a confirmed `Skill` tool
call; init-list presence alone is insufficient. Codex can currently observe only
a Skill-file read. The campaign accepts `file_read_observed` as limited access
evidence for scoring, **not confirmed invocation or causal proof**. Do not count
an output with no observed Skill access as a Skill pass.

`judgments.json` starts unreviewed. A human must inspect each record, supply a
reviewer identifier, set `method: human`, and explicitly finalize it. Agent-assisted
drafts use `method: agent_assisted` and remain pending; never impersonate a human
or silently approve draft labels. Do not edit imported execution metadata.

## Finding-level metrics

For finalized primary judgments only, report:

- Required detected (TP): distinct required expectation indices matched per run.
- Required missed (FN): required expectations minus detected expectations.
- Unsupported findings (FP): non-duplicate formal findings judged unsupported.
- Valid additional, optional and duplicate comments: separate counts.
- Unsupported supporting claims and prohibited matches: separate counts;
  a supporting-detail error is not an additional formal FP.

These are counts on versioned synthetic expectations, not real-world precision
or recall. Negatives have zero required expectations and do not inflate TP.
Case score is not finding-level precision. Partial counts must state that some
judgments remain pending. Variation compares the primary and fixed repeat for
each selected case, reporting 0/2, 1/2 or 2/2 passes and classification changes.
Human reviewers can disagree or miss claims; automated judges can favor their
own model family, wording or verbosity. An independent review is useful, but
the workflow does not claim independence when the maintainer reviews it.

## Local workflow

Commit and review the tooling first; no source changes after freezing. Use new
directories outside the repository, and never commit raw files or annotations.

```sh
make eval-score SCORE_ARGS="init --campaign /tmp/evidence-review-campaign --codex-model gpt-6.1-sol --claude-model claude-opus-5-5"
make eval EVAL_ARGS="--case negative-go-format --case negative-optional-label --model gpt-6.1-sol --timeout 300 --execute --output-dir /tmp/evidence-review-codex-batch01"
make eval-score SCORE_ARGS="import --campaign /tmp/evidence-review-campaign --summary /tmp/evidence-review-codex-batch01/summary.json --phase primary"
make eval-score SCORE_ARGS="score --campaign /tmp/evidence-review-campaign"
```

Use a separate output directory for every batch. Follow `EVALUATION_BATCHES.md`
for the primary pass, add the Japanese negative, then run the six frozen repeat
cases once using `--phase repeat` when importing. Stop after an error, incomplete
output or insufficient allowance; do not automatically substitute a successful
retry. If a technical rerun is needed, retain the failed record and explicitly
start a replacement campaign rather than cherry-picking.

On the authenticated Claude PC, check out the frozen commit and use the same
runner with `--agent claude --model claude-opus-5-5`. Confirm model availability
before freezing; do not substitute an alias or another model mid-campaign.
Run with the fixture request only, not an explicit Skill command. Transfer the
`summary.json` and referenced raw run directories privately to the scoring PC,
or use a copy of the same frozen campaign. Import locally after transfer so
absolute answer paths are generated for that PC. The tool rejects mismatched
revision, model, fixture/package hashes, dirty inputs, permissions and duplicate
entries. Existing annotations are never overwritten by import.

The aggregate excludes raw prose, annotation notes, reviewer names and local
paths. Still inspect it before publication; never publish source annotations.
`score` exits 0 only if both agents are complete and meet 80, 1 if pending or
below threshold, and 2 on invalid input. A missing/pending score is null, not 0
accuracy or a passing result. Preserve failed expectations instead of rewriting
them after seeing the result.

The design combines explicit metrics with human judgment, consistent with
[OpenAI's evaluation guide](https://developers.openai.com/api/docs/guides/evaluation-best-practices).
Claude CLI flags and permission semantics were checked against the
[CLI reference](https://code.claude.com/docs/en/cli-reference) and
[permission reference](https://code.claude.com/docs/en/permissions).
