# Project Technology Guidance

Add the project information needed for accurate technology-specific reviews to
this directory. The contents are intentionally not prescribed by Code Review
Skills because the relevant languages, frameworks, SDKs, versions, tools, and
constraints differ between projects.

Useful information may include:

- Language, framework, SDK, library, and tool versions.
- Framework lifecycle, state-management, and concurrency constraints.
- Project architecture and conventions that affect correctness.
- Build, test, lint, type-check, or code-generation commands.
- Guarantees provided by the compiler, runtime, framework, or infrastructure.
- Known compatibility requirements and unsupported patterns.

You may add Markdown guidance or link to authoritative project documentation.
Do not copy private or third-party material without permission.

Keep the guidance limited to information that changes how a review should be
investigated or judged. Repository instructions and verified project behavior
take precedence over general technology guidance. If this directory contains
no applicable information, the reviewer should investigate the repository and
must not invent technology-specific guarantees.
