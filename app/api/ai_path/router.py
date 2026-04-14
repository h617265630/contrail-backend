from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_db_dep
from pydantic import BaseModel, Field

from .service import generate_ai_path_pipeline


router = APIRouter(prefix="/ai-path", tags=["ai-path"])


class AiPathGenerateRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User natural-language goal")
    exclude_urls: list[str] = Field(default_factory=list, description="URLs to exclude from results (for shuffle)")
    # Preferences — passed directly to the ai_path pipeline
    level: str | None = Field(default=None, description="beginner | intermediate | advanced")
    learning_depth: str | None = Field(default=None, description="quick | standard | deep")
    content_type: str | None = Field(default=None, description="video | article | mixed")
    practical_ratio: str | None = Field(default=None, description="theory_first | balanced | practice_first")


class AiPathGenerateResponse(BaseModel):
    data: dict
    warnings: list[str] = Field(default_factory=list)


@router.post("/generate", response_model=AiPathGenerateResponse)
async def generate_ai_path(payload: AiPathGenerateRequest):
    """Generate a learning path using the ai_path pipeline (search → summarise → organize → report)."""
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    try:
        prefs = {
            k: v for k, v in {
                "level": payload.level,
                "learning_depth": payload.learning_depth,
                "content_type": payload.content_type,
                "practical_ratio": payload.practical_ratio,
            }.items()
            if v is not None
        }
        data, warnings = await generate_ai_path_pipeline(query, prefs)
        return AiPathGenerateResponse(data=data, warnings=warnings)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"ai_path pipeline failed: {exc}"
        ) from exc


class AiResourceSearchResponse(BaseModel):
    data: list[dict]          # web / Tavily results
    github_results: list[dict] # GitHub API results
    topic: str


class CachedResultsResponse(BaseModel):
    data: list[dict]
    topic: str
    cached_count: int


def _transform_github_resource(r: dict) -> dict:
    """Transform a search_github result dict to the frontend AiResourceItem schema."""
    return {
        "url": r.get("url", ""),
        "title": r.get("title", ""),
        "description": r.get("description", ""),
        "key_points": [r.get("why_recommended", "")] if r.get("why_recommended") else [],
        "difficulty": "intermediate",
        "resource_type": "repo",
        "learning_stage": "core",
        "estimated_minutes": 30,
        "image": r.get("thumbnail") or None,
    }


@router.post("/search-resources", response_model=AiResourceSearchResponse)
async def search_resources(
    payload: AiPathGenerateRequest,
    db=Depends(get_db_dep),
):
    """Search Tavily (6 results) + GitHub API (6 results) in parallel, return two separate arrays."""
    topic = payload.query.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="query is required")

    try:
        exclude = set(payload.exclude_urls)

        # Run Tavily web search and GitHub API search concurrently (independent)
        tavily_task = _run_tavily_search(topic, exclude)
        github_task = _run_github_api_search(topic, exclude)
        outcomes = await _run_parallel(tavily_task, github_task)

        tavily_raw = outcomes[0] if not isinstance(outcomes[0], Exception) else []
        github_raw = outcomes[1] if not isinstance(outcomes[1], Exception) else []

        # Transform Tavily results → AiResourceItem shape
        tavily_results = [_transform_tavily_resource(r) for r in tavily_raw]

        # Transform GitHub API results → AiResourceItem shape
        github_results = [_transform_github_resource(r) for r in github_raw]

        return AiResourceSearchResponse(
            data=tavily_results,
            github_results=github_results,
            topic=topic,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Resource search failed: {exc}"
        ) from exc


async def _run_parallel(*tasks):
    return await asyncio.gather(*tasks, return_exceptions=True)


async def _run_tavily_search(topic: str, exclude: set[str] | None = None) -> list[dict]:
    """Run Tavily search in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _sync_tavily_search, topic, exclude
    )


def _sync_tavily_search(topic: str, exclude: set[str] | None = None) -> list[dict]:
    """Tavily web search — returns 6 results, filtered of excluded URLs."""
    try:
        from ai_path.ai_resource.github import search_tavily_resources
        results = search_tavily_resources(topic, limit=6)
        if exclude:
            results = [r for r in results if r.get("url") not in exclude]
        return results[:6]
    except Exception:
        return []


async def _run_github_api_search(topic: str, exclude: set[str] | None = None) -> list[dict]:
    """Run GitHub API search in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _sync_github_api_search, topic, exclude
    )


def _sync_github_api_search(topic: str, exclude: set[str] | None = None) -> list[dict]:
    """GitHub API repo search — returns 6 results, filtered of excluded URLs."""
    try:
        from ai_path.ai_resource.github import search_github
        results = search_github(topic, limit=6)
        if exclude:
            results = [r for r in results if r.get("url") not in exclude]
        return results[:6]
    except Exception:
        return []


def _transform_tavily_resource(r: dict) -> dict:
    """Transform a Tavily search result to the frontend AiResourceItem schema."""
    url = r.get("url", "")
    # Infer resource type from URL
    resource_type = "article"
    if "youtube.com" in url or "youtu.be" in url:
        resource_type = "video"
    elif "github.com" in url:
        resource_type = "repo"
    elif any(d in url for d in ["docs.", "/docs/", "documentation"]):
        resource_type = "docs"

    return {
        "url": url,
        "title": r.get("title", ""),
        "description": r.get("description", r.get("content", "")),
        "key_points": [r.get("why_recommended", "")] if r.get("why_recommended") else [],
        "difficulty": "intermediate",
        "resource_type": resource_type,
        "learning_stage": "core",
        "estimated_minutes": 15,
        "image": r.get("thumbnail") or None,
    }


@router.get("/cached-results/{topic}", response_model=CachedResultsResponse)
async def get_cached_results(
    topic: str,
    db=Depends(get_db_dep),
):
    """Return cached search results for a topic without hitting external APIs."""
    topic_clean = topic.strip()
    if not topic_clean:
        raise HTTPException(status_code=400, detail="topic is required")

    from app.curd.resource_summary_cache_curd import ResourceSummaryCacheCURD

    rows = ResourceSummaryCacheCURD.get_multi_by_topic(db, topic=topic_clean, limit=50)
    import json as _json

    results: list[dict] = []
    for hit in rows:
        results.append({
            "url": hit.url,
            "title": hit.title or "",
            "description": hit.summary or "",
            "key_points": _json.loads(hit.key_points) if hit.key_points else [],
            "difficulty": hit.difficulty or "beginner",
            "resource_type": hit.resource_type or "article",
            "learning_stage": hit.learning_stage or "core",
            "estimated_minutes": hit.estimated_minutes or 15,
            "image": hit.image,
        })

    return CachedResultsResponse(data=results, topic=topic_clean, cached_count=len(results))
