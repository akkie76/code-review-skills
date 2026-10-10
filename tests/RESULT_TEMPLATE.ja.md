# 手動評価記録

[English](RESULT_TEMPLATE.md)

- 日付：
- 評価者：
- エージェントと製品version：
- 指定model / CLIが報告したmodel / 根拠の出典：
- Skillのcommitまたはrelease：
- Skillの版 / 生成元hash / 実際のpackage hash：
- 作業ツリー全体の未コミット状態 / 評価入力の未コミット状態：
- case ID：
- 依頼言語：
- 新規session：yes / no
- 呼び出し方式：implicit / explicit
- 起動の根拠：confirmed / call_requested / call_failed / by_construction / file_read_observed / not_observed
- Skill呼び出し：yes / no / 未確認
- tool権限 / fixtureコードの実行を許可したか：
- 拒否された検証の試行 / 環境隔離の制約：
- fixture期待値：pass / fail
- Skillの挙動評価（呼び出された場合）：pass / fail / 制約あり
- 期待するprefixを確認：
- 必須の動作を確認：
- 禁止する動作を確認：
- 追加コメント：
- 指摘でない質問／対象外注記と、確認した事実上の前提：
- 予期しない出力の分類：valid / ambiguous / false positive
- campaignのmanifest hash / 区分（primary・repeat）：
- 検出した必須項目index / 見逃した項目：
- 任意 / 妥当な追加 / 重複 / 根拠不足の指摘：
- 根拠不足の補足 / 禁止された期待項目index：
- 人による確定 / reviewer / 未確定の判定：
- 採点入力 / 除外ファイル / 置換内容：
- 非公開grading-contextの一覧／hash／除外した基盤ファイル：
- 採点入力の除外による未確定の主張 / 照合した根拠：
- follow-up：

出力の一致、起動の根拠、形式チェックは別々に記録します。ファイル読み取りは
専用のSkill toolイベントより弱い根拠です。implicitとexplicitの結果を合算せず、
未コミットの入力を記録したcommitだけに紐づけないでください。

公開予定の記録には、非公開リポジトリの内容、認証情報、個人情報、未公開のやり取りを
含めないでください。
