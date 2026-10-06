# 行動評価

[English](README.md)

この評価では、文章の完全一致を求めずに生成されたSkillの動作を確認します。各caseは
レビュー依頼、リポジトリcontext、patch、観察可能な期待結果で構成されます。

## fixtureの自動検証

次を実行します。

```sh
make test
```

生成物、公開前の安全検査、パッケージのクリーンアップ、各評価caseの構造・
内部整合性を検証します。AIサービスは呼び出しません。

負例には`false_positive_category`を記録し、抑制したい具体的な誤指摘を
`must_not_report`に記載します。`must_report`と`prefixes`は空、`output`は
`no_findings`である必要があります。`no_findings`の件数ではなく、挙動を保つ
リファクタ、ツールが検査するスタイル、既存不具合、検証済みの言語保証、全呼び出し元を
更新した共有契約という異なる状況を確認します。いずれもOSSからコピーしたコードでは
なく、この評価用に作成した例です。JavaのcaseはJava 17、GoのcaseはGo 1.22と
nilスライスに対する`len`の標準動作を前提とします。fixture検証器はpatchの適用可否を
確認します。CIでは別途`make language-check`を実行し、各patchを隔離された一時
ディレクトリへ適用した後、Java 17のコンパイル、Go 1.22の`gofmt`・`go test`、
Pythonの構文コンパイルを行います。patch適用後のPython fixtureに`test_*.py`が
ある場合は、その単体テストも実行します。実行環境があればローカルでも同じ検査を実行でき、
Goの依存関係のダウンロードは無効です。いずれの検査も、エージェントが実際に
誤検知を抑制するかは検証しません。

Batch 3のfixtureは、リポジトリの契約を示して文書とテスト不足の指摘を評価します。
`must-stale-documentation`では`API_TOKEN`必須化が承認済みの変更であると明記し、
setup guideには匿名モードの説明を残しています。`should-missing-test`では、
冪等な読み取りと再試行の契約を明記し、patchでnull・undefinedの拒否理由を保持します。
既存テストは成功系だけのままです。これらの整理で必須指摘は変更せず、過去の評価結果を
遡って変更しません。実行を比較するときはrevisionを記録してください。

`realistic-go-directory`、`realistic-java-fulfillment`、
`realistic-python-profile`、`realistic-python-retry-audit`、
`realistic-python-notice-batch`は、対応が必要な変更と無関係でもっともらしい変更を
組み合わせたcaseです。再試行と監査のcaseでは、変更された2ファイル間の相互作用を
追跡します。通知の一括送信caseは9ファイル・173変更行のより大きな差分で、
ページング、監査イベント、表示処理のリファクタ、テストをまとめて確認します。
不具合の判断には、送信済み通知がページ間で未送信集合から消えることの追跡が必要です。
これらは評価case間の相対的な差分規模であり、品質の行数基準ではありません。
各`case.json`に言語環境、前提、ファイルをまたいで確認すべき根拠、出典、評価上の限界を
記録しています。5件とも独自に作成した合成例であり、外部OSSの
ソースコードは再配布しません。差分の行数や指摘数で品質を判断せず、
`must_not_report`の候補も含めて各関心事を確認します。既存のJavaScriptのcaseを
含めると、評価セット全体で4言語の実質的な例を扱います。

## 任意実行のCodexローカル評価（自動化の初期段階）

`make test`は引き続きオフラインであり、モデルを呼び出しません。トークンを消費せずに
Codexの実行予定を確認するには、case IDを1つ以上（または明示的に`--all`）指定します。

```sh
make eval EVAL_ARGS="--case negative-refactor --language ja --runs 2"
```

全caseを初回評価する際は、[4グループの分割実行計画](EVALUATION_BATCHES.ja.md)を
使用してください。実際の呼び出しを最大2caseに分け、次のbatchへ進む前に残りの
利用枠を確認します。

言語指定を省略すると、英語依頼があるcaseでは英語、ないcaseでは日本語を選びます。
実際にモデルを呼び出す場合のみ`--execute`を追加します。実行ごとに一時Gitリポジトリを
新規作成し、fixtureの元ファイルと生成済みCodex Skillを`.agents/skills/`へ配置します。
作業場所は中立なランダム名`repo-`、基準commitの作者は`Developer`とし、case IDは
ローカルの結果ディレクトリにのみ使います。patchは未コミットの可視diffとして適用します。
Codexは読み取り専用・非対話・一時sessionで
動作し、sandboxを無効にするオプションは使用しません。`--model`と`--timeout`は任意で、
省略時はローカルCLIの既定モデルと1実行あたり10分の制限を使用します。

出力先は既定でリポジトリ外に作られる新規の非公開ローカルディレクトリです。
`--output-dir`で別の新規ディレクトリも指定できます。場所は実行終了時に表示します。
各実行の`events.jsonl`、`answer.txt`、`stderr.txt`と、集計用の`summary.json`を保存します。
生の記録はコミットせず、共有前に内容を確認し、不要になったらローカルから削除してください。

