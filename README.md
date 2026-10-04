# STEP 800

日本語で使う個人用のTOEIC Part 5・語彙学習アプリです。回答履歴と保存した単語は、このブラウザ内に保存されます。アカウントやクラウド同期はありません。

## 起動

Node.js 22.12以降を用意し、プロジェクトのディレクトリで実行します。外部パッケージのインストールは不要です。

```sh
npm run dev
```

表示された `http://localhost:5173` をブラウザで開きます。終了するときはターミナルで `Ctrl+C` を押します。ビルド済みのアプリを起動する場合は `npm start` を使います（先に `npm run build` を実行してください）。

## スマートフォンで試す

PCとスマートフォンを同じWi-Fiに接続し、次のようにLANからアクセスできる状態で起動します。

```sh
HOST=0.0.0.0 npm run dev
```

PCのLAN内IPアドレスを調べ、スマートフォンで `http://<PCのIPアドレス>:5173` を開きます。ファイアウォールが接続を止める場合は、プライベートネットワークからのアクセスを許可してください。ブラウザのホーム画面追加とService Workerによるオフライン機能にはHTTPSが必要です。公開する場合は、`npm run build` で作成される `dist/` をHTTPS対応の静的ホストへ配置してください。

## GitHub Pagesへ公開

`main`へpushすると、GitHub Actionsが型チェック・テスト・教材検査を実行し、成功後に`dist/`をGitHub Pagesへ公開します。初回のみ、GitHubリポジトリの **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に設定してください。公開先は `https://natchan0807-ai.github.io/toeic_800/` です。手動で再公開する場合は、Actionsタブから「Deploy GitHub Pages」ワークフローを実行します。

## 学習データのバックアップ

「設定・教材について」から学習データをJSONに書き出し、必要なときに同じ画面で読み込めます。読み込み時には現在の学習データが置き換わるため、画面の確認内容に従ってください。ブラウザのデータ消去や別端末への移行に備えて、定期的に書き出してください。

## 開発時の確認

```sh
npm run typecheck
npm test
npm run content:validate
npm run build
```

教材のバッチ・検査・配信数は [docs/content-quality.md](docs/content-quality.md) に記載しています。教材追加の詳細は [docs/content-contract.md](docs/content-contract.md) を参照してください。検査を通過していない教材はアプリの教材マスターへ取り込まれません。
