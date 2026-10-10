# 人の判定を取り込む評価

[English](EVALUATION_RUBRIC.md)

形式チェックだけのrunnerと、#24で求める指摘単位の評価をつなぐ手順です。
Skill本体・fixture・過去の得点は変更しません。
メンテナーから**今回の評価を実行する前に合格点80点**が指定されています。

## 固定する範囲と合格条件

`EVALUATION_PLAN.json`で方針を固定します。各エージェントの基本評価は29回です。
現行の全fixtureを既定言語で1回ずつ実行し、`negative-refactor`の日本語を追加します。
反復対象はtypo、古い文書、テスト不足、変更で発生した不使用コード、レイヤー境界、
補足の根拠確認の6ケースを事前に選定し、それぞれ追加で1回実行します。
各エージェント計35回、新規sessionを使い、最大2ケースずつ順番に実行します。

基本得点＝100×厳密に合格した基本評価回数÷予定した基本評価回数です。
Codex・Claude Codeが**それぞれ80点以上**であることが必要です（現行は24/29以上）。
両エージェントの合算、80未満の切り上げ、失敗の除外、最良の再実行の選別、反復結果の
基本得点への追加はしません。基本・反復の全実行と人の判定が完了してから合否を確定します。
反復の合格数・分類差は参考指標で、別の合格点は設けません。少数の選定ケースから
一般的なばらつきを推定しません。

両エージェントで、同じcleanなsource revisionとfixture hashを使います。
明示的なmodel IDとインストールするpackage hashを開始前に固定します。
エージェント別のpackage hashは異なっても、生成元hashは一致する必要があります。
各エージェントのCLI version・固定した権限手順・初期化時に固定するtimeoutは途中で変えません。実行環境、利用できない
runtime、拒否された検証、隔離の制約をローカルの注記と機密情報を除いた報告へ記録します。
Codexのread-onlyは実行を許可し得ますが、Claudeは静的レビュー用の許可一覧です。
これは同一実行能力の比較ではなく、記録した各host構成の比較です。
source・fixture・model・条件を変更する場合は、新しい評価campaignにします。

80点は評価の合格基準であり、**自動的なリリース承認ではありません**。
セキュリティ・データ消失の見逃し、誤検知、その他の未解決リスクには既存のリリース
チェックリストを適用します。高得点でも問題が無害になるわけではなく、#35も自動で閉じません。

## 判定ルール

生の回答、適用したdiff、repositoryの契約、確認したテスト、関連する実行記録を読みます。
期待項目の番号は、固定したcase期待値の0始まりのindexです。文章ではなく、挙動と根拠を照合します。

- `required`：1件以上の`must_report`を根拠とともに示す。indexと実際のprefixを記録し、
  同じ期待項目を重複して数えない。
- `optional`：根拠のある`may_report`。独立コメントでも必須指摘内の補足でもよく、任意項目のindexを記録する。
- `valid_additional`：期待値にはないが独立して妥当な指摘。自動的に誤検知とはせず、必須指摘の代わりにもしない。
- `duplicate`：同じ回答内で原因・条件・影響が重複する指摘。重複でない指摘IDを参照し、検出数や誤検知数を増やさない。
- `unsupported`：根拠不足、架空の挙動、対象外の既存不具合、好みを不具合として述べたもの。
  独立した指摘と、妥当な指摘中の根拠不足の補足文を分けて数える。
- `ambiguous`：根拠や採点入力が足りず判断できない。解決するまで未判定とし、有効・根拠不足へ勝手に振り分けない。

禁止された記述は、`must_not_report`にある根拠不足の補足も含めて`forbidden_matches`へ記録します。
その他の補足の事実は別に記録します。ブラインド採点で除外・置換した内容を説明し、
採点者に見えないファイルは機密情報を除いた一覧・記録と照合してから判断します。

### 回答全体の判定（方針v2）

見出し、prefixの有無、疑問符、「指摘ではない」というラベルではなく、主張と修正要求の内容で判定します。

- 正式な指摘と分けた、未確定の重要な要件についての質問で、前提を確認済み・不具合の主張がないものは
  指摘ではありません。`findings`ではなく`notes`へ記録し、質問の存在だけで負例を不合格にしません。
- 変更していない挙動を対象外と説明する正確で対応不要の注記も指摘ではありません。baselineを読んで確認します。
  修正要求や、今回の変更が原因だという主張は、prefixなし・質問形式でも指摘です。無関係な欠陥は羅列しません。
