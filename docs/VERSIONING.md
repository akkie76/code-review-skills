# Versioning and Compatibility

[日本語](VERSIONING.ja.md)

Published Codex and Claude Code packages share one [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
version from `VERSION`. Generated `SKILL.md` files expose it in a
`<!-- skill-version: vX.Y.Z -->` comment outside standard frontmatter. Git
release tags use the same version with a `v` prefix. The package directory and
Skill name are not versioned; inspect the comment in an installed copy to
identify it.

## Documented output contract

The following is the public output surface that downstream readers and tools
may rely on. [The output contract](../src/core/output-contract.md) defines its
full current behavior.

- Actionable finding titles begin `ACTION(Viewpoint):`. `ACTION` is one of
  `MUST`, `SHOULD`, `BETTER`, or `NITS`, with the meanings in the
  [review comment convention](REVIEW_COMMENTS.md). The action level expresses
  expected action, not confidence or implementation effort.
- `Viewpoint` is one of `Design`, `Simplicity`, `Naming`, `Style`,
  `Functionality`, `Test`, or `Document`. New viewpoints may be added as
  documented, additive contract changes; consumers must not assume this list
  will never grow. Existing names will not silently be repurposed.
- Each actionable finding provides a location, evidence, trigger, impact, and
  direction. These are information requirements, not fixed field labels or a
  machine-readable schema. The wording, paragraph layout, and presentation
  may evolve.
- The final response presents actionable findings by action level, followed
  by material open questions and a concise summary or verification gaps when
  useful. If there are no actionable findings, it says so explicitly. It does
  not promise identical prose, finding counts, or line ranges across runs.

## Output compatibility versus review behavior

Output compatibility concerns the documented structure and meaning above.
Review behavior concerns *which* defects are found, missed, or rejected as
unsupported. Better tracing, evidence checks, or false-positive suppression
can change findings without changing the output contract. Model, host agent,
available tools, and project context also affect results. A compatible version
does not guarantee identical review decisions or reproducible wording.

For releases that add to the output contract or materially change review
behavior, describe the change in release notes and record relevant evaluation
results or limitations. A corrected review decision is not automatically a
breaking output-format change.

## Choosing a version

- **Major**: after 1.0, an incompatible change to the documented output
  contract, such as removing an action level, changing its meaning, or
  replacing the title prefix syntax.
- **Minor**: a backward-compatible addition to the contract, such as a new
  viewpoint, or a substantial new capability. Describe how consumers can
  accommodate the addition.
- **Patch**: compatible corrections, clarifications, packaging fixes, or
  review-method improvements that do not add a public capability. Material
  changes in findings still need release notes and evaluation evidence.

`0.x` and pre-release versions are under evaluation and do not carry a stable
compatibility guarantee. Breaking changes during this period may be released
under a new pre-release version without prematurely declaring 1.0, but must
be called out prominently in its release notes with migration guidance. Never
change the contents of an already published version; issue a new version.

When deprecating a contract element, announce the replacement and migration
path in release notes. Keep the old form working through a reasonable
transition where practical, then remove it in an appropriately versioned
release. No fixed transition duration is promised; urgent correctness or
security fixes may require a shorter path, which must be explained.

## Release verification

`make release-check` validates `VERSION` syntax and its marker in both
generated packages. During release preparation, update both changelogs and
both release notes. After tagging the release commit, run
`make release-tag-check`: it also requires that `v<version>` points to `HEAD`
and that the dated changelog sections, release links, and English/Japanese
release-note titles agree with `VERSION`. Human review must still confirm the
release notes accurately describe the changes and evaluation evidence.
