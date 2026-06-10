# YouTube動画トランスクリプト取得 & Claude要約システム 設計書

## 概要

YouTube動画のURLを入力として受け取り、トランスクリプト（字幕）を取得し、Claude APIで要約を生成するシステムの設計。

---

## アーキテクチャ候補

### 案A: CLIスクリプト（シンプル構成）

```
[ユーザー] --URL--> [CLIスクリプト]
                        |
                        v
              [transcript取得モジュール]
                        |
                   (transcript text)
                        |
                        v
                  [Claude API呼び出し]
                        |
                   (要約テキスト)
                        |
                        v
                   [stdout / ファイル出力]
```

**特徴:**
- 最小構成。依存ライブラリ少。
- 単発実行に向く。
- Python or Node.js で実装可能。

---

### 案B: Webアプリ（UI付き）

```
[ブラウザ] --URL入力--> [Webフロントエンド]
                              |
                        (HTTP POST)
                              |
                              v
                     [バックエンドAPI (FastAPI / Express)]
                              |
               +--------------+---------------+
               |                              |
    [transcript取得]              [Claude API呼び出し]
               |                              |
           (transcript)               (要約テキスト)
               +------------>-----------------+
                                     |
                               [レスポンス]
                                     |
                              [ブラウザ表示]
```

**特徴:**
- UI付きで非エンジニアも利用可能。
- ストリーミング表示（SSE/WebSocket）で体験向上可能。

---

### 案C: Claude チャットへの直接組み込み（MCP経由）★採用

```
[Claudeチャット / Claude Code]
         |
  (MCP Tool呼び出し: get_youtube_transcript)
         |
         v
[MCPサーバー: server.py (stdio)]
         |
  youtube-transcript-api
         |
  (transcript text 返却)
         |
         v
[Claude がチャット内でそのまま要約]
```

**特徴:**
- Claudeチャット上でシームレスに完結。ユーザーはURLを貼るだけ。
- Claude Code (CLI) では stdio transport でローカル動作。
- Claude.ai Web では Remote MCP (HTTP/SSE) として公開すれば利用可能。
- 要約ロジックはClaudeが担うため、MCPサーバーはtranscript取得のみに専念。

**実装済みファイル:**
- `server.py` — MCP サーバー本体（stdio transport）
- `tests/test_server.py` — ユニットテスト

**ツール仕様:**

| ツール名 | 引数 | 戻り値 |
|---------|------|--------|
| `get_youtube_transcript` | `url: str`, `languages: list[str] = ["ja","en"]` | transcript テキスト |

**Claude Code への登録方法:**

```bash
claude mcp add youtube-transcript \
  uv --directory /path/to/project run python server.py
```

または `~/.claude/settings.json` に直接記述:

```json
{
  "mcpServers": {
    "youtube-transcript": {
      "command": "uv",
      "args": ["--directory", "/Users/koji/src_local/for_claude_youtube_video_pickup", "run", "python", "server.py"]
    }
  }
}
```

**利用例（チャット内）:**
```
ユーザー: https://www.youtube.com/watch?v=XXXXXXXXXXX この動画を要約して
Claude: [get_youtube_transcript ツールを呼び出し]
        → transcript取得後、日本語で要約を返す
```

---

## トランスクリプト取得方法の選択肢

| 方法 | ライブラリ/手段 | 言語 | 備考 |
|------|--------------|------|------|
| YouTube Data API v3 (captions) | googleapis | Python/Node | OAuth必要。コスト発生の可能性 |
| `youtube-transcript-api` | PyPI | Python | 字幕が公開されていれば不要認証。最も手軽 |
| `youtubei.js` | npm | Node.js | 非公式クライアント。比較的安定 |
| `yt-dlp --write-auto-sub` | CLI | - | 自動生成字幕含め取得可能。最も汎用的 |
| Whisper (音声→テキスト) | openai-whisper / faster-whisper | Python | 字幕なし動画にも対応。重い処理 |

**推奨: `youtube-transcript-api` (Python) または `yt-dlp`**
- 認証不要で手軽。自動生成字幕にも対応。

---

## Claude API連携

### 基本プロンプト設計

```
system: あなたは動画コンテンツの要約専門家です。
user: 以下はYouTube動画のトランスクリプトです。
      動画URL: {url}
      
      【要約してください】
      - 動画の主題と結論
      - 主要なポイント（箇条書き3〜5点）
      - 対象視聴者
      
      ---トランスクリプト---
      {transcript}
```

### トークン制限への対応

- 短い動画（〜30分）: そのままClaude に渡す
- 長い動画（30分〜）: チャンク分割 → 各チャンクを要約 → 要約同士を再要約（Map-Reduce）
- モデル推奨: `claude-sonnet-4-6`（コスパ）または `claude-opus-4-8`（高品質）

---

## 推奨実装構成（案A ベース・最短で動かす）

```
youtube-summarizer/
├── summarize.py          # エントリーポイント
├── transcript.py         # transcript取得ロジック
├── claude_client.py      # Claude API呼び出し
├── requirements.txt
└── .env                  # ANTHROPIC_API_KEY
```

### 最小コードフロー

```python
# summarize.py
url = sys.argv[1]
transcript = get_transcript(url)       # transcript.py
summary = summarize_with_claude(transcript, url)  # claude_client.py
print(summary)
```

---

## 将来の拡張ポイント

- 要約結果のキャッシュ（同じ動画を再リクエスト時に高速化）
- 言語指定（日本語要約 / 英語要約）
- 要約スタイル指定（ビジネス向け / 学習ノート形式 / SNS投稿用）
- プレイリスト一括処理
- Obsidian / Notion へのエクスポート

---

## 技術スタック推奨

| 項目 | 推奨 |
|------|------|
| 言語 | Python 3.11+ |
| transcript取得 | `youtube-transcript-api` |
| Claude連携 | `anthropic` SDK (Python) |
| 実行形式（初期） | CLI |
| 将来のUI | Streamlit（最速）または FastAPI + React |

---

*作成日: 2026-06-10*
