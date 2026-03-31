import httpx

from ..config import settings
from ._utils import mock_resource


def search_github(query: str) -> list[dict]:
    if not settings.github_token:
        return _fallback_github(query)

    params = {"q": query, "sort": "stars", "order": "desc", "per_page": settings.retrieval_top_k}
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        with httpx.Client(timeout=settings.http_timeout_seconds) as client:
            response = client.get("https://api.github.com/search/repositories", params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return _fallback_github(query)

    resources: list[dict] = []
    for idx, repo in enumerate(payload.get("items", [])):
        full_name = repo.get("full_name", "GitHub Repo")
        html_url = repo.get("html_url")
        if not html_url:
            continue
        description = repo.get("description") or f"与 {query} 相关的开源仓库。"
        score = max(0.58, 0.94 - idx * 0.07)
        resources.append(
            {
                "type": "github",
                "title": full_name,
                "url": html_url,
                "description": description,
                "source_score": score,
                "why_recommended": "高质量开源项目可直接用于阅读源码与实战参考。",
            }
        )

    return resources or _fallback_github(query)


def _fallback_github(query: str) -> list[dict]:
    return [
        mock_resource(
            rtype="github",
            title=f"GitHub: {query}",
            url="https://github.com/search?q=" + query.replace(" ", "+"),
            description=f"与 {query} 相关的开源仓库搜索结果。",
            score=0.85,
        )
    ]
