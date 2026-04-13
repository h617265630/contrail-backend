from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.deps import get_db_dep
from pydantic import BaseModel, Field

from .service import generate_ai_path_pipeline, search_resources_pipeline


router = APIRouter(prefix="/ai-path", tags=["ai-path"])


class AiPathGenerateRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User natural-language goal")


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
        data, warnings = await generate_ai_path_pipeline(query)
        return AiPathGenerateResponse(data=data, warnings=warnings)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"ai_path pipeline failed: {exc}"
        ) from exc


class AiResourceSearchResponse(BaseModel):
    data: list[dict]
    topic: str


class CachedResultsResponse(BaseModel):
    data: list[dict]
    topic: str
    cached_count: int


@router.post("/search-resources", response_model=AiResourceSearchResponse)
async def search_resources(
    payload: AiPathGenerateRequest,
    db=Depends(get_db_dep),
):
    """Search the web for learning resources on a topic and return summarised cards."""
    topic = payload.query.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="query is required")

    try:
        results = await search_resources_pipeline(topic, max_results=12, db=db)
        return AiResourceSearchResponse(data=results, topic=topic)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Resource search failed: {exc}"
        ) from exc


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
