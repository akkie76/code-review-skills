# Issue #24 v2 評価結果 — 2026-10-08

[English](2026-10-08-issue-24-v2-evaluation.md)

生成したCode Review Skill packageを対象とする、v2評価campaignの確定結果を記録します。
version管理された合成fixtureで評価し、基本評価の合格基準を80%に設定しました。
実際の開発現場におけるレビュー精度を示すものではありません。

## Campaignと評価対象

- Campaign方針：`issue-24-human-adjudication-v2`。
- 最終datasetは各agentの基本評価29件と事前指定の反復評価6件（各35件、合計70記録）ですが、
  一続きの実行ではなく、置き換えcampaignと既存実行の組み合わせです。
- 最初のv2 campaignで、Codexの`realistic-python-notice-batch`が一時的な接続失敗後に300秒で
  timeoutしました。そのcampaign内では再試行していません。同じrevisionと設定で置き換えcampaignを作成し、
  Codexの35件すべてをそこで再実行しました。
- 最初のcampaignで実施したClaudeの35件は変更せずに流用しました。revision・設定・model・package hashが一致し、
  記録上のdriftはありません。ルーブリックに一般的な流用規則はありませんが、この流用はmaintainerが承認しました。
  [Campaignの経緯](https://github.com/akkie76/code-review-skills/issues/24#issuecomment-6040546937)を参照してください。
- 合格基準：各agentの基本評価で80%以上、すなわち29件中24件以上。反復評価は参考情報であり、
  基本評価の得点には加算しません。
- 固定したsource revision：`05307082490bfd8416a60ce511faadf02998e5c4`。
- 生成packageのversion markerは`v0.1.0-beta.2`のままですが、PR #44・#45の公開後の変更を含みます。
  markerだけでは評価対象の内容を特定できないため、以下のsource hashとpackage hashで識別してください。
- 共通の生成元SHA-256：`104fe8438c7e44011ebd3f748c701550eccdbec8d36665089a604becf4e8f719`。
- 共通のpackage SHA-256：`cfb3047f846a8949d23572e0fb5dae69f2e69bbd03bdd7d462507d03153a3b3b`。
- fixture一式のSHA-256：`4de4361ee1fd0bbc2e96fb480b397acbcb21f9ba15e340eaaae8f85425459c37`。
- Codex CLI `0.160.0`、指定model `gpt-6.1-sol`。実行記録から実際に使用されたmodel IDは確認できませんでした。
  Skill fileの読み取りは確認しましたが、Skillの起動そのものを示す証拠より弱いものです。
- Claude Code `2.1.281`、model `claude-opus-5-5`。35回すべてで成功した`Skill` toolの結果を確認しました。

## 使用量、権限、分離

- Codexの35回分：入力2,954,159 tokens（うちcached 2,469,504）、出力20,665 tokens。費用は取得できませんでした。
- Claudeの35回分：通常入力328 tokens、cache作成入力648,106 tokens、cache読取1,620,312 tokens、
  出力50,455 tokens。記録された推定費用は約6.52米ドルです。
- Codexはephemeralなread-only sandboxで実行し、user設定を無視、approvalを無効化しました。
  read-onlyはfilesystemへの書き込み制限であり、command実行が一切不可能であることを意味しません。
  実際のmodel IDとSkill起動は独立に確認できていません。
- Claudeはstatic permission allowlist、fixture code実行無効、strict MCP設定で実行しました。
  実行を拒否されたcommandがあり、`permission_denied` eventとして記録されています。
  project設定を指定しましたが、userのSkill／memoryや管理設定が見える可能性があり、host全体の隔離は保証されません。
- したがって、両agentの実行環境では権限と隔離の設定が異なります。

## 結果

| Agent | 基本評価の合格 | 得点 | 反復評価の合格 | 完了 | 基準達成 |
| --- | ---: | ---: | ---: | --- | --- |
| Codex | 27/29 | 93.10% | 6/6 | はい | はい |
| Claude Code | 26/29 | 89.66% | 5/6 | はい | はい |

## 基本評価のcase別結果

| Case | 依頼言語 | Codex | Claude Code |
| --- | --- | --- | --- |
| `better-simplify-guard` | en | 不合格 | 合格 |
| `instruction-boundary` | en | 合格 | 合格 |
| `must-existing-consumer` | en | 合格 | 合格 |
| `must-focused-risk-variant` | en | 合格 | 合格 |
| `must-multi-agent-reconciliation` | en | 合格 | 不合格 |
| `must-multi-concern-depth` | en | 合格 | 不合格 |
| `must-same-diff-contract` | en | 合格 | 合格 |
| `must-shared-handler-variant` | en | 合格 | 合格 |
| `must-stale-documentation` | ja | 合格 | 合格 |
| `must-verified-supporting-evidence` | en | 合格 | 合格 |
| `negative-go-format` | en | 合格 | 合格 |
| `negative-go-runtime` | en | 合格 | 合格 |
| `negative-java-contract` | en | 合格 | 合格 |
| `negative-optional-label` | en | 合格 | 合格 |
| `negative-preexisting-defect` | en | 合格 | 合格 |
| `negative-refactor` | en | 合格 | 合格 |
| `negative-refactor` | ja | 合格 | 合格 |
| `nits-change-created-dead-code` | en | 合格 | 合格 |
| `nits-misspelled-local` | ja | 合格 | 合格 |
| `nits-project-style` | en | 不合格 | 合格 |
| `positive-pagination` | en | 合格 | 合格 |
| `realistic-go-directory` | en | 合格 | 合格 |
| `realistic-java-fulfillment` | en | 合格 | 合格 |
| `realistic-python-notice-batch` | en | 合格 | 合格 |
| `realistic-python-profile` | en | 合格 | 合格 |
| `realistic-python-retry-audit` | en | 合格 | 合格 |
| `should-ineffective-regression-test` | en | 合格 | 不合格 |
| `should-layer-boundary` | en | 合格 | 合格 |
| `should-missing-test` | en | 合格 | 合格 |

固定した集計処理では、両agentが80%基準を超えたためcampaignは合格です。一方、個別caseには
厳密基準での不一致が残っています。

- Codex：`nits-project-style`は期待値`NITS(Style)`に対して`MUST(Style)`。`better-simplify-guard`は
  有効なテスト改善案を出しましたが、必須の`BETTER(Simplicity)`を指摘しませんでした。
- Claude Code：`should-ineffective-regression-test`ではテスト不足を検出しましたが、期待値`SHOULD(Test)`に
  対して`MUST(Test)`でした。maintainerは実用上許容と判断しましたが、固定した集計基準ではprefix不一致のため
  不合格です。`must-multi-agent-reconciliation`では必須の不具合を検出した一方、変更前の挙動について誤った
  説明を含みました。`must-multi-concern-depth`では、空白nicknameを不具合とみなすプロジェクト要件がなく、
  変更前の挙動についても誤った説明を含んでいました。

以下の指摘単位の件数は基本評価29件のみです。必須項目はcaseごとに一度だけ数え、負例は検出数を増やしません。

| Agent | 必須項目の検出 (TP) | 必須項目の見逃し (FN) | 根拠のない指摘 (FP) | 妥当な追加 | 任意 | 重複 | 根拠のない補足 | 禁止項目との一致 | 必須prefix不一致 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex | 24 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 |
| Claude Code | 25 | 0 | 1 | 2 | 1 | 0 | 2 | 0 | 1 |

表の得点は固定した厳密ルーブリックの結果です。`SHOULD(Test)`と`MUST(Test)`の差を実用上許容するmaintainerの見解は
参考情報として記録し、scorerのcase判定は変更していません。

## 反復評価の観察

| Case | Codex 基本→反復 | Claude Code 基本→反復 |
| --- | --- | --- |
| `nits-misspelled-local` | 合格→合格 | 合格→合格 |
| `must-stale-documentation` | 合格→合格 | 合格→合格 |
| `should-missing-test` | 合格→合格 | 合格→合格 |
| `nits-change-created-dead-code` | 合格→合格 | 合格→不合格 |
| `should-layer-boundary` | 合格→合格 | 合格→合格 |
| `must-verified-supporting-evidence` | 合格→合格 | 合格→合格 |

Codexは6組すべてで結果・分類に変化がありませんでした。Claude Codeは5組で安定しました。
`nits-change-created-dead-code`の反復側は、変更行を6行目ではなく7行目と記載しました。
maintainerは1行の位置ずれを実用上軽微と判断しましたが、固定した基準では根拠の誤りとして反復評価を不合格にしています。
反復評価は参考情報で、基本評価の得点には加えません。6組の反復だけから一般的な再現性を推定することはできません。

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
