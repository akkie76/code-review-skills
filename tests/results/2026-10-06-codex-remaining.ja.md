# Codexの残りバッチ評価：2026-10-06

[English](2026-10-06-codex-remaining.md)

[分割実行計画](../EVALUATION_BATCHES.ja.md)の通算Batch 6〜16にある19ケースと、`should-missing-test`の再評価1件を記録します。20回すべて実行完了しました。残りケースの厳密なfixture一致は16/19、別途行ったテスト不足の再評価も一致しました。これは観測したfixture一致であり、一般的なレビュー精度の推定ではありません。

## 実行条件と変更

- 対象：`b2a1ea2ac833f34aa64638a44e5f0b89d686c5ab`。
- エージェント：Codex CLI `0.159.2`、モデル`gpt-6.1-sol`。
- 各ケース1回、英語、新規session、隔離リポジトリ、可視の未コミットfixture差分、read-only、ephemeral、ユーザー設定無視、timeout 300秒。
- 1回最大2ケースで順に実行し、バッチ間で利用枠を確認。
- 共通workflowを、現在の実装不具合だけでなく確認済みの品質・検証リスクも扱う定義に整理しました。既存テストを読み、検出できない具体的な回帰を示せる場合、実装が現在正しくても`SHOULD(Test)`の根拠になると明記しています。テストを実行できなかったことだけではテスト不足の根拠になりません。両packageを再生成しました。
- 今回の依頼文と期待指摘は変更していません。先に行ったBatch 3のfixture整理は対象revisionに含まれます。

このチャットのエージェントが回答と関連する実行記録を`must_report`、`must_not_report`、`prefixes`、`output`と照合しました。ブラインド評価や独立採点ではありません。生のrunner集計の意味的な判定は未判定のままとし、下記の手動確認を別に記録します。

## 残りケースの結果

| Batch | Case | 厳密なfixture一致 |
| --- | --- | --- |
| 6 | `must-focused-risk-variant` | 合格 |
| 6 | `nits-change-created-dead-code` | prefix不一致：期待`NITS(Simplicity)`、実際`BETTER(Simplicity)` |
| 7 | `must-existing-consumer` | 合格 |
| 7 | `realistic-go-directory` | 合格 |
| 8 | `realistic-java-fulfillment` | 合格。必須の2件とも指摘 |
| 9 | `negative-preexisting-defect` | 本文の手動照合で合格 |
| 9 | `instruction-boundary` | 合格。fixtureを実行せずレビュー |
| 10 | `must-same-diff-contract` | 合格 |
| 10 | `must-shared-handler-variant` | 合格 |
| 11 | `should-ineffective-regression-test` | 合格 |
| 11 | `realistic-python-profile` | 合格。必須の2件とも指摘 |
| 12 | `realistic-python-retry-audit` | 合格 |
| 13 | `negative-refactor` | 本文の手動照合で合格 |
| 13 | `better-simplify-guard` | 必須の`BETTER(Simplicity)`提案が欠落 |
| 14 | `must-multi-agent-reconciliation` | 最終出力は一致。実際の委譲動作は未検証 |
| 14 | `must-multi-concern-depth` | 合格 |
| 15 | `must-verified-supporting-evidence` | 合格 |
| 15 | `should-layer-boundary` | prefix不一致：期待`SHOULD(Design)`、実際`MUST(Design)` |
| 16 | `realistic-python-notice-batch` | 合格 |

## 不一致の判断と再評価

1. `nits-change-created-dead-code`は、変更で未使用になったprivate helperを正しく検出し、削除を任意の修正として説明しましたが、`BETTER`を使いました。厳密なprefix不一致を残します。機能不具合の見逃しではありません。
2. `better-simplify-guard`は、繰り返したactive-admin条件を名前付き条件にする任意提案を出しませんでした。代わりに、新たな権限分岐に対する具体的な`SHOULD(Test)`を指摘し、roleとactive状態の境界検証を提案しています。fixtureにテストがないことをリポジトリ確認で裏付けました。この追加の検証リスク指摘は妥当ですが、必須の簡素化指摘を満たすものではありません。
3. `should-layer-boundary`はdomainからUIへの依存を正しく検出しましたが、repositoryの明示的な「must not」という規約違反を`MUST`と分類しました。不一致を残し、この出力に合わせてfixture期待値を変更しません。

Skillの明文化後、別途実行した`should-missing-test`は、timeoutからの回復・上限到達・拒否理由の保持について期待する`SHOULD(Test)`を出しました。`should-ineffective-regression-test`も、実装変更を元に戻しても通るassertionを`SHOULD(Test)`として指摘しました。明文化を支持する観察ですが、各1回だけでは因果関係や安定した再現性は確定できません。今回の残りケースでは、必須の`MUST(Functionality)`不具合の見逃しはありませんでした。

## 制約と利用量

- 20回すべてでSkillファイルの読み取りを観測しました。専用のSkill起動イベントは取得できていません。
- 複数エージェントのcaseは、子エージェント初期化に失敗したと報告しています。最終指摘は一致しましたが、独立した委譲と統合が成功した評価には数えません。
- 負例では説明が続く`No actionable findings`や`No actionable defects found`を使っており、runnerの狭い表現検出はfalseを返しました。本文の確認では正式な指摘はありません。元の集計を変更していません。
- エージェントの複数の検査ではNode.js・Goが利用できず、Javaの検証も静的確認でした。一部のPython検証は実行しています。profileの再現では、環境のPythonがfixture想定より古いため型注釈を遅延評価しました。これは絞った挙動確認であり、想定runtime全体のテストではありません。
- 大きな通知caseでは既存テスト3件が成功し、別の通知5件の再現で未送信通知の取りこぼしを確認しました。既存テストの成功だけで正しさは確定しません。
- 先のバッチは別revisionで行っています。この報告は最終revisionで全28ケースを揃えた評価ではなく、過去の結果も遡って再採点していません。
- 20回の利用量：入力1,619,760 tokens（キャッシュ済み1,383,296）、出力11,898 tokens。生の記録はリポジトリ外に保管し、CLIから料金額は取得できていません。
- `make release-check`は成功しました（toolingテスト19件、fixture構造28件）。skill-creatorの単独検証器はPyYAML不足で実行できませんでしたが、repositoryのpackage検証は成功しています。

先のDocument caseで期待`MUST(Document)`に対して`SHOULD(Document)`となった分類の課題は別に残っています。本報告やテスト不足の改善によって、その課題やリリース可否が自動的に解決するわけではありません。
