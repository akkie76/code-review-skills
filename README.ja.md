# Code Review Skills

[English](README.md)

Code Review Skillsは、AIコーディングエージェント向けの、根拠を重視した
コードレビューワークフローです。CodexとClaude Codeで、スタイル上の好みや
根拠のない推測を避けながら、対応すべき不具合を見つけることを支援します。

> **ベータ版:** 現在、レビュー手法と配布形式を検証しています。最初の安定版までに
> 内容を変更する可能性があります。

## できること

- 依頼されたレビュー範囲とリポジトリ固有のルールを確認する
- 変更行だけでなく、変更の影響を受ける処理を追跡する
- リスクに応じて、正しさ、インターフェース、設計、セキュリティ、信頼性、
  テスト、ドキュメントを確認する
- 各指摘に具体的な発生条件と影響を求める
- `MUST(Functionality):`や`BETTER(Simplicity):`のように、対応要否と
  レビュー観点を各コメントのプレフィックスで示す
- 優先度を付けた指摘を日本語または英語で出力する

このSkillはコードをレビューするためのものです。ユーザーが修正も依頼しない限り、
レビュー対象のコードは変更しません。

対応要否、レビュー観点、コミュニケーションルールの詳細は
[レビューコメント規約](docs/REVIEW_COMMENTS.ja.md)を参照してください。

## インストール

このリポジトリをcloneし、利用するエージェント向けの配布物を選択します。

### Codex

ローカル環境の全プロジェクトで利用する場合：

```sh
mkdir -p ~/.codex/skills/code-review
cp dist/codex/code-review/SKILL.md ~/.codex/skills/code-review/SKILL.md
```

特定のリポジトリだけで利用する場合は、そのリポジトリ内の
`.agents/skills/code-review/SKILL.md`へコピーします。インストール後にCodexの
新しいタスクを開始し、diff、commit、branch、Pull Request、または作業ツリーの
レビューを依頼してください。

### Claude Code

ローカル環境の全プロジェクトで利用する場合：

```sh
mkdir -p ~/.claude/skills/code-review
cp dist/claude-code/code-review/SKILL.md ~/.claude/skills/code-review/SKILL.md
```

特定のリポジトリだけで利用する場合は、そのリポジトリ内の
`.claude/skills/code-review/SKILL.md`へコピーします。`/code-review`で明示的に
呼び出すか、Claude Codeへ変更のレビューを依頼してください。

Skillはエージェントへ指示を与えるものです。ほかの実行可能な開発設定と同様に、
内容を確認してからインストールしてください。

## 開発

`src/core/`以下が、ベンダーに依存しないレビュー手法の正本です。`dist/`以下は
生成物であり、直接編集しません。

```sh
make build  # 全エージェント向け配布物を再生成
make check  # frontmatter、リンク、生成物の鮮度を検証
make test   # 上記に加えて行動評価fixtureを検証
```

`make build`はPython標準ライブラリだけを使用し、ネットワーク接続を必要としません。
各エージェントでの手動評価方法は[評価ガイド](tests/README.ja.md)を参照してください。

### プロジェクト固有の技術情報

言語、フレームワーク、SDK、ツールの要件はプロジェクトごとに異なります。正確な
レビューに必要な情報は、インストールしたSkillの`references/technologies/`へ
追加してください。記載形式や詳しさは利用するプロジェクトが決定し、Code Review
Skillsでは技術カタログや固定テンプレートを強制しません。

バージョン制約、ライフサイクルや並行処理のルール、アーキテクチャ上の規約、検証
コマンドなどを記載できます。情報が追加されていない場合、レビューではリポジトリ内の
根拠を調査し、技術固有の保証を推測で補いません。

## プロジェクト方針

現在はメンテナー主導でベータ版を検証しています。事前の合意がないIssueと
Pull Requestは受け付けていません。フィードバック方針は
[SUPPORT.ja.md](SUPPORT.ja.md)、脆弱性の非公開報告については
[SECURITY.ja.md](SECURITY.ja.md)を参照してください。

このリポジトリは独自に執筆した内容で構成しています。参照資料との境界と公開方針は
[docs/CONTENT_POLICY.ja.md](docs/CONTENT_POLICY.ja.md)に記載しています。

## ライセンス

このリポジトリで公開する独自の内容には[MIT License](LICENSE)を適用します。
