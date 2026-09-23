# Behavioral Evaluations

These evaluations test the behavior of the generated skill without requiring
an exact wording match. Each case provides a review request, repository
context, a patch, and observable expectations.

## Automated fixture validation

Run:

```sh
make test
```

This verifies the generated packages and the structure and internal
consistency of every evaluation case. It does not call an AI service.

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

An evaluation passes only when all `must_report`, `must_not_report`, and
`output` expectations hold. Any additional finding must independently meet the
skill's evidence requirements; otherwise record it as a false positive.

Use a dated local evaluation record while the project is private. Do not
commit model transcripts when they contain machine paths, private repository
content, or unpublished correspondence.