- 回答全体の事実上の前提・補足を確認します。誤った事実や根拠のない事実の主張は`supporting_claims`の
  `unsupported`へ記録し、判断に必要な採点資料が足りなければ`ambiguous`のままにします。
  断りを付けても架空の関数・ファイル名・挙動を許しません。事実の捏造を伴わない、意図についての本当の
  不確実性はそれだけで根拠不足とはしません。「誤りと証明された主張だけ不合格」へ条件を緩めません。
- `must_not_report`は限定条件も含め意味で照合します。「今回導入した欠陥として報告するな」は、
  正確な対象外注記だけでは該当しません。実際に禁止された主張なら質問形式でも不合格です。

各実行の非公開`grading-context.json`へファイルhashと、除外する`.git/`・エージェントのSkill配置先を記録します。
回答、適用後fixture、baseline、関連ログとともに採点者へ渡します。importはhashを記録し、`grading_exclusions`を
初期設定します。追加の除外・置換は理由を説明してください。除外された基盤ファイルはレビュー環境に存在しなかった
わけではありません。ただし存在だけでは挙動の証明にならず、内容・ログで確認します。
この情報は非公開とし、集計へ出力しません。

### 分類の調整

実行前に、契約と影響から対応要否を決めます。

| ケース | 原則 | v2の期待prefix |
| --- | --- | --- |
| `must-stale-documentation` | token必須化は承認済みだが、setup説明が失敗する起動手順を勧める | `MUST(Document)`を維持 |
| `nits-change-created-dead-code` | 小さなprivate helperが未使用になり、呼び出し・動作影響がない。局所的な削除で再設計ではない | `NITS(Simplicity)`を維持 |
| `should-layer-boundary` | AGENTS.mdがdomainからUIへの依存を明示的に禁止し、承認された例外もない | SHOULDから`MUST(Design)`へ修正 |

最後のcase IDは追跡のため維持します。IDが対応要否を決めるわけではありません。
延期可能な設計上の助言は引き続き`SHOULD`です。以前の結果を再分類しません。
v2の採点基準・Skill・採点資料の変更後は新しい固定campaignが必要です。
Run A／Bを新ルールで再採点せず、改善の試算を実測として扱いません。過去の起動ラベルも当時の根拠のままです。

厳密なケース合格には、必須項目、期待prefix、要求された出力種別、出力契約を満たし、
禁止された記述と根拠不足の指摘・補足がないことが必要です。
内容が有益でもprefix差は不合格のままです。必須コメントはそれぞれ期待prefixを満たす必要があり、
追加・任意コメントのprefixで必須コメントの不一致を補えません。注記の`prefix`は正確な
`ACTION(Viewpoint)`トークン（埋め込んだ補足ならnull）のみとし、本文やローカルパスを入れません。
正例での妥当な追加・任意コメントは減点しません。
負例は、意味のある回答があり、prefixのない不具合の主張も含め指摘がないことが必要です。
正規表現の`explicit_no_findings`を意味的な判定に使いません。

起動の根拠は別に記録します。Claudeは`Skill` toolの要求と、同じIDに対応する成功した`tool_result`が必要です。
要求だけ、エラー、init一覧だけでは足りません。`call_requested`・`call_failed`を起動確認として数えません。
Codexは現在ファイル読み取りまでしか観測できないため、`file_read_observed`を**限定的なアクセスの
根拠として採点に使用しますが、起動確認や因果関係の証明とはしません**。
Skillへのアクセスを観測できない回答をSkillの合格として数えません。

`judgments.json`は未確認状態で作ります。人が各記録を確認し、reviewer識別名、`method: human`を
記入して明示的に確定します。エージェントによる下書きは`method: agent_assisted`とし、未判定のままです。
人の判定を偽装したり、下書きを暗黙に承認したりしません。取り込んだ実行情報は編集しないでください。

## 指摘単位の指標

人が確定した基本評価だけについて、以下を集計します。

- 必須項目の検出（TP）：各実行で検出した、重複しない期待項目indexの件数。
- 必須項目の見逃し（FN）：必須項目の総数から検出数を引いた件数。
- 根拠不足の指摘（FP）：重複でない独立した指摘のうち根拠不足と判断した件数。
- 妥当な追加、任意、重複のコメント：それぞれ別の件数。
- 根拠不足の補足、禁止された記述：それぞれ別の件数。補足の誤りを独立したFPとして増やさない。

これらはバージョン管理した合成fixtureの期待項目に対する件数であり、実世界のprecision／recallではありません。
負例には必須項目がなくTPを増やしません。ケース得点も指摘単位のprecisionではありません。
一部のみの集計では未判定があると明示します。反復は対象caseの基本・追加実行を比較し、
0/2、1/2、2/2の合格数と分類差を示します。
人も見落とし・判断差があり、自動採点者は同系統のmodelや表現・文章量に偏る場合があります。
独立したレビューは有益ですが、メンテナーによる判定を独立評価とは呼びません。

