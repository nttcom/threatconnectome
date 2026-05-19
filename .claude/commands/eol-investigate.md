---
description: 指定プロダクトの endoflife.date API データと TC DB の実データを収集し、eol-implement で使う調査レポートを eol-work/ に出力する
argument-hint: <endoflife.date-product-name>
---

# EOL対応プロダクト追加: 調査フェーズ

このコマンドは `/eol-sbom` で SBOM を登録した後に実行する。
`scripts/endoflife2tc.py` への登録と `api/app/business/eol/` 配下のマッチングロジック実装に必要な情報を集め、`eol-work/<product>-report.md` に出力する。**コード変更は行わない**。

## 入力

- プロダクト名: `$ARGUMENTS`
  - **endoflife.date 上のプロダクト名** (例: `nginx`, `django`, `postgres`, `alpine`)。空であればユーザーに確認。
  - 注意: `/add-sbom` で使った SBOM の service 名 (例: `rocky-apache-http-server`) とは別物。endoflife.date が認識する名前を使う。

## 事前確認

着手前に以下を1度だけ確認:

1. `docker ps --format '{{.Names}}'` で `threatconnectome-db-1` が起動していること。なければユーザーに通知して中断。
2. `curl -sSf -o /dev/null -w "%{http_code}" https://endoflife.date/api/v1/products/<product>` が 200 を返すこと。404 の場合はプロダクト名が違う可能性があるので、ユーザーに確認。

## 手順

### 1. endoflife.date からデータ取得

```bash
curl -sS https://endoflife.date/api/v1/products/<product> -o eol-work/<product>-eol.json
```

取得した JSON から以下を抽出してレポートに記載:

- `result.name` — endoflife.date 上のプロダクト名 (`eol_product_list[].product` の候補)
- `result.label` / `result.category` — `product_category` 判定の参考 (os / runtime / middleware / package など)
- `result.releases[0].name` — バージョン文字列の例 (例: `"3.20"`, `"5.0"`, `"22.04"`)
- `result.releases` の最初の3件の `name` を一覧として残す (バージョン形式判定用)

description は API の `result.label` ではなく `https://endoflife.date/<product>` の HTML 先頭段落を採用する。
取得が難しい場合は `result.label` を仮置きし、レポートで「**要レビュー: description は endoflife.date のページから手動コピペ推奨**」と明記する。

### 2. TC DB から実データ抽出

`/add-eol-product` で登録した SBOM が反映されているはず。以下を実行 (`<keyword>` はプロダクト名の部分一致用、必要に応じて短く調整):

```bash
docker compose -f docker-compose-firebase-local.yml exec db psql -U postgres -d postgres -t -A -F'|' -c \
  "SELECT p.name, p.ecosystem, p.type, pv.version FROM package p JOIN packageversion pv ON p.package_id = pv.package_id WHERE p.name ILIKE '%<keyword>%' LIMIT 50;"

docker compose -f docker-compose-firebase-local.yml exec db psql -U postgres -d postgres -t -A -F'|' -c \
  "SELECT DISTINCT ecosystem FROM package WHERE ecosystem ILIKE '%<keyword>%';"
```

結果をレポートに ecosystem 別 (rocky/alpine/ubuntu/pypi/golang/npm) に整理して記載。
ヒット 0 件の ecosystem は「TC側にデータなし (SBOM 未登録 or パッケージ名が違う)」とマークする。

### 3. 判定と推奨マッチングパターンの提示

レポートには以下を**根拠つきで**記載 (実装フェーズの判断材料):

#### (a) `is_ecosystem` 判定
- 第2段の `SELECT DISTINCT ecosystem` で `<product>-X.Y` のような行が返れば → `is_ecosystem: True` (OS型)
- ヒットがなく、`package.name` 側にのみ現れる → `is_ecosystem: False` (Package/Runtime/Middleware型)

#### (b) `product_category` 判定
- OS (alpine, rocky, ubuntu, debian など) → `OS`
- 言語ランタイム (python, nodejs, php, ruby, java) → `RUNTIME`
- DB / Web server / cache (postgresql, redis, sqlite, apache-http-server, nginx) → `MIDDLEWARE`
- ライブラリ / フレームワーク (django, numpy, react, ansible) → `PACKAGE`

#### (c) Package型の場合: ecosystem 別 package_name パターン
1. 抽出した `package.name` を ecosystem 別に列挙
2. 命名規則を推定 (例: PostgreSQL → DEBIAN: `postgresql-<major>`, RPM: `postgresql`, ALPINE: `postgresql<major>`)
3. `PackageFamily.DEBIAN` / `RPM` / `ALPINE` / `PYPI` / `NPM` のどれにマップされるかを記載

