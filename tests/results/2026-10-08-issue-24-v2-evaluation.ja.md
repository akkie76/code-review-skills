# Issue #24 v2 評価結果 — 2026-10-08

[English](2026-10-08-issue-24-v2-evaluation.md)

生成したCode Review Skill packageを対象とする、v2評価campaignの確定結果を記録します。
version管理された合成fixtureで評価し、基本評価の合格基準を80%に設定しました。
実際の開発現場におけるレビュー精度を示すものではありません。

## Campaignと評価対象

- Campaign方針：`issue-24-human-adjudication-v2`。
- 各agentは基本評価29件と、事前指定の反復評価6件を実行（各35回、合計70回）。
- 合格基準：各agentの基本評価で80%以上、すなわち29件中24件以上。反復評価は参考情報であり、
  基本評価の得点には加算しません。
- 固定したsource revision：`05307082490bfd8416a60ce511faadf02998e5c4`。
- 両packageのSkill version：`v0.1.0-beta.2`。
- 共通の生成元SHA-256：`104fe8438c7e44011ebd3f748c701550eccdbec8d36665089a604becf4e8f719`。
- 共通のpackage SHA-256：`cfb3047f846a8949d23572e0fb5dae69f2e69bbd03bdd7d462507d03153a3b3b`。
- fixture一式のSHA-256：`4de4361ee1fd0bbc2e96fb480b397acbcb21f9ba15e340eaaae8f85425459c37`。
- Codex CLI `0.160.0`、指定model `gpt-6.1-sol`。実行記録から実際に使用されたmodel IDは確認できませんでした。
  Skill fileの読み取りは確認しましたが、Skillの起動そのものを示す証拠より弱いものです。
- Claude Code `2.1.281`、model `claude-opus-5-5`。35回すべてで成功した`Skill` toolの結果を確認しました。

## 結果

| Agent | 基本評価の合格 | 得点 | 反復評価の合格 | 完了 | 基準達成 |
| --- | ---: | ---: | ---: | --- | --- |
| Codex | 27/29 | 93.10% | 6/6 | はい | はい |
| Claude Code | 26/29 | 89.66% | 5/6 | はい | はい |

固定した集計処理では、両agentが80%基準を超えたためcampaignは合格です。一方、個別caseには
厳密基準での不一致が残っています。

- Codex：`nits-project-style`は期待値`NITS(Style)`に対して`MUST(Style)`。`better-simplify-guard`は
  有効なテスト改善案を出しましたが、必須の`BETTER(Simplicity)`を指摘しませんでした。
- Claude Code：`should-ineffective-regression-test`ではテスト不足を検出しましたが、期待値`SHOULD(Test)`に
  対して`MUST(Test)`でした。maintainerは実用上許容と判断しましたが、固定した集計基準ではprefix不一致のため
  不合格です。`must-multi-agent-reconciliation`では必須の不具合を検出した一方、変更前の挙動について誤った
  説明を含みました。`must-multi-concern-depth`では、空白nicknameを不具合とみなすプロジェクト要件がなく、
  変更前の挙動についても誤った説明を含んでいました。

## 反復評価の観察

Codexは6組すべてで基本評価と反復評価の結果・分類が一致しました。Claude Codeは6組中5組で安定しました。
`nits-change-created-dead-code`では基本評価が合格、反復評価が不合格でした。反復側は変更行を6行目ではなく
7行目と記載しています。maintainerは1行の位置ずれを実用上軽微と判断しましたが、固定した基準では根拠の誤りとして
反復評価を不合格にしています。反復評価は参考情報で、基本評価の得点には加えません。6組の反復だけから、
一般的な再現性を推定することはできません。

## 結果の解釈と限界

- version管理された小規模な合成fixtureの結果です。実プロジェクトでのレビュー精度、precision、recall、
  不具合防止率を測定したものではありません。
- maintainerがassistantによる分析を参考に各記録を判定しました。ブラインドの独立採点ではないため、
  reviewerやmodel familyによる偏りが残る可能性があります。
- Codexの実際のmodel IDは実行記録から確認できず、file readの証拠だけではSkillの起動や結果への因果的な影響を
  証明できません。ClaudeではSkillの呼び出しを確認しましたが、このcampaignもSkillの因果的な効果を分離するものでは
  ありません。
- 得点は記録したmodel／CLI version、Skill package、固定rubric、fixtureに限った結果です。他のversionや
  project contextでは異なる結果になり得ます。
- 生の回答、実行trace、grading context、各マシン固有のpathは公開記録に含めていません。

両agentはcampaignで合意した80%基準を満たしました。これはbeta評価の基準を満たした結果であり、レビュー品質の保証や
安定版リリースの承認を意味しません。