schema 2の集計は、指定モデルと、CLIの開始イベントまたはstderrのmodel headerで
報告されたモデルを分けて記録します。CLIが情報を出さない場合は`observed_model`を
nullとし、指定しただけのモデルを観測済みとしません。repositoryのrevision、全体の
未コミット状態、評価入力に関係する未コミット状態、Skillの版・生成元hash・実際の
package hashも記録します。各実行では、参照ファイルを含むコピー後のpackageをhash化します。
無関係な未追跡ファイルで`worktree_dirty`だけがtrueになる場合があります。
`evaluation_inputs_dirty`の対象は`src`・`dist`・`tests/cases`とrunnerです。
revisionだけでは未コミットの入力を識別できません。

形式チェックはMarkdown見出し、番号付きリスト、強調、inline codeのタイトルに対応します。
負例の`negative_output_check`は「回答が空でなく、認識した指摘prefixがない」ことだけを示します。
「指摘なし」の文言は`explicit_no_findings`へ別に記録します。prefixのない不具合の主張も
形式チェックを通るため、人の判定が必要です。空の回答は合格にせず、runnerを非zeroで終了します。
これらの変更で過去の集計や評価結果は書き換えません。

設定、case、実行回数、取得可能なtoken利用量、Skill読み取りの根拠も記録します。
同じshell内の後続コマンドが失敗しても、出力にインストール済みSkillの全文があれば
読み取りを確認できます。失敗したコマンドの部分出力だけでは確認しません。
ファイルの読み取りだけではSkillがレビューへ影響した証拠にはならず、レビュー本文は集計に含めません。
Skillの起動確認、指摘の意味的な一致、想定外の指摘の分類、指摘単位の指標、
一般的な精度の算出は**行いません**。生の記録と`case.json`を
人が照合し、起動の有無を別に記録し、想定外の主張を有効・曖昧・重複・根拠不足に
分類してください。判定には下記の手動評価記録を使用します。エージェント実行には
相応のトークンを消費する可能性があるため、事前表示と`--execute`を必須にしています。
これは[Issue #24](https://github.com/akkie76/code-review-skills/issues/24)の初期段階であり、
両エージェントで行うリリース評価の代替ではありません。

## エージェントによる手動評価

CodexとClaude Codeの両方で、caseごとに次を実施します。

1. 評価対象エージェントへ生成済みパッケージをインストールする
2. caseの`repository/`以下を含む隔離された一時リポジトリを作る
3. `change.diff`をcommitせずに適用する。新規ファイルがある場合は、そのファイルに
   `git add -N`を実行し、内容をstageせずに`git diff`へ表示させる
4. `case.json`の各requestを、期待結果のヒントを加えずに送信する
5. `expectations`の全項目を満たすか記録する。文章ではなく挙動と根拠を比較する
6. 他のfixtureのcontextを避けるため、新しい会話で次のcaseを評価する

`must_report`、`must_not_report`、`prefixes`、`output`のすべてを満たした場合だけ
合格です。`may_report`は負例以外で、`output: findings`と1件以上の`must_report`が
ある場合にのみ設定でき、妥当だが任意の指摘を示します。任意の指摘は独立した
コメントでも、必須指摘の本文中で根拠を伴って述べられていても該当します。
`may_report`との一致に独立したコメントは不要です。どちらの形式でも根拠のない
主張は許容されず、必須指摘の欠落を任意の指摘で補うことはできません。それ以外の
追加findingはSkillの根拠要件を独立して満たす必要があり、満たさない場合は誤検知
として記録します。出力がfixtureの期待値に一致したかと、Skillが実際に呼び出されたかは
分けて記録します。Skill未起動での一致は、Skillのレビュー挙動の合格と数えません。
少なくとも1つの負例を、各エージェントで英語と日本語の両方の依頼文により評価します。
fixtureの形式だけから言語間の挙動を推測しないでください。

### Claude Codeの評価手順

同じrevisionのClaude向けpackageを、新規の中立な作業場所の
`.claude/skills/evidence-code-review/`へ配置し、基準commitの作者も中立なものにします。
基本は`implicit`（自動選択）として`case.json`の依頼文だけを送信します。
Skill起動を観測できなかった回だけ、必要に応じて`/evidence-code-review <依頼文>`で
`explicit`（明示呼び出し）の切り分け評価を行います。方式を記録し、両方式を合算しません。

出力の期待値一致とは別に、起動の根拠を記録します。

| エージェント・方式 | 根拠 | 記録する値 |
| --- | --- | --- |
| Claude・implicit | `input.skill == "evidence-code-review"`の`Skill` tool呼び出し | `confirmed`。なければ`not_observed` |
| Claude・explicit | 明示コマンドに加え、initイベントの`skills`一覧に存在 | `by_construction`。起動を直接観測したものではない |
| Codex | CLI記録上のSkillファイル読み取り | `file_read_observed`。起動は`not_verified`のまま |

`references/`の読み取りは補助情報であり、単独で起動の証拠にはしません。
Claudeの`not_observed`で期待出力と一致しても、Skillの合格には数えません。

Claude CLI `2.1.281`の評価では、[PR #44の報告](https://github.com/akkie76/code-review-skills/pull/44#issuecomment-5996575210)
にある、次の非対話・静的レビュー用の固定許可一覧を使いました。

```sh
claude -p "<case.jsonの依頼文>" \
  --setting-sources project --strict-mcp-config --no-session-persistence \
  --allowedTools "Read" "Grep" "Glob" "Skill" \
    "Bash(git diff:*)" "Bash(git status:*)" "Bash(git log:*)" "Bash(git show:*)" \
  --disallowedTools "Edit" "Write" "NotebookEdit" "WebFetch" "WebSearch" \
  --output-format stream-json --verbose
```

インストールしたCLIとアカウントで利用可能なモデルを選び、記録してください。
固定した権限、拒否された検証の試行、CLIが報告した情報も記録します。このClaude手順は
fixtureのコード実行を許可しません。Codexのread-onlyは書き込みを制限しますが、
絞ったPython検証などの実行を許可する場合があり、同じ権限条件ではありません。
結果比較時はこの違いを明記します。`--setting-sources project`だけではユーザー単位の
Skillやmemoryを除外した証明になりません。その制約を記録し、比較条件に必要なら
別途隔離した環境を使用してください。

日付入りで機密情報を除いた評価サマリーは公開リポジトリへ記録できます。
生のmodel transcriptはリポジトリ外で管理し、端末固有のパス、非公開リポジトリの
内容、認証情報、未公開のやり取りはコミットしません。

製品、model、revision、言語、予期しない出力を一貫して記録するため、
[手動評価記録](RESULT_TEMPLATE.ja.md)を使用します。
[2026-10-01の評価サマリー](results/2026-10-01.ja.md)にはCodexの最初の新規
セッション評価を記録しています。[2026-10-02のサマリー](results/2026-10-02.ja.md)には、
Skillが起動しなかった実行とfixture期待値以外に見つかった課題も含め、Claude Codeの
抽出評価を記録しています。
[2026-10-04のCodexリリース候補の部分評価](results/2026-10-04.ja.md)には、
beta.2で選択したcaseの結果と、全件評価ではないという制約を記録しています。
[2026-10-04のCodex全fixture評価](results/2026-10-04-codex-full.ja.md)には、
新規sessionでの29回の実行、厳密な25/29の結果、合格扱いに書き換えていない
4件の逸脱を記録しています。
[2026-10-04のClaude Codeリリース候補の評価](results/2026-10-04-claude.ja.md)には、
全28件と追加の日本語負例1回の結果、および2件のprefix不一致を記録しています。
betaの判断で逸脱を容認しても、厳密な結果は27/29のままです。
[2026-10-06のCodex残りバッチ評価](results/2026-10-06-codex-remaining.ja.md)には、
1つのrevisionでの残り19ケース（厳密な一致16/19）と、検証リスクの指摘条件を
明文化した後のテスト不足の再評価成功を記録しています。分類差と委譲動作未検証の
制約も残しており、最終revisionで全28ケースを揃えた評価ではありません。

## 複数エージェント評価の境界

任意の複数エージェント分解は、実行環境が委譲を許可しているか、および
sub-agentの実行をどのように公開するかに依存します。現在の`case.json`と
`change.diff`によるfixture形式で観察できるのは最終レビュー出力だけです。そのため、
`make test`の成功やfixture数は、委譲、各sub-reviewでの独立した検証、最終的な統合が
実行されたことを示しません。

このガイドは、委譲に対応した実行環境において、複数の独立した関心事を含むdiffで
手動評価します。通常の評価記録に加えて、次を確認します。

- 調整コストに見合わない場合は分解しない
- 各担当reviewerがdiff全体と必要なcontextを確認できる
- 各指摘候補が独立して検証される
- 複雑なfocused checkは調整コストに見合う場合だけ委譲し、検証担当へ1つの具体的な
  主張、その根拠、完全なdiff、確認または反証すべき問いを渡す
- 最終reviewerが担当外の相互作用を確認し、重複、対応要否、観点を統合するとともに、
  検証担当の結論だけを受け入れず、委譲した検証の根拠を確認する
- 統合後の指摘だけが最終出力に含まれる

単一reviewerと分解したreviewerの結果を比較する場合は、新しいsessionを使用し、
diff、依頼、model、Skill revisionを同一にします。見落とした欠陥と誤検知の両方を
記録し、指摘数が多いことだけを改善の根拠にしません。
