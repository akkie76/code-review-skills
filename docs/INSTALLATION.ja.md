# インストールガイド

[English](INSTALLATION.md)

`evidence-code-review` directory全体をインストールします。packageには`SKILL.md`が
必要とするreferenceが含まれます。

`v1.0.0`リリースの正確な内容を取得するため、コピーする前にリリースタグを指定して
cloneします。

```sh
git clone --depth 1 --branch v1.0.0 https://github.com/akkie76/code-review-skills.git
cd code-review-skills
```

インストール前にpackageの内容を確認してください。

## 適用範囲を選ぶ

- 個人単位：現在の端末にある複数プロジェクトで利用する
- プロジェクト単位：1つのリポジトリで利用し、チームと共有できる
- プロジェクト固有ルールはリポジトリの指示へ保存する

## macOSとLinux

Codexの個人単位：

```sh
mkdir -p ~/.codex/skills
cp -R dist/codex/evidence-code-review ~/.codex/skills/
```

Codexのプロジェクト単位：

```sh
mkdir -p /path/to/project/.agents/skills
cp -R dist/codex/evidence-code-review /path/to/project/.agents/skills/
```

Claude Codeの個人単位：

```sh
mkdir -p ~/.claude/skills
cp -R dist/claude-code/evidence-code-review ~/.claude/skills/
```

Claude Codeのプロジェクト単位：

```sh
mkdir -p /path/to/project/.claude/skills
cp -R dist/claude-code/evidence-code-review /path/to/project/.claude/skills/
```

## Windows PowerShell

`<repository>`をこのリポジトリのcheckout pathへ置き換えます。

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force "<repository>\dist\codex\evidence-code-review" "$HOME\.codex\skills\"

New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "<repository>\dist\claude-code\evidence-code-review" "$HOME\.claude\skills\"
```

## 動作確認

インストール後に新しいsessionを開始します。

- Codex：`evidence-code-review Skillを使って作業ツリーをレビューしてください`
- Claude Code：`/evidence-code-review`を実行するか、同じ内容を文章で依頼する

指摘には`MUST(Functionality):`などのプレフィックスが付きます。対応すべき問題が
なければ、コメントを作らず、その旨を回答します。

## 更新

更新対象のrevisionを取得して変更内容を確認し、package directory全体を同じ保存先へ
再度コピーします。プロジェクト固有情報はpackage内ではなくプロジェクトへ保存し、
packageを安全に置き換えられるようにします。

## 削除

選択した個人またはプロジェクトのskills directoryから、インストール済みの
`evidence-code-review` directoryだけを削除し、新しいsessionを開始します。

## トラブル対応

- directory名が`evidence-code-review`で、直下に`SKILL.md`と`references/`があるか確認する
- frontmatterの`name`も`evidence-code-review`か確認する
- 追加・更新後に新しいsessionを開始する
- 明示的に呼び出し、検出の問題とレビュー動作の問題を切り分ける
- managed、safe、restricted modeで個人・プロジェクトSkillが制限されていないか確認する
- 問い合わせ時は製品version、model、repository revision、依頼、実際の結果を記録する
