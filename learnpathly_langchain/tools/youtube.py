import httpx

from ..config import settings
from ._utils import mock_resource, safe_get


def search_youtube(query: str) -> list[dict]:
    if not settings.youtube_api_key:
        return _fallback_youtube(query)

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": settings.retrieval_top_k,
        "order": "relevance",
        "key": settings.youtube_api_key,
    }

    try:
        with httpx.Client(timeout=settings.http_timeout_seconds) as client:
            response = client.get("https://www.googleapis.com/youtube/v3/search", params=params)
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return _fallback_youtube(query)

    items = payload.get("items", [])
    resources: list[dict] = []
    for idx, item in enumerate(items):
        video_id = safe_get(item, "id", "videoId")
        title = safe_get(item, "snippet", "title", default="YouTube 视频")
        if not video_id:
            continue
        score = max(0.55, 0.95 - idx * 0.08)
        resources.append(
            {
                "type": "youtube",
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "description": f"{title}（YouTube 检索结果）",
                "source_score": score,
                "why_recommended": "视频内容适合阶段性学习，便于快速理解并跟练。",
            }
        )

    return resources or _fallback_youtube(query)


def _fallback_youtube(query: str) -> list[dict]:
    return [
        mock_resource(
            rtype="youtube",
            title=f"YouTube: {query}",
            url="https://www.youtube.com/results?search_query=" + query.replace(" ", "+"),
            description=f"与 {query} 相关的视频搜索结果。",
            score=0.82,
        )
    ]
