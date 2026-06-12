---
description: 修正差分を確認し、api/webに変更がある場合だけ該当領域の全チェック・全テストを実行する
argument-hint: [補足メモ]
arguments:
  - 補足メモ
---

# PR前検証

現在のブランチと作業ツリーの差分を確認し、`api` または `web` に変更がある場合だけ、その領域のフル検証を実行する。`$ARGUMENTS` は補足メモとして扱い、検証方針や結果報告に反映してよい。

## 手順

1. **差分把握**: `git status -sb` / `git diff --name-only main...HEAD` / `git diff --name-only` / `git diff --cached --name-only` / `git ls-files --others --exclude-standard` を実行し、変更ファイルを把握する。
2. **対象判定**:
   - `api/` 配下の変更が1件以上あれば API 検証を実行する。
   - `web/` 配下の変更が1件以上あれば Web 検証を実行する。
   - `api/` と `web/` のどちらにも変更がなければ、該当なしとして検証を実行しない。
3. **API 検証**: `api/` に変更がある場合、まず `api/` で静的チェックを実行する。

   ```bash
   cd api
   uv run --locked black --check --diff ./app
   uv run --locked ruff check ./app
   uv run --locked mypy ./app --show-error-codes --no-error-summary
   uv run --locked codespell ./app
   ```

   続けてテスト用スタックを確認する。

   リポジトリルートに戻ってから Docker Compose を操作する。

   - `docker-compose-firebase-local.yml` が起動中なら、テスト前に停止する。
   - `docker-compose-firebase-test.yml` が起動していなければ起動する。すでに起動中なら再起動しない。
   - このコマンドで起動した test stack は検証後に停止する。元から起動していた場合は触らない。

   全APIテストを実行する。

   ```bash
   docker compose -f docker-compose-firebase-test.yml exec testapi pytest -s -vv app/tests/
   ```

4. **Web 検証**: `web/` に変更がある場合、以下を実行する。

   ```bash
   cd ./web
   npm run check
   npm run test
   ```

5. **結果報告**: 実行した検証、pass/fail、失敗時の原因と修正状況を簡潔に報告する。未実行の領域がある場合は、変更がなかったため未実行であることを明記する。

## 注意

- `api/` と `web/` の両方に変更がある場合は、両方の検証を実行する。
- 失敗した検証がある場合は、原因を調査して修正を試み、同じ検証を再実行する。
- API の endpoint signature、request/response schema、field name/type/nullability を変更している場合は、AGENTS.md の OpenAPI 再生成ルールに従い、必要に応じて `web/types` と `openapi.json` を更新してから再検証する。
- 機微ファイル (`.env` 等) が差分に混ざっていたら停止して警告する。
