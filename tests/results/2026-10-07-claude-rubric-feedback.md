# Claude fixed-revision runs and rubric feedback — 2026-10-07

[日本語](2026-10-07-claude-rubric-feedback.ja.md)

Source: the maintainer's [Run A/B report](https://github.com/akkie76/code-review-skills/pull/45#issuecomment-6029132765).
Private artifacts were not independently inspected here. This record supersedes
neither the original judgments nor their rules.

## Reported observations (old policy)

- Run A used a dedicated clone at `b45962613738c8caab8c321f2dec6b0744dc6668`;
  HEAD/cleanliness were checked per batch. Claude Code `2.1.281`, requested and
  reported model `claude-opus-5-5`, static-only runner, 35/35 completed.
- All 20 summaries imported with the old scorer. Official Claude score remains
  null and completion false because no judgment is human-finalized.
- Run B separately repeated all 35 sessions for diagnosis; it was not imported.
- Agent-assisted drafts: Run A 21/29 strict primary passes with one pending,
  repeats 2/6; Run B 17/29 with seven pending, repeats 3/6. Both report 25/25
  required items detected, with the same case outcome in 26/35 sessions.
- Three stable classification differences: setup `SHOULD` instead of `MUST`,
  unused helper `BETTER` instead of `NITS`, layer boundary `MUST` instead of `SHOULD`.
- Questions and an explicitly excluded pre-existing defect were graded differently
  or counted as findings. A wrong function name in a repeat is a #35-type concern.
- Run A reported 18 denied verification attempts, no runtime installation and
  imperfect host isolation. Approximate use: 0.58M cache-creation, 1.48M cache-read,
  49K output tokens, USD 5.93. These are reported host limits/cost, not quality metrics.
- Both runs' 35/35 `confirmed` labels use the old request-only evidence parser,
  not the newer successful-tool-result check. No new confirmation is inferred.

## Adopted for new campaigns only

The v2 rubric separates grounded material questions and accurate non-actionable
scope notes from findings. It still rejects unsupported factual premises,
including in hedged sentences; "only proven false claims fail" is not adopted.
Qualified prohibited statements are matched semantically, not by keyword mention.

The Skill's evidence checks now cover questions and summaries. Graders receive a
private file/hash inventory including excluded Git and Skill infrastructure.
Existence alone is not proof of behavior. The scorer retains and verifies the
context hash without exporting its contents.

Classification is calibrated by principle: setup failure remains `MUST(Document)`;
local removal of a small unused private helper remains `NITS(Simplicity)`.
The authoritative mandatory dependency rule warrants `MUST(Design)`, so only
that fixture's prefix is corrected; its historical ID is retained.

No old scores/annotations are rewritten and no estimated 83–90-point improvement
is presented as measured. The predeclared 29-primary + six-repeat plan and 80-point
threshold remain unchanged. Two samples for every case require agreement on cost
and aggregation before execution; diagnostic Run B is not cherry-picked into Run A.

## Remaining

Review these v2 decisions, freeze a new common revision, explicitly authorize and
collect comparable Codex/Claude sessions, then human-finalize and aggregate.
Accuracy improvement and #35 recurrence remain unverified. No model reruns,
merges, releases or issue closure were performed for this feedback fix.
