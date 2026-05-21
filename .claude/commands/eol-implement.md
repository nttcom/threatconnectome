---
description: endoflife.date APIが管理するproductを指定する。/eol-investigate のレポートに基づき、scripts/endoflife2tc.py への登録と api/app/business/eol/ 配下のマッチングクラスを実装する
argument-hint: [product]
arguments:
  - product
---

# EOL対応プロダクト追加: 実装フェーズ

このコマンドは `/eol-investigate <product>` の後に実行する。
レポート `eol-work/<product>-report.md` を基に、

- `scripts/endoflife2tc.py` の `eol_product_list` 追加
- Package型: `api/app/business/eol/product/$product_product.py` 新規 + `eol_product_factory.py` / `eol_version_factory.py` の case 追加
- Ecosystem型: `api/app/business/eol/ecosystem/eoL_$product_ecosystem.py` 新規 + `eol_ecosystem_factory.py` の case 追加

を実施する。

## 入力

- プロダクト名: `$product`
  - `/eol-investigate` で使ったプロダクト名と一致させる。空なら確認。
- レポートファイル: `eol-work/$product-report.md` (必須)

## 事前確認

着手前にこの順で実施 (失敗時はユーザーに通知して中断):

1. `eol-work/$product-report.md` を `Read` で取得。なければ「先に `/eol-investigate $product` を実行してください」とユーザーに通知して中断。
2. レポートの「判定」「Package型の場合: マッチング設計」または「Ecosystem型の場合: マッチング設計」「要レビュー / 不明点」を**ユーザーに提示し、以下を1メッセージでまとめて確認**:
   - product (TC側キー)
   - product_category (`OS` / `RUNTIME` / `MIDDLEWARE` / `PACKAGE`)
   - description (確定文字列)
   - is_ecosystem (True / False)
   - Package型なら: 新規クラス名 / ecosystem別 package_name パターン / version クラス
   - Ecosystem型なら: 新規クラス名 / ecosystem 文字列フォーマット
   - 「要レビュー」項目に対する回答

   ユーザーから明示的に「OK」「進めて」等の確認が取れるまで**コード変更を始めない**。AGENTS.md `./web` ブロックの External Specification Confirmation Rule と同じ精神で、判断のあいまいさを残さない。

## 手順

### A. `scripts/endoflife2tc.py` への登録

`eol_product_list` (リスト末尾) に1エントリ追加する。
カテゴリ別の既存エントリを真似てフォーマットを揃える (description は ` "..." "..."` で改行、最後にカンマ)。

```python
{
    "product": "$product",
    "threatconnectome": {
        "product_category": ProductCategoryEnum.<CATEGORY>,
        "description": "<確定 description>",
        "is_ecosystem": <True|False>,
    },
},
```

複数行 description は既存エントリ (redis, ansible など) を参考に文字列リテラル連結で書く。

### B-1. Package型の場合 (`is_ecosystem: False`)

#### (a) `<Product>Product` クラスの新規作成

`api/app/business/eol/product/$product_product.py` を作成。クラス名はproductのPascalCase + `Product` (例: `apache-http-server` → `ApacheHttpServerProduct`)。

テンプレート (DjangoProductクラス / PostgresqlProductクラス を参考):

```python
from app.business.eol.version.<VersionClass> import <VersionClass>
from app.detector.package_family import PackageFamily

from .EoLBaseProduct import EoLBaseProduct


class <Product>Product(EoLBaseProduct):
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem

    def match_package(self, package_name: str, package_version: str) -> bool:
        major_version = <VersionClass>(package_version, self.ecosystem).get_versions()[0]
        package_family = PackageFamily.from_registry(self.ecosystem)

        match package_family:
            case PackageFamily.DEBIAN:
                return package_name == "<debian pattern>"
            case PackageFamily.RPM:
                return package_name == "<rpm pattern>"
            case PackageFamily.ALPINE:
                return package_name == "<alpine pattern>"
            case PackageFamily.PYPI:
                return package_name == "<pypi pattern>"
            case _:
                return False
```

- `major_version` 変数は MajorOnly を使う場合の例。MajorAndMinor / MajorOrMajorAndMinor を使う場合や major 値を package_name に埋め込まない場合は、`major_version` の取得行を削除してよい。
- レポートで「TC側にデータなし」と判定された PackageFamily は `case _:` に流すか、文字列マッチでヒットしない値 (`return False`) を返す。`return package_name == "..."` の形を保つこと。

#### (b) `eol_product_factory.py` への case 追加

```python
from .<Product>Product import <Product>Product
```
を import 群に追加 (アルファベット順を保つ)。
`match` 文に case を追加:

```python
case "$product":
    return <Product>Product(ecosystem)
```

`case _:` の手前に挿入する。

#### (c) `eol_version_factory.py` への case 追加

```python
case "$product":
    return <VersionClass>(version_string, ecosystem)
```

既存の case と同じカテゴリ (MajorOnly / MajorAndMinor / MajorOrMajorAndMinor) のグループに追加する。

