# Release Checklist

This checklist separates checks that can run locally from approvals and
behavioral evidence that require a human decision. Do not tag or publish a
release while any required item remains incomplete.

## Automated checks

- [ ] `make release-check` passes from a clean checkout.
- [ ] A second `make build` produces no tracked diff.
- [ ] All generated packages were inspected after the final source change.
- [ ] The branch contains no uncommitted release file.

## Behavioral validation

- [ ] Every fixture passes a fresh-session evaluation in Codex.
- [ ] Every fixture passes a fresh-session evaluation in Claude Code.
- [ ] English and Japanese requests produce equivalent finding decisions.
- [ ] Any unexpected finding has been classified as valid, ambiguous, or a
      false positive and reflected in the fixtures or methodology.

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
- [ ] Unsolicited Issues and pull requests are disabled or clearly routed by
      the published support policy.
- [ ] GitHub private vulnerability reporting is enabled before `SECURITY.md`
      directs users to it.
- [ ] Installation steps have been tested from the public repository URL.

## Release

- [ ] `CHANGELOG.md` contains a dated `0.1.0` section and comparison links.
- [ ] `docs/releases/v0.1.0.md` matches the final release contents.
- [ ] The release commit has received final review.
- [ ] Tag `v0.1.0` only after every required item above is complete.
