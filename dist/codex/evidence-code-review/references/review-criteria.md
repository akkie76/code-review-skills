# Review Criteria

Use these criteria selectively after understanding the intended change. They
are prompts for investigation, not a requirement to manufacture one comment
per category.

## Behavioral correctness

Confirm that the implementation satisfies the current product and API
contract across normal, boundary, and failure cases.

Check for:

- Incorrect conditions, calculations, ordering, defaults, or state
  transitions.
- Missing handling for empty, absent, malformed, duplicated, stale, or
  partially available data.
- Errors that are swallowed, mistranslated, retried unsafely, or exposed at
  the wrong abstraction boundary.
- Partial side effects when an operation fails midway.
- Behavior that contradicts requirements, compatibility guarantees, or
  platform semantics.

## Interfaces and data flow

Trace how data and control cross module, process, persistence, and network
boundaries.

Check for:

- Existing callers or consumers that were not changed but no longer satisfy a
  modified shared contract. Search beyond newly added or edited call sites.
- Unchanged enum cases, sum-type variants, subtypes, or modes whose guarantees
  are altered by an unconditional mutation or side effect in a shared handler.
- Downstream validation, authorization, deduplication, or safety checks that a
  new upstream effect now pre-satisfies or bypasses for variants it was not
  intended to change.
- Conceptually equivalent paths added or modified in the same diff that apply
  conflicting precedence, validation, normalization, error, state, or response
  semantics without an inspected contract justifying the difference.
- Callers that no longer satisfy a changed precondition.
- Consumers that cannot handle a new return value, error, or state.
- Schema, serialization, migration, or versioning mismatches.
- Ownership, lifetime, concurrency, retry, cancellation, or cleanup mistakes.
- External side effects occurring in an unsafe or irreversible order.

## Design and maintainability

Judge structure against the repository's established architecture and the
cost of likely changes, not against a preferred pattern in isolation.

Check for:

- Responsibilities placed in the wrong layer or combined without a coherent
  reason.
- Dependencies that point against the intended architecture or make focused
  testing impractical.
- New extension points that require repeated modification of unrelated code.
- Duplicate sources of truth or inconsistent implementations of the same
  policy.
- Branches, symbols, assets, configuration, or tests that the change leaves
  unreachable or unused. Confirm that no consumer remains by repository search
  or authoritative tooling before reporting the dead code.
- Abstractions that hide important behavior, or fragmentation that makes a
  single operation unnecessarily difficult to follow.

Prefer the smallest design change that removes the demonstrated risk. Do not
request speculative abstraction solely for possible future reuse.

## Comprehensibility

Evaluate whether a maintainer can infer intent and constraints from the code
without reconstructing hidden context.

Check for:

- Names that misstate behavior, units, ownership, cardinality, or side
  effects.
- Control flow whose important cases are obscured by nesting or incidental
  detail.
- Comments that repeat syntax, contradict behavior, or compensate for an
  unclear interface.
- Local conventions that diverge enough to create a concrete maintenance or
  defect risk.

Formatting preferences belong in automated tooling where practical.

## Security and privacy

Treat all external input and cross-trust-boundary data as untrusted until the
code establishes otherwise.

Check for:

- Missing authorization at the operation or resource boundary.
- Injection, unsafe parsing, path traversal, request forgery, or output
  encoding failures.
- Secrets, credentials, personal data, or sensitive operational details in
  code, fixtures, errors, analytics, or logs.
- Unsafe storage, transport, session, cookie, or cryptographic configuration.
- Validation performed after a sensitive side effect or only in a client that
  an attacker can bypass.
- New dependencies, permissions, or execution paths with unjustified trust.

Do not recommend a security control without connecting it to a concrete threat
in the changed path.

## Performance and reliability

Review resource use relative to realistic input size, call frequency, and
service constraints.

Check for:

- Unbounded work, memory growth, recursion, queues, retries, or fan-out.
- Repeated I/O, queries, parsing, or allocation on a hot path.
- Blocking work on latency-sensitive or single-threaded execution contexts.
- Races, deadlocks, lost updates, duplicate side effects, and non-idempotent
  retry behavior.
- Timeouts, backpressure, cleanup, or degradation behavior that cannot meet
  the system's availability expectations.

Avoid performance findings based only on aesthetic inefficiency; establish a
plausible scale or hot path.

## Verification and tests

Evaluate whether tests demonstrate the changed public behavior and important
failure modes.

Check for:

- Missing coverage for a newly introduced branch, boundary, or regression
  scenario.
- Assertions that can pass while the intended behavior is broken.
- Tests coupled to private implementation details instead of observable
  behavior.
- Nondeterminism, shared state, real external services, or timing assumptions
  that make results unreliable.
- Mocks or fixtures that no longer represent the production contract.
- Test constants that duplicate implementation details and can drift from the
  specification they are meant to verify.

Do not require a test merely because a line changed. State the failure the
missing test would need to catch.

## Documentation and operations

Check documentation when the change affects how people or systems install,
configure, call, deploy, observe, recover, or migrate the software.

Check for:

- Public behavior changed without corresponding API or user documentation.
- Setup, configuration, dependency, permission, or migration steps that are
  missing or stale.
- Operational changes without suitable logging, metrics, alerts, rollback, or
  recovery guidance.
- Examples that now recommend invalid or unsafe usage.
- Comments and runbooks that conflict with the implementation.