#### (d) Package型の場合: version マッチングクラスの選択
- バージョンが endoflife.date 側で `"3"` のように major のみ、TC 側も major のみ → `MajorOnlyVersion`
- endoflife.date 側で `"3.12"` のように major.minor、TC 側も major.minor → `MajorAndMinorVersion`
- 混在 (ansible のように一部リリースが major、一部が major.minor) → `MajorOrMajorAndMinorVersion`

選定理由はレポートに 1〜2 文で明記。

#### (e) Ecosystem型の場合: ecosystem 文字列フォーマット
- TC 側 ecosystem 例: `alpine-3.20`, `rocky-9.4`, `ubuntu-22.04`
- endoflife.date のリリース名と TC 側 ecosystem の suffix のフォーマット差を記載 (例: alpine は `major.minor` の2桁、ubuntu は `YY.MM`)。
- 既存の `EoLAlpineEcosystem` / `EoLRockyEcosystem` / `EoLAlmaLinuxEcosystem` を参考に、必要な前処理 (`split` / `re` など) を提案。

### 4. レポート出力

`eol-work/<product>-report.md` に以下のフォーマットで保存:

```markdown
# EOL Investigation Report: {{product}}

## endoflife.date 情報
- product name (API): {{result.name}}
- product_category (推定): <OS|RUNTIME|MIDDLEWARE|PACKAGE> — 根拠: ...
- description: |
    <endoflife.date HTML 先頭段落、または要レビューの旨>
- releases 例 (上位3件): {{name1}}, {{name2}}, {{name3}}
- バージョン形式: <Major のみ | Major.Minor | 混在>

## TC DB 抽出結果
### ecosystem として登録 (`SELECT DISTINCT ecosystem` のヒット)
- <なし or 一覧>

### package として登録 (`SELECT p.name, p.ecosystem, ...`)
| package.name | package.ecosystem | type | version 例 |
|---|---|---|---|
| ... | ... | ... | ... |

## 判定
- is_ecosystem: <True | False>
- product (TC側キー): <例: rocky-linux / apache-http-server>
- product_category: <Enum>

## Package型の場合: マッチング設計
- 必要な Product クラス: {{product名}}Product.py (新規) or EoLBaseProduct (流用)
- ecosystem 別の package_name 対応:
  - DEBIAN: <package_name パターン>
  - RPM: <package_name パターン>
  - ALPINE: <package_name パターン>
  - PYPI: <package_name パターン>
  - NPM: <package_name パターン>
- version クラス: <MajorOnlyVersion | MajorAndMinorVersion | MajorOrMajorAndMinorVersion>
  - 根拠: ...

## Ecosystem型の場合: マッチング設計
- 既存クラス流用可: <yes/no>
- 新規クラス名: EoL{{Product}}Ecosystem.py
- ecosystem 文字列フォーマット: <例: ubuntu-YY.MM>
- 前処理: <例: 末尾の `.0` を削除 / major.minor のみ抽出>

## 要レビュー / 不明点
- <description の確定>
- <ヒット 0 ecosystem の扱い>
- <その他、判断に迷う点>
```

### 5. 完了報告

ユーザーに以下を1回だけ報告:

```
レポート出力: eol-work/{{product}}-report.md
endoflife.date 取得: OK (releases <件数>件)
TC DB ヒット: ecosystem=<件数>件, package=<件数>件
推定 is_ecosystem: <True|False>
推奨 version クラス: <Major|MajorAndMinor|MajorOrMajorAndMinor> (Package型の場合)

次のステップ: レポートを確認し、問題なければ `/eol-implement <product>` を実行してください。
description やマッチングパターンに修正が必要な場合は、レポートを直接編集してから実装フェーズへ進んでください。
```

## 注意

- このコマンドは**コード変更を一切行わない**。`scripts/endoflife2tc.py` や `api/app/business/eol/` 配下を編集しないこと。
- AGENTS.md `./api` ブロックの静的チェック / テスト実行はこのフェーズでは不要 (コード変更がないため)。
- レポート出力先 `eol-work/<product>-report.md` は `.gitignore` 対象。コミットしないことをユーザーに通知すること。
- `WebFetch` で endoflife.date のページから description を取れる場合は使ってよい。失敗時は API の `label` を仮置きし要レビューマークを付ける。
