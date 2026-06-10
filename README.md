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

## 開発

```bash
# テスト実行
uv run pytest

# サーバー単体起動（デバッグ用）
uv run python server.py
```
