# 行動評価

[English](README.md)

この評価では、文章の完全一致を求めずに生成されたSkillの動作を確認します。各caseは
レビュー依頼、リポジトリcontext、patch、観察可能な期待結果で構成されます。

## fixtureの自動検証

次を実行します。

```sh
make test
```

生成物と、各評価caseの構造・内部整合性を検証します。AIサービスは呼び出しません。

## エージェントによる手動評価

CodexとClaude Codeの両方で、caseごとに次を実施します。

1. 評価対象エージェントへ生成済みパッケージをインストールする
2. caseの`repository/`以下を含む隔離された一時リポジトリを作る
3. `change.diff`をcommitせずに適用する
4. `case.json`の各requestを、期待結果のヒントを加えずに送信する
5. `expectations`の全項目を満たすか記録する。文章ではなく挙動と根拠を比較する
6. 他のfixtureのcontextを避けるため、新しい会話で次のcaseを評価する

`must_report`、`must_not_report`、`output`のすべてを満たした場合だけ合格です。追加の
findingはSkillの根拠要件を独立して満たす必要があり、満たさない場合は誤検知として
記録します。

非公開期間中は、日付入りの評価記録をリポジトリ外で管理します。端末固有のパス、
非公開リポジトリの内容、未公開のやり取りを含むmodel transcriptはコミットしません。
