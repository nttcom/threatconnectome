---
description: 指定されたプロダクトについて、対応する全ecosystem (rocky/alpine/ubuntu/pypi/golang/npm) のSBOMを生成し、Threatconnectome に登録する
argument-hint: <product-name>
---

# EOL対応プロダクト追加: SBOM生成・登録

ユーザーが指定したプロダクト名に対して、対応する全ecosystem (rocky/alpine/ubuntu/pypi/golang/npm) を考慮した検証用SBOMを生成し、Threatconnectomeのローカル環境に登録します。

## 入力

- プロダクト名: `$ARGUMENTS`
  - 空であればユーザーに `endoflife.date` 上のプロダクト名 (例: `nginx`, `django`, `postgres`) を確認する。
- `pteam_id`: ユーザーに確認する (Threatconnectomeに登録済みの対象チームID)。
- `access_token`: ユーザーに確認する (SBOMアップロード用のBearerトークン)。

`AskUserQuestion` ではなく通常のテキスト質問で十分。先に3つまとめて確認してから着手すること。

## 事前確認

着手前に以下を1度だけ確認すること:

1. `docker --version` と `trivy --version` が通ること。通らなければユーザーに通知して中断。
2. Threatconnectomeがローカルで起動していること (`curl -sSf -o /dev/null -w "%{http_code}" http://localhost/api/docs` で疎通だけ確認)。

## 手順

### 1. 対応ecosystemの調査

プロダクトに対応している ecosystem を以下から判定する。判断に迷う場合のみ `WebSearch` を使ってよい。`alpine` と `ubuntu` のように複数該当する場合は**該当する全てを対象**にする。

base image は **OS/runtime レベルの EOL マッチを最大化するため、最近 EOL に達したバージョン** をデフォルトとする。

| ecosystem | パッケージリポジトリ | インストールコマンド (Dockerfileで使用) |
|---|---|---|
| rocky | https://rockylinux.pkgs.org/ | `FROM rockylinux:8` + `RUN dnf install -y <pkg>` |
| alpine | https://pkgs.alpinelinux.org/packages | `FROM alpine:3.18` + `RUN apk add --no-cache <pkg>` |
| ubuntu | https://packages.ubuntu.com/ | `FROM ubuntu:20.04` + `RUN apt-get update && apt-get install -y <pkg>` |
| pypi | https://pypi.org/ | `FROM python:3.9-slim` + `RUN pip install <pkg>` |
| golang | https://pkg.go.dev/ | `FROM golang:1.21` + `RUN go install <module>@latest` (該当する場合のみ) |
| npm | https://www.npmjs.com/ | `FROM node:18` + `RUN npm install -g <pkg>` |

判定結果と理由を箇条書きで先に出力し、対象ecosystemリストを確定する。

**注意**: メジャーブランチが1つしか維持されていない製品 (例: Apache HTTP Server は 2.4 のみ現行) では、どのbase imageでもインストールされる product のバージョンは現行ブランチのものになり、product-level の EOL マッチは発生しない (これは仕様。OS/runtime レベルの EOL マッチは依然発生する)。

### 2. 各ecosystemごとに以下を実行

作業ディレクトリ: `eol-work/<product>-<ecosystem>/` (リポジトリルート直下に作成)。

1. Dockerfile を配置 (上表のインストールコマンドを使用)。
2. `docker build -t sbom-<ecosystem>-<product> eol-work/<product>-<ecosystem>` でイメージビルド。
3. `trivy image --format cyclonedx --output eol-work/trivy-<product>-<ecosystem>.json sbom-<ecosystem>-<product>` でSBOM生成。
4. 生成したJSONを curl で登録:

   ```bash
   curl -X POST \
     "http://localhost/api/pteams/<pteam_id>/upload_sbom_file?service=<ecosystem>-<product>" \
     -H "accept: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -F "file=@eol-work/trivy-<product>-<ecosystem>.json;type=application/json"
   ```

5. `docker rmi sbom-<ecosystem>-<product>` でイメージをクリーンアップ。

各ステップで失敗した場合は、原因を1〜2行で報告して**当該ecosystemのみスキップ**し、他のecosystemは続行する。最後にスキップしたものを集計して報告する。

### 3. 完了報告

以下の形式で1度だけ報告:

```
対応ecosystem: rocky / alpine / ubuntu / ...
成功: <ecosystem名のリスト>
失敗 (スキップ): <ecosystem名と理由>
生成ファイル: eol-work/trivy-<product>-<ecosystem>.json (一覧)
TC登録: <成功したecosystemの service 名>
```

次のステップ (endoflife2tc.py の編集など) は本コマンドの範囲外であることを明記する。

## 注意

- 生成したSBOMファイル (`eol-work/`) はリポジトリにコミットしない (`.gitignore` 対象でなければユーザーに通知)。
- `docker build` や `trivy image` は時間がかかるので、各 ecosystem を**直列**で実行する (Docker daemon の負荷を避ける)。
- pypi / golang / npm のパッケージ名は OS パッケージ名と異なる場合がある (例: `Pillow` → `pip install pillow`)。判断に迷う場合はユーザーに確認する。
