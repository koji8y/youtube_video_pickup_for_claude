"""YouTube transcript MCP server."""

import re

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

app = Server("youtube-transcript")


def _extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from URL or return as-is if already an ID."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        m = re.search(pattern, url_or_id)
        if m:
            return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return url_or_id
    raise ValueError(f"YouTube video ID を抽出できませんでした: {url_or_id}")


def _fetch_transcript(video_id: str, languages: list[str]) -> str:
    """Fetch and format transcript text."""
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)

    # 指定言語順に試みて、なければ利用可能な最初のものを使う
    try:
        transcript = transcript_list.find_transcript(languages)
    except NoTranscriptFound:
        transcript = transcript_list.find_transcript(
            [t.language_code for t in transcript_list]
        )

    snippets = transcript.fetch()
    lines = []
    for s in snippets:
        text = s.text.strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_youtube_transcript",
            description=(
                "YouTube動画のトランスクリプト（字幕テキスト）を取得します。"
                "URLまたは動画IDを受け取り、字幕テキストを返します。"
                "字幕が無効または存在しない場合はエラーを返します。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube動画のURL または 動画ID (例: https://www.youtube.com/watch?v=XXXXXXXXXXX)",
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "優先言語コードのリスト (例: ['ja', 'en'])。省略時は ['ja', 'en']",
                        "default": ["ja", "en"],
                    },
                },
                "required": ["url"],
            },
        )
    ]


@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    if name != "get_youtube_transcript":
        raise ValueError(f"Unknown tool: {name}")

    url = arguments["url"]
    languages = arguments.get("languages", ["ja", "en"])

    try:
        video_id = _extract_video_id(url)
    except ValueError as e:
        return [types.TextContent(type="text", text=f"エラー: {e}")]

    try:
        transcript = _fetch_transcript(video_id, languages)
        return [
            types.TextContent(
                type="text",
                text=f"[動画ID: {video_id}]\n\n{transcript}",
            )
        ]
    except TranscriptsDisabled:
        return [types.TextContent(type="text", text=f"エラー: 動画 {video_id} は字幕が無効です。")]
    except NoTranscriptFound:
        return [types.TextContent(type="text", text=f"エラー: 動画 {video_id} に字幕が見つかりません。")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"エラー: {e}")]


async def main() -> None:
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
