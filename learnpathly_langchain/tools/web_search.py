import httpx

from ..config import settings
from ._utils import mock_resource


def search_web(query: str) -> list[dict]:
    if not settings.tavily_api_key:
        return _fallback_web(query)

    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": settings.retrieval_top_k,
    }
    headers = {"Content-Type": "application/json"}

    try:
        with httpx.Client(timeout=settings.http_timeout_seconds) as client:
            response = client.post("https://api.tavily.com/search", json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
    except Exception:
        return _fallback_web(query)

    resources: list[dict] = []
    for idx, item in enumerate(result.get("results", [])):
        title = item.get("title") or f"Web Guide: {query}"
        url = item.get("url")
        if not url:
            continue
        content = item.get("content") or item.get("snippet") or f"与 {query} 相关的教程与官方资料。"
        score = item.get("score")
        normalized_score = float(score) if isinstance(score, (int, float)) else max(0.5, 0.9 - idx * 0.08)
        resources.append(
            {
                "type": "article",
                "title": title,
                "url": url,
                "description": content[:220],
                "source_score": normalized_score,
                "why_recommended": "覆盖文档与教程场景，适合补全知识细节与最佳实践。",
            }
        )

    return resources or _fallback_web(query)


def _fallback_web(query: str) -> list[dict]:
    return [
        mock_resource(
            rtype="article",
            title=f"Web Guide: {query}",
            url="https://duckduckgo.com/?q=" + query.replace(" ", "+"),
            description=f"与 {query} 相关的教程与官方资料入口。",
            score=0.78,
        )
    ]
