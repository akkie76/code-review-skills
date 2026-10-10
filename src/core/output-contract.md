# Review Output Contract

Apply this contract after investigating and validating candidate comments. It
defines how to communicate review results; it does not lower the evidence
required to report them.

## Select the output language

Write the review in the language explicitly requested by the user. If the user
does not specify a language, follow authoritative repository instructions. If
neither specifies a language, use the language of the user's review request.

Keep source identifiers, API names, command names, paths, and error messages in
their original form unless translating them is necessary for comprehension. Do
not produce duplicate English and Japanese reviews unless requested.

## Assign the action level

Every review comment starts with one of these action levels. The level tells the
author what response is expected; it is not reviewer confidence or fix effort.

### MUST

Use `MUST` when the change has a demonstrated defect, security failure,
contract violation, data-integrity risk, or other problem that must be resolved
before merge. State the failing behavior and why merge should be blocked.
A new violation of an authoritative non-negotiable repository rule remains
`MUST` even without a runtime failure. Incorrect setup instructions that make
the documented installation or startup fail are also `MUST(Document)`.

Do not use `MUST` for personal preferences, uncertain concerns, or an optional
design alternative. Ask a question when missing context prevents proving the
problem.

### SHOULD

Use `SHOULD` when a concrete quality, maintainability, verification, or
operational risk should normally be resolved, but the team can consciously
defer it without making the current change incorrect. Explain the cost of
deferral. When deferring, recommend recording the follow-up rather than leaving
the outcome implicit. An architectural recommendation that is explicitly deferrable
can be `SHOULD(Design)`; do not silently reinterpret a mandatory rule as advice.

### BETTER

Use `BETTER` for an optional alternative that provides a specific, explainable
benefit. Make clear that the current implementation can still be accepted. Do
not present subjective taste as an improvement.

### NITS

Use `NITS` for a minor, non-blocking correction such as a typo, misleading
local wording, or a clearly established convention that automation does not
cover. Report an unambiguous spelling error introduced on changed lines as a
`NITS` finding even when it does not affect runtime behavior; for an identifier,
use `NITS(Naming)`. Describe only its proportionate readability, searchability,
or presentation impact, and do not make it sound like a merge blocker. If the
typo changes an API or behavior, classify the actual impact instead. Use NITS
sparingly: do not report valid but unfamiliar names, personal naming or wording
preferences, pre-existing typos, or formatter output, and do not manufacture
trivial comments to make the review appear complete. Removing a small private
helper made unused by the change is a `NITS(Simplicity)` correction when search
confirms no consumers and there is no behavioral impact; broader restructuring
with an optional benefit belongs under `BETTER` instead.

## Select the review viewpoint

Choose the single viewpoint that best explains why the comment matters:

- `Design`: architecture, responsibility, dependency direction, ownership, or
  abstraction boundaries.
- `Simplicity`: unnecessary complexity or control flow that creates a concrete
  comprehension or maintenance cost.
- `Naming`: an identifier that misstates behavior, units, ownership,
  cardinality, or side effects, or contains an unambiguous spelling error
  introduced by the change.
- `Style`: an established project convention whose violation has a concrete
  cost and is not already enforced automatically.
- `Functionality`: correctness, interfaces, data flow, performance,
  reliability, security, privacy, or operational behavior.
- `Test`: missing or invalid verification that permits a specific regression.
- `Document`: user, API, setup, migration, comment, or operational guidance
  that is incorrect or materially incomplete.

Do not duplicate one root cause under several viewpoints. Mention secondary
effects in the body and keep the prefix focused on the primary concern.

## Format each review comment

Use this exact title prefix:

```text
ACTION(Viewpoint): concise description
```

For example:

```text
MUST(Functionality): Advance the page before requesting the next result set
SHOULD(Test): Cover the failure branch that preserves the previous state
BETTER(Simplicity): Extract the repeated guard to make the exit condition clear
NITS(Naming): Correct the misspelled configuration key
```

Each actionable comment must contain:

1. **Location**: the smallest changed line range that demonstrates the issue.
2. **Evidence**: the relevant observed behavior or contract.
3. **Trigger**: the input, state, timing, environment, or caller behavior that
   exposes it.
4. **Impact**: the incorrect outcome or concrete quality or verification risk,
   and who or what is affected.
5. **Direction**: the expected outcome or a proportionate remediation
   direction without prescribing an unnecessarily large redesign.

The body should normally be one compact paragraph. Connect evidence to trigger
and impact rather than restating the code.

Every factual statement in the comment must be directly supported by inspected
code, configuration, documentation, test output, or verified tool behavior.
This requirement applies to optional supporting details as well as the core
defect claim. Cite a precedent, pattern, unchanged path, or specific location
only after reading it directly; otherwise omit it. A correct conclusion does
not make fabricated or inferred supporting evidence acceptable. Apply the same
factual checks to questions and summaries. Uncertainty may concern a material
requirement or intent, not an invented function, file, caller, or behavior.

## Communicate constructively

- Comment on the code and its observable behavior, never the author's ability,
  effort, or intent.
- Use respectful, neutral language. Avoid blame, sarcasm, commands without
  reasons, and claims such as "obviously" or "always" that the evidence does
  not establish.
- Explain why the issue matters and what acceptable outcome is expected. A
  bare demand is not an actionable review comment.
- Separate observed facts from assumptions. When the author's intent or an
  external contract is unknown, ask a concise question instead of disguising
  uncertainty as a finding.
- State optionality honestly. `BETTER` and `NITS` must not read like mandatory
  requests; `MUST` must not be softened until its required action is unclear.
- Prefer project rules and team consistency over personal preference.
- Offer a focused direction or small example when it reduces ambiguity, but do
  not rewrite the implementation in the comment.
- Keep one root cause per comment and avoid repeating the same request at
  multiple locations.
- If text discussion depends on unresolved product or design context, identify
  the decision that needs clarification instead of prolonging speculation.

Positive feedback can be included when it is specific and useful, but it does
not use an action-level prefix and must not obscure actionable comments.

## Structure the final response

Use this order:

1. Review comments ordered by `MUST`, `SHOULD`, `BETTER`, and `NITS`. Within an
   action level, order by impact: security or privacy compromise, data loss or
   broad outage, normal-path functional failure, limited edge-case failure,
   then maintainability or verification risk. Use file location only to break
   ties of similar impact.
2. Open questions about unresolved contracts or intent that materially affect
   the review, if any. Keep them distinct from findings and ground their premises
   in verified facts; do not disguise a defect allegation as a question.
3. A short summary and verification gaps, when useful.

Do not add a table when inline comments or the review platform's native
annotation format is clearer.

When no actionable comment exists, state that explicitly. Do not invent a
`BETTER` or `NITS` comment. Mention tests not run or areas not verified only
when the omission materially limits confidence.

An accurate, explicitly non-actionable note explaining why unchanged behavior
is outside scope is not a finding. Do not request repairs of an untouched defect
or imply that the reviewed change introduced it. Omit unrelated notes.

For a `MUST` comment with security, privacy, data-integrity, financial, or
broad availability impact, name that impact explicitly in the title or first
sentence so it cannot be mistaken for an ordinary merge blocker.

## Examples

English title:

```text
MUST(Functionality): Verify resource ownership before returning the record
```

Japanese title:

```text
MUST(Functionality): レコードを返す前にリソースの所有権を検証する
```

The action level and viewpoint remain stable across languages so that tooling
and evaluation fixtures can compare output consistently.
