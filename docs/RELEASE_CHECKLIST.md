# Release Checklist

[日本語](RELEASE_CHECKLIST.ja.md)

This checklist separates checks that can run locally from approvals and
behavioral evidence that require a human decision. Do not tag or publish a
release while any required item remains incomplete.

## Automated checks

- [ ] `make release-check` passes from a clean checkout.
- [ ] The PR's required `validate` CI check passes, including `make language-check`
      for Java, Go, and Python fixtures (these runtimes are not required locally).
- [ ] A second `make build` produces no tracked diff.
- [ ] All generated packages were inspected after the final source change.
- [ ] The branch contains no uncommitted release file.

## Behavioral validation

- [ ] Run a documented, fresh-session release-candidate sample in both Codex
      and Claude Code. Cover a negative case in English and Japanese, a
      realistic multi-file change, and the highest-risk outstanding behavior
      concerns. Confirm Skill invocation for every result counted as a Skill
      pass. Full-suite behavioral execution is useful evidence, but a 100%
      exact-prefix score on every single run is not a release gate.
- [ ] Adjudicate every observed missed required finding, prohibited finding,
      prefix mismatch, or unsupported factual claim. Do not accept a missed
      security/data-loss defect or a false-positive finding as a harmless
      formatting deviation. A non-critical omitted `SHOULD`, `BETTER`, or
      `NITS` finding, a non-central prefix difference, or a supporting-detail
      error may be accepted only when its impact, rationale, and
      follow-up are recorded in the evaluation summary and release notes.
- [ ] For Claude Code, record the CLI version, model, Skill revision, and
      request language. In each fresh session, confirm Skill invocation from
      the execution trace separately from whether the output matches the
      fixture expectations; do not count an unassisted match as a Skill pass.
- [ ] For Claude Code, evaluate at least one negative fixture in both English
      and Japanese and classify every unexpected finding or unsupported
      supporting claim, including whether the behavior in #35 recurs.
- [ ] Across the release-candidate evaluations, at least one positive and one
      negative case produce equivalent finding decisions with English and
      Japanese requests; state the limited scope.
- [ ] Any unexpected finding has been classified as valid, ambiguous, or a
      false positive and reflected in the fixtures or methodology.
- [ ] Add a dated, sanitized summary of the release-candidate behavioral
      evidence to `tests/results/` and reference it from the release notes.
      Record campaign provenance (including reused runs), artifact/version
      identifiers, models and CLI versions, permissions and isolation limits,
      per-case and finding-level outcomes, repeat variation, usage/cost when
      available, adjudication method, and evaluation limits. Keep raw answers,
      traces, grading contexts, and machine-local paths outside the repository.

Optional quality step:

- [ ] Ask one or more reviewers other than the maintainer to assess the skill's
      technical usefulness. This is recommended but does not block release.

## Content and rights

- [ ] Editorial or rights-holder approval is recorded outside this repository.
- [ ] Acknowledgement wording and links are approved before they are added.
- [ ] The working tree and complete Git history contain no manuscript, proof,
      extracted text, figure, table, copied example, or private correspondence.
- [ ] Public documentation does not imply endorsement that was not granted.

## Operations

- [ ] Repository visibility, default branch, and branch protection are set.
- [ ] Issue templates and the published support policy route accepted feedback,
      out-of-scope requests, pull requests, and vulnerability reports correctly.
- [ ] GitHub private vulnerability reporting is enabled before `SECURITY.md`
      directs users to it.
- [ ] Installation steps have been tested from the public repository URL.

## Release

- [ ] `VERSION`, the version displayed in both READMEs, and both generated
      Skill package markers agree on `1.0.0`.
- [ ] Both changelogs contain a dated `1.0.0` section and release link.
- [ ] `docs/releases/v1.0.0.md` and `docs/releases/v1.0.0.ja.md` match the
      final release contents.
- [ ] Any output-contract addition or material review-behavior change is
      explained in the release notes with relevant evaluation evidence or limits.
- [ ] The release commit has received final review.
- [ ] Tag `v1.0.0` only after every required item above is complete.
- [ ] Run `make release-tag-check` after tagging to verify the tag, both
      changelogs, both release notes, `VERSION`, and both generated packages.
- [ ] Publish the GitHub Release as a stable release, not a pre-release.
