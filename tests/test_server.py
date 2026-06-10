"""Tests for server.py utility functions."""

import pytest
from server import _extract_video_id


def test_extract_from_watch_url():
    assert _extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_from_short_url():
    assert _extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_from_embed_url():
    assert _extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_bare_id():
    assert _extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_extract_invalid_raises():
    with pytest.raises(ValueError):
        _extract_video_id("https://example.com/notayoutube")
