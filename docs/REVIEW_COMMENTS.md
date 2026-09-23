# Review Comment Convention

[日本語](REVIEW_COMMENTS.ja.md)

Every actionable review comment uses this prefix:

```text
ACTION(Viewpoint): concise description
```

## Action levels

- `MUST`: A demonstrated problem that must be resolved before merge.
- `SHOULD`: A concrete quality or maintenance risk that should normally be
  resolved, but may be deferred by an explicit team decision.
- `BETTER`: An optional alternative with a specific benefit. The current
  implementation remains acceptable.
- `NITS`: A minor, non-blocking correction. Use sparingly and never for
  automatically enforced formatting.

## Review viewpoints

- `Design`: Architecture, responsibilities, dependencies, and boundaries.
- `Simplicity`: Complexity that creates a concrete comprehension or
  maintenance cost.
- `Naming`: Identifiers that misstate behavior or important constraints.
- `Style`: Established project conventions not covered by automation.
- `Functionality`: Correctness, interfaces, security, reliability,
  performance, privacy, and operational behavior.
- `Test`: Verification that is missing or unable to detect a specific
  regression.
- `Document`: Incorrect or incomplete user, API, setup, migration, comment, or
  operational guidance.

## Comment-writing rules

Describe the code's observable behavior rather than judging the author.
Connect evidence to the triggering conditions and impact, explain why the
comment matters, and state an acceptable outcome or proportionate direction.
Use respectful, neutral language and distinguish facts from assumptions.

When context is missing, ask a question instead of presenting uncertainty as
a finding. State optionality honestly: optional comments must not read as
demands, and required comments must remain unambiguous. Prefer project rules
and team consistency over personal taste, keep one root cause per comment, and
do not invent a low-value comment when no actionable issue exists.

Example:

```text
MUST(Functionality): Advance the page before requesting the next result set

When the API returns a full page, the loop requests the same page again because
`page` never changes. This duplicates results until `maxPages` and increases
request volume. Increment the page before the next request so each iteration
fetches a new result set.
```
