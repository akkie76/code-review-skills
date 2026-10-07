# Codex fixture評価の分割実行

[English](EVALUATION_BATCHES.md)

これは`tests/cases/`の28件に対する基本評価の実行計画です。[80点を基準とする評価](EVALUATION_RUBRIC.ja.md)
では日本語の負例1回と、事前に固定した反復6回を追加します。人による判定の
代替ではありません。各CLI呼び出しを小さくし、利用量を確認してから次へ進むための
ものです。4グループや全28件を並列に実行しないでください。

## 実行前の確認

1. 評価ランナーのレビューを完了し、Skillのcommit、Codex CLIの版、明示的に選んだ
   モデルを記録します。比較する実行ではSkillのrevision、モデル、設定を揃えます。
   未コミット状態とコピーしたSkillの実際のpackage hashも記録します。評価入力に
   ローカル変更がある場合、commitだけでは入力を識別できません。
2. 初回は各caseを1回ずつ実行します。ばらつきの確認が必要なcaseだけ、初回評価後に
   再実行します。各batchは最大2件です。順に実行し、batchごとにアカウントの残り
   利用枠を確認します。
3. `--execute`を付ける前に、対象batchをドライランで確認します。ランナーは
   アカウントの残り利用枠を取得できず、上限に達する前に自動停止できません。
   起動失敗、出力不足、次の実行に必要な利用枠の不足があれば中断します。
4. 生の記録とbatchごとの保存先はリポジトリ外でローカル管理します。集計を公開する
   前に各回答を`case.json`と照合し、機密情報や端末固有の情報を除きます。

最初のbatchは、モデルを呼ばずに次のように確認できます。

```sh
make eval EVAL_ARGS="--revision REVISION_SHA --case negative-go-format --case negative-optional-label --runs 1"
```

エディタやGitクライアントが切り替えない専用clone／worktreeを使います。
`REVISION_SHA`はcampaign初期化時の共通の完全なcommit SHAへ置き換え、毎回`--revision`を指定します。
tooling変更後に過去のcampaignを再利用しません。スナップショットと各sessionの確認で入力変更時に停止します。

対応するモデルを選んだ後、このコマンドへ`--model MODEL_ID --timeout 300 --execute`を追加します。
`MODEL_ID`は実際のCLIモデル名に置き換え、プレースホルダーのまま実行しないで
ください。実行後にランナーが表示する保存先で`summary.json`、各`answer.txt`、
該当する`case.json`を確認してから次へ進みます。Skillの起動確認と、回答がfixtureの
期待値を満たしたかは分けて記録します。ファイルの読み取りやprefixの一致だけで
合格とはしません。

もう一方のエージェントは[Claude Codeの評価手順](README.ja.md)に従い、自動選択を基本に、
明示呼び出しの切り分けを別に記録します。中立な作業場所、固定権限、起動の根拠も記録します。
Codexのread-onlyとClaudeの静的レビュー用許可一覧は異なる設定です。

## 4グループ・各4batch

表の上から順に実行します。後半ほど複雑なcaseを含みます。差分の行数は計画上の
目安にすぎず、トークン消費量を予測できません。初回計画では全fixtureを1回ずつ
含めています。

| グループ | Batch | Case |
| --- | --- | --- |
| 1 — 基本動作 | 1 | `negative-go-format`, `negative-optional-label` |
| 1 — 基本動作 | 2 | `nits-misspelled-local`, `nits-project-style` |
| 1 — 基本動作 | 3 | `must-stale-documentation`, `should-missing-test` |
| 1 — 基本動作 | 4 | `positive-pagination` |
| 2 — 契約・言語 | 1 | `negative-go-runtime`, `negative-java-contract` |
| 2 — 契約・言語 | 2 | `must-focused-risk-variant`, `nits-change-created-dead-code` |
| 2 — 契約・言語 | 3 | `must-existing-consumer`, `realistic-go-directory` |
| 2 — 契約・言語 | 4 | `realistic-java-fulfillment` |
| 3 — ファイル間の挙動 | 1 | `negative-preexisting-defect`, `instruction-boundary` |
| 3 — ファイル間の挙動 | 2 | `must-same-diff-contract`, `must-shared-handler-variant` |
| 3 — ファイル間の挙動 | 3 | `should-ineffective-regression-test`, `realistic-python-profile` |
| 3 — ファイル間の挙動 | 4 | `realistic-python-retry-audit` |
| 4 — 根拠・大きな差分 | 1 | `negative-refactor`, `better-simplify-guard` |
| 4 — 根拠・大きな差分 | 2 | `must-multi-agent-reconciliation`, `must-multi-concern-depth` |
| 4 — 根拠・大きな差分 | 3 | `must-verified-supporting-evidence`, `should-layer-boundary` |
| 4 — 根拠・大きな差分 | 4 | `realistic-python-notice-batch` |

先の`must-stale-documentation`単発スモークテストは、ランナーの検証です。
評価対象のrevisionとモデルを固定した後の初回評価の代わりにはしません。各グループ後に
完了したcase ID、ローカル保存先、エージェントのエラー、トークン使用量、人による
未判定事項を記録します。再実行するcaseを決める前に、prefixだけでなく指摘内容を
照合します。既存の[手動評価記録](RESULT_TEMPLATE.ja.md)を注記に使い、
指摘単位の集計には[ローカルの判定・集計手順](EVALUATION_RUBRIC.ja.md)を使用します。
