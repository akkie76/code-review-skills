# Manual Evaluation Record

[日本語](RESULT_TEMPLATE.ja.md)

- Date:
- Evaluator:
- Agent and product version:
- Requested model / CLI-reported model / evidence source:
- Skill commit or release:
- Skill version / source hash / actual package hash:
- Worktree dirty / evaluation inputs dirty:
- Case ID:
- Request language:
- Fresh session: yes / no
- Invocation mode: implicit / explicit
- Invocation evidence: confirmed / by_construction / file_read_observed / not_observed
- Skill invoked: yes / no / not verified
- Tool permissions / fixture-code execution allowed:
- Denied verification attempts / isolation limitations:
- Fixture expectations: pass / fail
- Skill behavior assessment (if invoked): pass / fail / limited
- Expected prefixes observed:
- Required behavior observed:
- Prohibited behavior observed:
- Additional comments:
- Classification of unexpected output: valid / ambiguous / false positive
- Follow-up:

Keep output matches separate from invocation evidence and syntax checks. A
file read is weaker than a dedicated Skill tool event. Do not combine implicit
and explicit runs, or attribute dirty inputs to the recorded commit alone.

Do not include private repository content, credentials, personal data, or
unpublished correspondence in a record intended for publication.