## ローカルでの手順

先にtoolingをcommit・確認します。エディタやGitクライアントが切り替えない専用clone／worktreeを使い、
両エージェント共通の完全なcommit SHAを選びます。以下の`REVISION_SHA`をそのSHAへ置き換えてください。
initと毎回のrunnerに`--revision`を指定すると、独立したobject storeを持つ非公開のdetached cloneを
一時作成し、元checkoutやrefを変更せず実行します。実行中のrunner／scorerの内容はそのrevisionと
一致する必要があり、新しいtoolingで古いcampaignのrevisionを名乗ることはできません。
リポジトリ外の新規ディレクトリを使い、生の回答・注記をcommitしません。

```sh
make eval-score SCORE_ARGS="init --revision REVISION_SHA --timeout 300 --campaign /tmp/evidence-review-campaign --codex-model gpt-6.1-sol --claude-model claude-opus-5-5"
make eval EVAL_ARGS="--revision REVISION_SHA --case negative-go-format --case negative-optional-label --model gpt-6.1-sol --timeout 300 --execute --output-dir /tmp/evidence-review-codex-batch01"
make eval-score SCORE_ARGS="import --campaign /tmp/evidence-review-campaign --summary /tmp/evidence-review-codex-batch01/summary.json --phase primary"
make eval-score SCORE_ARGS="score --campaign /tmp/evidence-review-campaign"
```

各batchは`--execute`なしで事前確認します。事前確認とcampaign初期化はmodelを呼び出しません。
各sessionの前後でHEAD、入力の未コミット状態、fixture hash、package情報を確認します。
変化があれば`input_integrity: failed`とし、影響した実行を`agent_error`にして停止します。
回答が未完了・エラーでもbatchを停止し、準備段階の異常はsession開始前に停止します。
importには検証済みの入力整合性と、timeout・入力方式を含む固定設定の完全一致が必要です。
整合性情報のない古い集計やrevision混在の記録は履歴として保持し、置き換えcampaignには取り込みません。
SHAや設定の書き換え、結果を見て固定条件を緩めることもしません。この手順の変更後は新しい共通revisionで
両エージェントの全件を明示的に再評価します。内容hashだけでの固定と一括実行機能は今回実装しません。

バッチごとに別の出力先を使います。基本評価は`EVALUATION_BATCHES.ja.md`に従い、日本語の負例を追加します。
固定した反復6ケースは各1回実行し、取り込み時に`--phase repeat`を指定します。
エラー、回答未完了、利用枠不足なら停止し、成功した再実行へ自動で置き換えません。
技術的な再実行が必要なら失敗の記録を残し、よい結果の選別ではなく新しいcampaignとしてやり直します。

全caseを2回実行する提案はv2では有効化せず、事前指定の基本29回＋反復6回を維持します。
拡大する場合は実行前にコストと集計方法を合意し、全サンプルを保持して最良結果を選ばないことが必要です。
診断用Run Bを暗黙に2つ目の基本得点としたり、Run Aの失敗と差し替えたりしません。

認証済みのClaude PCでは固定commitをcheckoutし、同じrunnerへ
`--agent claude --model claude-opus-5-5`を指定します。固定前にmodelの利用可否を確認し、
途中で別名・別modelへ変えません。依頼はfixture本文のみで、Skillの明示呼び出しは追加しません。
`summary.json`と参照する生の実行ディレクトリ（`grading-context.json`も含む）を非公開で採点PCへ移すか、同じ固定campaignのコピーを使います。
移動後にローカルでimportすれば、そのPC用の回答の絶対パスを作れます。
revision、model、fixture／package hash、入力の未コミット状態、権限、重複が不整合なら取り込みを拒否します。
importで既存の判定を上書きしません。

集計からは回答本文、注記、reviewer名、ローカルパスを除外します。それでも公開前に内容を確認し、
元の判定ファイルは公開しません。`score`の終了コードは、両エージェントが完了して80点以上なら0、
未完了・基準未達なら1、入力が不正なら2です。
未実行・未判定の得点はnullで、精度0点でも合格でもありません。結果を見て期待値を書き換えません。

明示的な指標と人の判断を組み合わせる設計は、
[OpenAIの評価ガイド](https://developers.openai.com/api/docs/guides/evaluation-best-practices)を参考にしています。
ClaudeのCLIフラグ・権限は[CLI仕様](https://code.claude.com/docs/en/cli-reference)と
[権限仕様](https://code.claude.com/docs/en/permissions)を確認しています。
