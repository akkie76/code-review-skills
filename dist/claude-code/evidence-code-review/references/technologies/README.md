# Project Technology Guidance

[日本語](README.ja.md)

This directory explains what project information helps technology-specific
reviews. Do not edit the installed copy to store project configuration: a
Skill update may replace it, and a personal installation is shared by every
project.

Store the actual guidance in the reviewed repository, such as in `AGENTS.md`,
`CLAUDE.md`, or a project document referenced by those instructions. The format
is intentionally not prescribed because the relevant languages, frameworks,
SDKs, versions, tools, and constraints differ between projects.

Useful information may include:

- Language, framework, SDK, library, and tool versions.
- Framework lifecycle, state-management, and concurrency constraints.
- Project architecture and conventions that affect correctness.
- Build, test, lint, type-check, or code-generation commands.
- Guarantees provided by the compiler, runtime, framework, or infrastructure.
- Known compatibility requirements and unsupported patterns.

You may add Markdown guidance or link to authoritative project documentation.
Do not copy private or third-party material without permission.

Keep project guidance limited to information that changes how a review should be
investigated or judged. Repository instructions and verified project behavior
take precedence over general technology guidance. If this directory contains
no applicable information, the reviewer should investigate the repository and
must not invent technology-specific guarantees.
