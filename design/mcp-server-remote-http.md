# MCPサーバー Remote HTTP 対応設計（claude.ai Web 連携）

## 概要

現状の stdio transport 実装を拡張し、claude.ai Web チャットから接続できる
Streamable HTTP transport に対応するための設計指針。

---

## 現状との差分

| 項目 | 現状（ローカル） | Web対応後 |
|------|----------------|-----------|
| Transport | stdio（サブプロセス） | Streamable HTTP（HTTPS） |
| 起動方法 | Claude Code がプロセス管理 | 常時稼働サーバーとして公開 |
| 認証 | なし | OAuth 2.1 必須 |
| 登録方法 | `.mcp.json` | claude.ai の設定画面でURL登録 |

---

## 変更が必要な箇所

### 1. transport の切り替え対応（server.py）

`mcp.server.fastmcp` を使い、起動引数で stdio / HTTP を切り替えられる構成にする。
ローカル開発は stdio のまま継続できる。

```python
# 起動引数で transport を切り替えるイメージ
if args.transport == "http":
    mcp.run(transport="streamable-http", port=8080)
else:
    asyncio.run(main())  # 現状の stdio
```

### 2. 認証の追加

claude.ai は OAuth 2.1 を要求する。

- **最小構成**: API キー認証（Bearer token）でも動作確認は可能
- **本番構成**: OAuth 2.1 フローの実装が必要（claude.ai UI 上でのフロー対応）

### 3. 依存追加

`uvicorn` と `starlette` はすでに `mcp[cli]` の依存として入っている。
追加が必要なのは OAuth ライブラリ程度（例: `authlib`）。

---

## ホスティング

`localhost` は不可。外部から到達できる HTTPS エンドポイントが必要。

| 選択肢 | 特徴 |
|--------|------|
| Railway / Render | 無料枠あり・デプロイ簡単。初期検証向き |
| Fly.io | 小規模なら無料枠内。CLI デプロイ |
| VPS（さくら・Hetzner 等）+ Caddy | 自由度高い。HTTPS は Caddy が自動管理 |

---

## 推奨実装方針

stdio と HTTP を **同一 `server.py` で両対応** させ、起動引数で切り替える。

```
# ローカル（現状維持）
uv run python server.py

# HTTP モードで起動（デプロイ時）
uv run python server.py --transport http --port 8080
```

これにより：
- ローカルの Claude Code 環境はそのまま動作し続ける
- デプロイ時だけ HTTP モードに切り替わる
- `.mcp.json` はローカル用のまま保持できる

---

## claude.ai への登録手順（HTTP 対応後）

1. サーバーを HTTPS エンドポイントとしてデプロイ
2. claude.ai の設定 → 「Integrations」→ 「Add MCP Server」
3. サーバーの URL を登録
4. OAuth 認証フローを完了

---

*作成日: 2026-06-11*
