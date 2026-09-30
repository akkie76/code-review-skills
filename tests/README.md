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
modules, and compiles Python source files. This check can be run locally when
those runtimes are installed; Go dependency downloads are disabled. Neither
check establishes that an agent actually suppresses false positives.

The mixed-noise cases (`realistic-go-directory`, `realistic-java-fulfillment`,
`realistic-python-profile`, and `realistic-python-retry-audit`) combine actionable
changes with unrelated, plausible changes. The retry/audit case also requires
following the interaction between two changed files across a larger diff.
Their `case.json` files record the ecosystem, assumptions, expected cross-file
evidence, source, and limitations. All four are original
synthetic examples; no external OSS source is redistributed. Evaluate every
concern, including candidates listed under `must_not_report`, rather than
using diff size or the number of findings as a quality measure. The wider
suite also contains JavaScript cases, giving meaningful examples in four
languages overall.

## Manual agent evaluation

Run each case separately with both Codex and Claude Code:

1. Install the generated package for the agent under test.
2. Create an isolated temporary repository containing the files under the
   case's `repository/` directory.
3. Apply `change.diff` without committing it.
4. Submit each request in `case.json` without adding hints about the expected
   result.
5. Record whether every item under `expectations` was satisfied. Compare
   behavior and evidence, not sentence-level wording.
6. Repeat the case in a fresh conversation to avoid context from another
   fixture.

An evaluation passes only when all `must_report`, `must_not_report`, `prefixes`,
and `output` expectations hold. Any additional finding must independently meet
the skill's evidence requirements; otherwise record it as a false positive.
Evaluate at least one negative case with both English and Japanese requests
in each agent; do not infer cross-language behavior from the fixture schema.

Use a dated local evaluation record while the project is private. Do not
commit model transcripts when they contain machine paths, private repository
content, or unpublished correspondence.

Use [the manual evaluation record](RESULT_TEMPLATE.md) so product, model,
revision, language, and unexpected output are recorded consistently.

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
