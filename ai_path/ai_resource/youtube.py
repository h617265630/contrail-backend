"""
YouTube search tool for video resources.
Uses YouTube Data API v3.
"""

import httpx
import os


def search_youtube(query: str, limit: int = 5) -> list[dict]:
    """
    Search YouTube videos.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of video dictionaries with type, title, url, description, source_score, thumbnail
    """
    youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")

    if not youtube_api_key:
        return _fallback_youtube(query)

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": limit,
        "order": "relevance",
        "key": youtube_api_key,
    }

    try:
        timeout = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
        with httpx.Client(timeout=timeout) as client:
            response = client.get("https://www.googleapis.com/youtube/v3/search", params=params)
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return _fallback_youtube(query)

    items = payload.get("items", [])
    resources: list[dict] = []
    for idx, item in enumerate(items):
        video_id = _safe_get(item, "id", "videoId")
        title = _safe_get(item, "snippet", "title", default="YouTube 视频")
        if not video_id:
            continue
        score = max(0.55, 0.95 - idx * 0.08)
        thumbnail = _safe_get(item, "snippet", "thumbnails", "default", "url") or f"https://img.youtube.com/vi/{video_id}/default.jpg"
        resources.append(
            {
                "type": "youtube",
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "description": f"{title}（YouTube 检索结果）",
                "source_score": score,
                "thumbnail": thumbnail,
                "why_recommended": "视频内容适合阶段性学习，便于快速理解并跟练。",
            }
        )

    return resources or _fallback_youtube(query)


def _fallback_youtube(query: str) -> list[dict]:
    """Fallback when API calls fail - return YouTube search page."""
    from .utils import mock_resource

    return [
        mock_resource(
            rtype="youtube",
            title=f"YouTube: {query}",
            url="https://www.youtube.com/results?search_query=" + query.replace(" ", "+"),
            description=f"与 {query} 相关的视频搜索结果。",
            score=0.82,
        )
    ]


def _safe_get(data: dict, *keys, default=None):
    """Safely get nested values from a dictionary."""
    value = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value
