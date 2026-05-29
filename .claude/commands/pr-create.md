---
description: .github/pull_request_template.md に沿った本文でプルリクを作成する (デフォルト Draft、通常 PR にするには --ready)
argument-hint: [--ready] [補足メモ]
arguments:
  - --ready (任意): 指定すると Draft ではなく review-ready の通常 PR として作成する。未指定時は Draft。
  - 補足メモ (任意): PR 本文に反映したい追加情報 (issue 番号、背景、テストメモ等)。
---

現在のブランチから main への PR を作成する。`$ARGUMENTS` に `--ready` が含まれていれば通常 PR、含まれなければ Draft で作成し、`--ready` を除いた残りを補足メモとして扱う。

## 手順

1. **変更把握**: `git status` / `git diff main...HEAD` / `git log main..HEAD --oneline` / `git status -sb` を並列実行。
2. **テンプレート読込**: Read ツールで `.github/pull_request_template.md` を毎回読み込む。見出し・コメントタグはそのまま、プレースホルダ例は実内容で書き換える。フォーマットはこのコマンドに埋め込まない。
3. **本文ドラフト**: 差分・コミット・補足メモから各セクションを埋める。テストは実施済みのものだけ書く (未実施なら明記)。タイトルは 70 文字以内。署名は付けない。
4. **push**: 未追跡なら `git push -u origin <branch>`、追跡済みなら `git push`。`--force` / `--no-verify` 禁止。
5. **PR 作成**: `gh pr create --base main --title "..." --body "$(cat <<'EOF' ... EOF)"` で作成し、URL を出力。デフォルトは `--draft` を付ける。`--ready` 指定時のみ `--draft` を外す。

## 注意

- 機微ファイル (`.env` 等) が差分に混ざっていたら停止して警告。
- 同名ブランチの PR が既存 (`gh pr view` で確認) なら新規作成せずユーザーに確認。
