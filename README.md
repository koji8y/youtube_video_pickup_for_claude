# YouTube Video Transcript Summarizer (MCP)

YouTube動画のトランスクリプトを取得し、Claude チャット上でそのまま要約させる MCP サーバー。

## セットアップ

### 依存インストール

```bash
uv sync
```

### Claude Code への登録

プロジェクトルートに `.mcp.json` が含まれているため、このディレクトリで Claude Code を起動すると自動的に `youtube-transcript` MCP サーバーが読み込まれます。

初回起動時に MCP サーバーの承認プロンプトが表示されるので、許可してください。

## 使い方

Claude Code のチャットで YouTube URL を貼り付けて要約を依頼するだけです。

```
この動画を日本語で要約して
https://www.youtube.com/watch?v=XXXXXXXXXXX
```

Claude が自動で `get_youtube_transcript` ツールを呼び出してトランスクリプトを取得し、要約を返します。

### ツール仕様

MCP ツール名: `get_youtube_transcript`

| 引数 | 型 | 必須 | 説明 |
|------|----|------|------|
| `url` | string | yes | YouTube URL または動画ID |
| `languages` | string[] | no | 優先言語コード（デフォルト: `["ja", "en"]`） |

対応 URL 形式:
- `https://www.youtube.com/watch?v=XXXXXXXXXXX`
- `https://youtu.be/XXXXXXXXXXX`
- `https://www.youtube.com/embed/XXXXXXXXXXX`
- 動画ID のみ（例: `dQw4w9WgXcQ`）

### 注意事項

- 字幕（自動生成含む）が存在しない動画はトランスクリプトを取得できません
- 字幕が無効に設定されている動画も同様です

## LibreChat（ローカル Web UI）で使う

Docker Compose でローカルに LibreChat を立ち上げ、Web チャット上で YouTube 要約を使う方法。

### 1. 環境変数ファイルを用意する

```bash
cp .env.example .env
```

`.env` を編集し、少なくとも以下を設定する:

| 変数 | 説明 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API キー |
| `JWT_SECRET` | 任意の長いランダム文字列 |
| `JWT_REFRESH_SECRET` | 別の任意の長いランダム文字列 |

### 2. 起動

```bash
docker compose up -d
```

初回はイメージのビルド・ pull が走るため数分かかる。

### 3. アクセス

ブラウザで `http://localhost:3080` を開く。アカウントを作成してログインすると、Claude モデルと `youtube-transcript` MCP ツールが使える状態になっている。

### サービス構成

```
[ブラウザ :3080]
      ↓
[LibreChat コンテナ]  →  Anthropic API
      ↓ SSE (MCP)
[mcp-youtube コンテナ :8080]
      ↓
[youtube-transcript-api]
```

### 停止

```bash
docker compose down
```

---

## 開発

```bash
# テスト実行
uv run pytest

# stdio モードで起動（Claude Code 用）
uv run python server.py

# SSE モードで起動（Docker/手動確認用）
uv run python server.py --transport sse --port 8080
```
