# Multi-Agent Decomposition (Optional)

Use this guidance only when the reviewing environment supports delegation to
independent sub-agents and the applicable user, repository, and platform
instructions permit it. The core workflow remains complete for a single
reviewer.

Decomposition can improve coverage when a diff is large or contains enough
independent concerns that one pass would divide attention too thinly. It also
adds coordination cost. Keep a single reviewer when the concern map is short,
the interactions are straightforward, or delegation would not provide each
reviewer with the context needed to validate findings.

## Decide whether to decompose

Consider decomposition when one or more of these conditions holds:

- The concern map contains several largely independent concerns.
- The diff spans enough distinct files, functions, or subsystems that one pass
  is unlikely to give each concern sufficient depth.
- The diff includes substantive changes across multiple surfaces, such as core
  behavior, tests, and documentation or types, and one pass is unlikely to
  examine each surface adequately.

Diff size alone is not decisive. A large, coherent change with tightly coupled
behavior may be safer and more efficient to review as one concern.

## Choose a decomposition axis

Use either axis, or combine them when the diff justifies the additional cost.

### By concern

Assign one reviewer to each concern, or to a small cluster of related concerns,
from step 2's change map. Give every reviewer the complete diff and access to
relevant surrounding files, while making its primary responsibility explicit.
Each reviewer applies steps 3 through 6 of the core workflow to that scope and
notes interactions or uncertainties that require integration.

Prefer concern-based decomposition for functional behavior. `Functionality`
is too broad to be a useful assignment for one reviewer on a large diff.

### By viewpoint

Use viewpoint-based assignments when a distinct review surface would otherwise
receive insufficient attention. `Test` and `Document` can be separate
assignments. The structurally lighter viewpoints (`Design`, `Simplicity`,
`Naming`, and `Style`) can be grouped unless the diff gives one of them enough
substance to justify a focused review.

A viewpoint narrows the reviewer's primary responsibility, not its evidence
standard. If a reviewer discovers a possible defect whose primary impact lies
outside its assignment, it should preserve the evidence for integration rather
than force the finding into the assigned viewpoint.

## Require independent validation

Each sub-review must satisfy step 5's validation requirements and step 6's
false-positive controls. A sub-agent's conclusion is a candidate finding, not
additional evidence merely because another agent produced it.

Do not split the review so narrowly that a reviewer cannot inspect the callers,
contracts, tests, or surrounding implementation needed to establish behavior.
If required context cannot be shared, use a single reviewer or broaden the
assignment.

## Integrate the sub-reviews

One final reviewer must reconcile all results before applying the output
contract:

1. Read every candidate finding, the complete diff, and the concern map.
2. Confirm that the cited evidence and recorded verification support each
   candidate's trigger, impact, change attribution, and relevant cross-concern
   or cross-viewpoint interactions. Do not mechanically repeat every
   sub-review's verification. Re-run a focused check when its result is
   missing, cannot be inspected, conflicts with another result, materially
   affects classification, or warrants independent confirmation because of
   the potential impact.
3. Merge candidates that share one root cause. Reassess the action level and
   viewpoint from the complete evidence; do not automatically preserve either
   the highest or the most frequently proposed severity.
4. Check interactions that no scoped reviewer owned. This includes whether
   changed tests that are intended to establish behavior added or relied on by
   the diff would fail to detect a relevant defect. Report a `Test` finding
   only when that verification gap is attributable to the reviewed change,
   even if the underlying defect itself predates the diff.
5. Drop duplicates, superseded interpretations, unsupported claims, and
   lower-confidence variants of a validated finding.
6. Apply the output contract only to the reconciled findings.

During step 2, when a focused check is complex enough to compete with the
reconciliation work, the final reviewer may delegate that check to a fresh
verifier if the environment supports it and the coordination cost is justified.
Give the verifier the complete diff, one exact candidate claim, its cited
evidence, and the question to confirm or refute. Do not mechanically delegate
every unresolved candidate or a check that is simpler to perform inline. The
final reviewer must inspect the returned evidence and recorded result before
using it; the verifier's conclusion is not evidence by itself.

The final reviewer owns the result. Delegation increases investigation
coverage but does not relax evidence requirements or transfer responsibility
for false positives to the sub-agents.