### B-2. Ecosystem型の場合 (`is_ecosystem: True`)

#### (a) `EoL<Product>Ecosystem クラスの新規作成

`api/app/business/eol/ecosystem/eoL_$product_ecosystem.py` を作成。
シンプルなフォーマットは EoLAlpineEcosystemクラス を参考に、`_get_matching_ecosystem` で TC 側 ecosystem 文字列から比較用に整形する。

```python
from .eoL_base_ecosystem import EoLBaseEcosystem


class EoL<Product>Ecosystem(EoLBaseEcosystem):
    def __init__(self, product: str):
        self.product = product

    def match_ecosystem(self, ecosystem: str, eol_version: str) -> bool:
        matching_ecosystem = EoL<Product>Ecosystem._get_matching_ecosystem(ecosystem)
        return f"<prefix>-{eol_version}" == matching_ecosystem

    @staticmethod
    def _get_matching_ecosystem(ecosystem: str) -> str:
        # TC側 ecosystem 文字列を eol_version と比較できる形に整形する
        ...
        return ecosystem
```

ecosystem 文字列のフォーマット (例: `ubuntu-22.04` のように major.minor を維持するか、`rocky-9` のように major のみに切り詰めるか) はレポートの判定に従う。

#### (b) `eol_ecosystem_factory.py` への case 追加

```python
from .EoL<Product>Ecosystem import EoL<Product>Ecosystem
```
を import 群に追加。
`match` 文に case を追加:

```python
case "<product>":
    return EoL<Product>Ecosystem(product)
```

### C. AGENTS.md `./api` ブロック準拠の事後アクション

以下を順に実行 (失敗時は原因を報告して修正を試みる)。

#### (1) 静的チェック

```bash
cd api
pipenv run black --check --diff ./app
pipenv run ruff check ./app
pipenv run mypy ./app --show-error-codes --no-error-summary
pipenv run codespell ./app
```

`black --check` が失敗した場合のみ `pipenv run black ./app` で整形してから再実行する。

#### (2) テスト実行

- `docker-compose-firebase-local.yml` が起動中なら停止する (テスト用と同居できないため)。
- `docker-compose-firebase-test.yml` の状態を確認:

  ```bash
  docker compose -f docker-compose-firebase-test.yml ps --status running --format '{{.Name}}'
  ```

  - 何も起動していなければこのコマンドで起動:

    ```bash
    docker compose -f docker-compose-firebase-test.yml up -d
    ```
  - 起動していれば触らない。
- テスト実行 (関連テストのみではなく `app/tests/` 全体を流す。EOL マッチングは複数モジュールに影響するため):

  ```bash
  docker compose -f docker-compose-firebase-test.yml exec testapi pytest -s -vv app/tests/
  ```

- テスト中に新規追加した Product / Ecosystem / Version クラスをカバーするテストが落ちた場合は修正する。`api/app/tests/` 配下を確認し、EOL 関連テスト (`test_eol_*.py` などがあれば) も合わせて流す。
- このコマンドで起動した test stack はテスト終了後に停止する (元から起動していた場合は触らない)。

### D. 完了報告

以下のフォーマットで1回だけ報告:

```
変更ファイル:
  - scripts/endoflife2tc.py (eol_product_list に {{product}} 追加)
  - api/app/business/eol/product/$product_product.py (新規) ← Package型のみ
  - api/app/business/eol/product/eol_product_factory.py ← Package型のみ
  - api/app/business/eol/version/eol_version_factory.py ← Package型のみ
  - api/app/business/eol/ecosystem/eoL_$product_ecosystem.py (新規) ← Ecosystem型のみ
  - api/app/business/eol/ecosystem/eol_ecosystem_factory.py ← Ecosystem型のみ

静的チェック: black/ruff/mypy/codespell すべて pass
テスト: pytest app/tests/ → {{pass数}} passed / {{fail数}} failed

次のステップ (本コマンドの範囲外):
  - scripts/endoflife2tc.py を実行して EoL データを TC に登録
  - TC UI の EOL ページで {{product}} がマッチされているか確認
```

## 注意

- AGENTS.md `./api` ブロックに記された Mandatory Actions (テスト更新、静的チェック、テスト実行) は省略しない。
- Frontend 型定義の再生成 (`web/types`, `openapi.json`) は本コマンドの変更範囲では**不要** (`api/app/schemas.py` を変更しないため)。schemas.py を結果的に触ることになった場合のみ、AGENTS.md の「Frontend Type Definitions」節に従って `npm run openapi:update` を回す。
- レポートに記載された「要レビュー / 不明点」が確定する前にコード変更を始めないこと。曖昧な仕様で生成したマッチングロジックは後で必ず手戻りになる (手順書の「対応が難しいプロダクトについては微妙なコードが生成される」)。
- import 文の追加位置はアルファベット順を保つ (既存 factory は基本的にアルファベット順)。
- `match` 文の case 追加位置は既存のグループ (Version factory は MajorOnly / MajorAndMinor / MajorOrMajorAndMinor のブロック) を意識する。
