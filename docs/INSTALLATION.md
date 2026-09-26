# Installation Guide

[日本語](INSTALLATION.ja.md)

Install the complete `evidence-code-review` directory. The package includes
references required by `SKILL.md`.

## Choose a scope

- Personal installation loads the Skill for projects on the current machine.
- Project installation travels with one repository and can be shared by its
  team.
- Repository instructions remain the right place for project-specific rules.

## macOS and Linux

Codex personal installation:

```sh
mkdir -p ~/.codex/skills
cp -R dist/codex/evidence-code-review ~/.codex/skills/
```

Codex project installation:

```sh
mkdir -p /path/to/project/.agents/skills
cp -R dist/codex/evidence-code-review /path/to/project/.agents/skills/
```

Claude Code personal installation:

```sh
mkdir -p ~/.claude/skills
cp -R dist/claude-code/evidence-code-review ~/.claude/skills/
```

Claude Code project installation:

```sh
mkdir -p /path/to/project/.claude/skills
cp -R dist/claude-code/evidence-code-review /path/to/project/.claude/skills/
```

## Windows PowerShell

Replace `<repository>` with this repository's checkout path.

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force "<repository>\dist\codex\evidence-code-review" "$HOME\.codex\skills\"

New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "<repository>\dist\claude-code\evidence-code-review" "$HOME\.claude\skills\"
```

## Verify

Start a new agent session after installation.

- Codex: ask `Use the evidence-code-review skill to review the working tree.`
- Claude Code: invoke `/evidence-code-review` or request the same in prose.

A review comment should use a prefix such as `MUST(Functionality):`. When no
actionable issue exists, the Skill should say so rather than inventing one.

## Update

Fetch or download the intended repository revision, review its changes, and
copy the complete package directory to the same destination again. Do not keep
project-specific information inside the installed package; store it in the
project so replacement is safe.

## Remove

Remove only the installed `evidence-code-review` directory from the selected
personal or project skills directory. Start a new session afterward.

## Troubleshoot

- Confirm the installed directory is named `evidence-code-review` and directly
  contains `SKILL.md` and `references/`.
- Confirm the frontmatter `name` is also `evidence-code-review`.
- Start a new session after adding or replacing the Skill.
- Invoke the Skill explicitly to distinguish discovery problems from review
  behavior problems.
- Check product policies when managed, safe, or restricted modes prevent
  personal or project Skills from loading.
- Record the product version, model, repository revision, request, and observed
  result when asking for support.
