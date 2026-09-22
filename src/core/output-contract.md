# Review Output Contract

Apply this contract after investigating and validating candidate findings. It
defines how to communicate review results; it does not lower the evidence
required to report them.

## Select the output language

Write the review in the language explicitly requested by the user. If the user
does not specify a language, follow authoritative repository instructions. If
neither specifies a language, use the language of the user's review request.

Keep source identifiers, API names, command names, paths, and error messages in
their original form unless translating them is necessary for comprehension.
Do not produce duplicate English and Japanese reviews unless the user requests
both.

## Assign priority

Priority represents the urgency of correcting a demonstrated defect. It is not
a measure of reviewer confidence, code complexity, or the amount of work
needed to fix it.

### P0 - Critical

Use P0 only when the change creates an immediate, broadly damaging condition
that requires stopping deployment or operation. Examples include active data
loss, a broadly exploitable security failure, or a system-wide outage on the
normal path.

P0 findings block merge and usually require incident-level attention. Do not
use P0 for a serious defect with narrow or unlikely preconditions.

### P1 - High

Use P1 for a clear defect on a realistic path that can cause substantial user,
security, financial, data-integrity, or availability impact.

P1 findings block merge. The triggering conditions may be narrower than P0,
but they must be plausible in the system's intended use.

### P2 - Medium

Use P2 for a reproducible defect whose impact is limited in scope, recoverable,
or dependent on less common conditions. This includes violations of an
established contract that are likely to become user-visible or operationally
costly.

P2 findings should normally be corrected before merge. A team may consciously
defer one when the risk and follow-up are recorded.

### P3 - Low

Use P3 for a concrete, low-impact defect or maintainability problem that has a
demonstrable future cost. The issue must still be actionable and caused by the
change.

P3 findings are non-blocking. Do not use P3 as a container for preferences,
optional refactoring, praise, questions, or formatter output.

## Categorize the finding

Choose the single category that best describes the primary failure:

- `Correctness`: behavior, state, error handling, or contract failures.
- `Interface`: integration, compatibility, schema, or data-flow failures.
- `Design`: architecture, responsibility, dependency, or testability failures.
- `Clarity`: misleading names or structure with a demonstrated maintenance
  risk.
- `Security`: confidentiality, integrity, authorization, validation, or trust
  boundary failures.
- `Reliability`: performance, concurrency, resource, recovery, or availability
  failures.
- `Test`: missing or invalid verification that permits a specific regression.
- `Documentation`: user, API, setup, migration, or operational guidance that
  is incorrect or materially incomplete.

Do not create duplicate findings under multiple categories. Select the root
cause and describe the downstream impact in the body.

## Write each finding

Each finding must contain:

1. **Title**: `[P#][Category]` followed by a concise description of the defect.
2. **Location**: the smallest changed line range that demonstrates the issue.
3. **Trigger**: the input, state, timing, environment, or caller behavior that
   exposes it.
4. **Impact**: the incorrect outcome and who or what is affected.
5. **Direction**: enough remediation guidance to make the requested action
   clear without prescribing an unnecessarily large redesign.

The body should be one compact paragraph whenever possible. Connect the
location to the trigger and impact rather than restating the code. Use a
question instead of a finding when missing context prevents establishing that
the behavior is defective.

## Structure the final response

Use this order:

1. Findings, ordered from P0 to P3 and then by file location.
2. Open questions that materially affect the review, if any.
3. A short summary and verification gaps, when useful.

Do not add a findings table when inline findings or the review platform's
native annotation format is clearer.

When no actionable finding exists, state that explicitly. Do not invent a low
priority comment to make the review appear complete. Mention tests not run or
areas not verified only when the omission materially limits confidence.

## Examples

English title:

```text
[P1][Security] Enforce resource ownership before returning the record
```

Japanese title:

```text
[P1][Security] レコードを返す前に所有権を検証する
```

The category identifier remains stable across languages so that tooling and
evaluation fixtures can compare output consistently.
