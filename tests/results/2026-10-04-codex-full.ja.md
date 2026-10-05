# Codex beta.2リリース候補の評価：2026-10-04

[English](2026-10-04-codex-full.md)

## 対象と方法

- 対象：PR #41の`7e3427e`。生成済みCodex Skill `v0.1.0-beta.2`。Skillのソースと生成物は、先のリリースブランチの部分評価から変更していません。
- エージェント：Codex CLI `0.158.0-alpha.2.1`、モデル`gpt-6-luna`、推論強度high。
- 28件すべてのfixtureを、隔離した新規の一時sessionで1回ずつ、読み取り専用で実行しました。英語の依頼文があれば英語、なければ日本語を使いました。さらに`negative-refactor`を日本語でも実行し、計29回です。
- 各一時repositoryにはfixtureのbaselineファイルとプロジェクト単位の生成済みSkillを配置しました。`change.diff`を未コミットの変更として適用し、新規ファイルにはintent-to-addを設定しました。依頼文は`case.json`からそのまま使用し、ヒントは加えていません。ユーザー設定は読み込まないようにしました。
- 全実行の記録で、生成済み`SKILL.md`の読み込み成功とGitが表示する差分を確認しました。ここで観察できるのはSkillファイルの読み込みであり、独立した専用のSkill呼び出しイベントではありません。最終出力を`must_report`、`must_not_report`、`prefixes`、`output`と手動で照合しました。ブラインド評価や独立した採点ではありません。
- 最初の試行では評価ログを一時repository内に置いてしまったため、結果を破棄しました。記録対象の29回はログをrepository外に分離して最初から実行したものです。生の実行記録と一時repositoryはコミットしていません。

## 結果

| 項目 | 結果 |
| --- | --- |
| 完了した実行・Skillファイルの読み込み・差分表示 | 各29/29 |
| fixtureの厳密な合格 | 25/29 |
| 必須の`MUST`内容を指摘したcase | 15/15 |
| `kind: negative`で指摘なしの実行 | 7/7（6件のfixtureと日本語の`negative-refactor`） |
| 禁止された指摘 | 観測した範囲で0件 |
| 期待外の追加指摘 | 1件。再試行時の冪等性に関する有効な懸念と分類 |
| 手動確認で明らかに根拠のない補足の事実 | 観測した範囲で0件 |

| case | 言語 | 厳密なfixture結果 |
| --- | --- | --- |
| `better-simplify-guard` | 英語 | 不合格：`BETTER(Simplicity)`の指摘なし |
| `instruction-boundary` | 英語 | 合格 |
| `must-existing-consumer` | 英語 | 合格 |
| `must-focused-risk-variant` | 英語 | 合格 |
| `must-multi-agent-reconciliation` | 英語 | 合格 |
| `must-multi-concern-depth` | 英語 | 合格 |
| `must-same-diff-contract` | 英語 | 合格 |
| `must-shared-handler-variant` | 英語 | 合格 |
| `must-stale-documentation` | 日本語 | 不合格：`MUST(Document)`ではなく`MUST(Functionality)` |
| `must-verified-supporting-evidence` | 英語 | 合格 |
| `negative-go-format` | 英語 | 合格 |
| `negative-go-runtime` | 英語 | 合格 |
| `negative-java-contract` | 英語 | 合格 |
| `negative-optional-label` | 英語 | 合格 |
| `negative-preexisting-defect` | 英語 | 合格 |
| `negative-refactor` | 英語 | 合格 |
| `negative-refactor` | 日本語 | 合格。英語と同じ指摘なしの判断 |
| `nits-change-created-dead-code` | 英語 | 合格 |
| `nits-misspelled-local` | 日本語 | 合格 |
| `nits-project-style` | 英語 | 合格 |
| `positive-pagination` | 英語 | 合格 |
| `realistic-go-directory` | 英語 | 合格 |
| `realistic-java-fulfillment` | 英語 | 合格 |
| `realistic-python-notice-batch` | 英語 | 合格 |
| `realistic-python-profile` | 英語 | 合格 |
| `realistic-python-retry-audit` | 英語 | 合格 |
| `should-ineffective-regression-test` | 英語 | 合格 |
| `should-layer-boundary` | 英語 | 不合格：`SHOULD(Design)`ではなく`MUST(Design)` |
| `should-missing-test` | 英語 | 不合格：期待する`SHOULD(Test)`がなく、別の`MUST(Functionality)`の懸念を指摘 |

## 判断とリリース上の扱い

1. `better-simplify-guard`では挙動を変えない任意の簡素化を見逃しました。fixture上の不合格ですが、欠陥の見逃しや誤検知ではありません。
2. `must-stale-documentation`では、`API_TOKEN`と`SETUP.md`の矛盾という必須内容と`MUST`の対応を指摘しましたが、匿名モードの退行を`Functionality`と捉えました。厳密なprefix不一致は記録に残します。同じ根本原因に対し、どちらの観点も説明可能です。
3. `should-layer-boundary`では依存方向の違反を`MUST(Design)`で指摘しました。fixtureのrepositoryはdomainからUIへ依存しては「must not」と明記しており、強い対応レベルにも根拠があります。期待prefixや過去の得点は後から書き換えません。
4. `should-missing-test`では、成功系だけのテストがtimeout時の再試行と上限到達を検証していない、という期待された指摘を見逃しました。代わりに、任意の`send` callbackが副作用の後でtimeoutした場合に重複実行される、別の具体的な懸念を指摘しました。これは有効な懸念ですが、fixtureのテスト観点を満たすものではありません。実質的な`SHOULD(Test)`の見逃しとして後続対応に残します。

betaの[リスクに基づくチェックリスト](../../docs/RELEASE_CHECKLIST.ja.md)では、観測した不一致に必須の`MUST`欠陥の見逃しや誤検知はありません。ただし、厳密な25/29を完全合格として扱いません。テスト観点の見逃しと分類差を記録に残し、他のリリース条件と合わせて、beta.2で容認するかをメンテナーが最終判断する必要があります。

1モデルによる各1回の実行であり、精度、呼び出し率、誤検知率の推定ではありません。手動採点では根拠のない補足を見落とす可能性があります。29回の使用量は入力約2,164,556トークン（うちキャッシュ約1,784,832）、出力27,455トークンでした。トークン使用量は品質指標ではありません。
