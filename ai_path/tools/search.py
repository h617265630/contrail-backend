"""
Web search wrapper — supports Tavily and Serper.
Returns List[SearchResult].
"""

from __future__ import annotations
import os
from typing import List

from ai_path.models.schemas import SearchResult

# 跳过视频类域名（这些无法提取文本内容）
_SKIP_DOMAINS_VIDEO = {
    "youtube.com", "youtu.be", "bilibili.com", "vimeo.com",
    "twitch.tv", "dailymotion.com", "coursera.org", "udemy.com",
}


def _is_video_url(url: str) -> bool:
    """检查 URL 是否为视频类资源（无法提取文本）。"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.netloc.lstrip("www.").lower()
        return any(vd in host for vd in _SKIP_DOMAINS_VIDEO)
    except Exception:
        return False


def _search_tavily(query: str, max_results: int = 5) -> List[SearchResult]:
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    # Fetch extra results to account for GitHub URLs being filtered out
    resp = client.search(query, max_results=max_results + 3)
    results = []
    for r in resp.get("results", []):
        url = r.get("url", "")
        # Skip GitHub resources — handled separately via GitHub API
        if "github.com" in url:
            continue
        # Skip video URLs — cannot extract text content
        if _is_video_url(url):
            continue
        results.append(SearchResult(
            url=url,
            title=r.get("title", ""),
            snippet=r.get("content", ""),
            query=query,
        ))
        if len(results) >= max_results:
            break
    return results


def _search_serper(query: str, max_results: int = 5) -> List[SearchResult]:
    import requests
    headers = {
        "X-API-KEY": os.environ["SERPER_API_KEY"],
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": max_results}
    resp = requests.post(
        "https://google.serper.dev/search",
        json=payload,
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    results = []
    for r in data.get("organic", []):
        results.append(SearchResult(
            url=r.get("link", ""),
            title=r.get("title", ""),
            snippet=r.get("snippet", ""),
            query=query,
        ))
    return results


def web_search(query: str, max_results: int = 5) -> List[SearchResult]:
    """Run a single query with the configured search provider."""
    provider = os.getenv("SEARCH_PROVIDER", "tavily").lower()
    if provider == "serper":
        return _search_serper(query, max_results)
    return _search_tavily(query, max_results)
