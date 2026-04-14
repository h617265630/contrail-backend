"""
AIPathService — wraps the ai_path LangGraph pipeline for use by the FastAPI router.
Handles async pipeline invocation and output transformation.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

# Ensure ai_path is importable by adding the project root to sys.path
# __file__ = backend/app/api/ai_path/service.py
# parents: 0=ai_path/, 1=api/, 2=app/, 3=backend/, 4=project root
_AI_PATH_ROOT = Path(__file__).resolve().parents[4]
if str(_AI_PATH_ROOT) not in sys.path:
    sys.path.insert(0, str(_AI_PATH_ROOT))

# Load ai_path/.env so API keys are available before importing ai_path modules
from dotenv import load_dotenv
load_dotenv(_AI_PATH_ROOT / "ai_path" / ".env")

from ai_path.pipeline import build_graph  # noqa: E402
from ai_path.models.schemas import PipelineState  # noqa: E402


# ── Defaults ─────────────────────────────────────────────────────────────────

_DEFAULT_LEVEL = "beginner"
_DEFAULT_LEARNING_DEPTH = "standard"
_DEFAULT_CONTENT_TYPE = "mixed"
_DEFAULT_RESOURCE_COUNT = "standard"
_DEFAULT_PRACTICAL_RATIO = "balanced"

_VALID_LEVELS = {"beginner", "intermediate", "advanced"}
_VALID_DEPTHS = {"quick", "standard", "deep"}
_VALID_CONTENT = {"video", "article", "mixed"}
_VALID_RATIOS = {"theory_first", "balanced", "practice_first"}


def _sanitize(prefs: dict[str, Any] | None) -> dict[str, str]:
    """Filter and validate preference keys/values."""
    if not prefs:
        return {}
    return {
        k: v for k, v in prefs.items()
        if v and (
            (k == "level" and v in _VALID_LEVELS)
            or (k == "learning_depth" and v in _VALID_DEPTHS)
            or (k == "content_type" and v in _VALID_CONTENT)
            or (k == "practical_ratio" and v in _VALID_RATIOS)
        )
    }


# ── Output transformation ──────────────────────────────────────────────────────

def _transform_learning_path_to_nodes(data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Transform ai_path LearningPath → frontend AiPathNode[].

    ai_path LearningPath:
      { topic, level, overview, total_duration_hours,
        sections: [{ title, description, learning_goals, resources: [ResourceSummary], order }] }

    ResourceSummary:
      { url, title, summary, key_points, difficulty,
        resource_type, learning_stage, estimated_minutes }
    """
    nodes: list[dict[str, Any]] = []

    for sec in data.get("sections", []):
        # Build resource list
        resources: list[dict[str, Any]] = []
        for res in sec.get("resources", []):
            if isinstance(res, dict):
                resources.append({
                    "url": res.get("url", ""),
                    "title": res.get("title", ""),
                    "description": res.get("summary", ""),
                })
            else:
                # Pydantic model
                resources.append({
                    "url": getattr(res, "url", ""),
                    "title": getattr(res, "title", ""),
                    "description": getattr(getattr(res, "summary", ""), "summary", ""),
                })

        # Build sub_nodes from learning_goals grouped by difficulty/learning_stage
        # Group key_points into sub_nodes (one sub_node per key_point as a simplification)
        sub_nodes: list[dict[str, Any]] = []
        learning_goals: list[str] = sec.get("learning_goals", [])
        for idx, goal in enumerate(learning_goals):
            sub_nodes.append({
                "title": goal,
                "description": f"Goal {idx + 1} of section '{sec.get('title', '')}'",
                "learning_points": [goal],
                "resources": [],
            })

        nodes.append({
            "title": sec.get("title", ""),
            "description": sec.get("description", ""),
            "learning_points": learning_goals,
            "resources": resources,
            "sub_nodes": sub_nodes,
            "order": sec.get("order", len(nodes) + 1),
        })

    return nodes


def _build_recommendations(data: dict[str, Any], warnings: list[str]) -> list[str]:
    """Build recommendations from path metadata."""
    recs: list[str] = []
    duration = data.get("total_duration_hours")
    if duration:
        recs.append(f"Estimated total time: ~{duration:.1f} hours")
    level = data.get("level", "")
    if level:
        recs.append(f"Designed for: {level} level")
    return recs


# ── Main service ───────────────────────────────────────────────────────────────

async def generate_ai_path_pipeline(
    query: str,
    preferences: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """
    Run the ai_path LangGraph pipeline and return transformed data + warnings.

    preferences may contain: level, learning_depth, content_type, practical_ratio.
    Unknown or invalid keys/values are silently dropped by _sanitize().

    Returns (data, warnings) where data matches AiPathGenerateResponse.data shape.
    """
    graph = build_graph()
    clean = _sanitize(preferences)
    initial: PipelineState = {
        "topic": query,
        "level": clean.get("level", _DEFAULT_LEVEL),
        "learning_depth": clean.get("learning_depth", _DEFAULT_LEARNING_DEPTH),
        "content_type": clean.get("content_type", _DEFAULT_CONTENT_TYPE),
        "resource_count": _DEFAULT_RESOURCE_COUNT,
        "practical_ratio": clean.get("practical_ratio", _DEFAULT_PRACTICAL_RATIO),
        "current_stage": "search",
    }

    result: dict[str, Any] = {}
    warnings: list[str] = []

    async for event in graph.astream_events(initial, version="v2"):
        if event["event"] == "on_chain_end":
            output = event.get("data", {}).get("output", {})
            if isinstance(output, dict):
                if output.get("current_stage"):
                    result["_stage"] = output["current_stage"]
                if output.get("queries"):
                    result["_n_queries"] = len(output["queries"])
                if output.get("search_results"):
                    result["_n_results"] = len(output["search_results"])
                if output.get("fetched_pages"):
                    result["_n_pages"] = len(output["fetched_pages"])
                if output.get("summaries"):
                    result["_n_summaries"] = len(output["summaries"])
                if output.get("error"):
                    result["_error"] = output["error"]
                if output.get("final_report"):
                    result["final_report"] = output["final_report"]
                if output.get("learning_path"):
                    result["learning_path"] = output["learning_path"]

    # Check for error
    if result.get("_error"):
        raise RuntimeError(result["_error"])

    # Extract data
    lp_data: dict[str, Any] = {}
    if result.get("learning_path"):
        lp = result["learning_path"]
        if hasattr(lp, "model_dump"):
            lp_data = lp.model_dump()
        elif hasattr(lp, "dict"):
            lp_data = lp.dict()
        else:
            lp_data = dict(lp)

    # Build stage explanations (reuse existing prompt logic)
    nodes = _transform_learning_path_to_nodes(lp_data)
    _enrich_nodes_explanations(nodes, query)

    topic = lp_data.get("topic", query)
    overview = lp_data.get("overview", result.get("final_report", ""))
    final_report = result.get("final_report", "")

    # Combine overview + final report as summary
    summary = overview or (final_report[:300] if final_report else "")

    data = {
        "title": topic,
        "summary": summary,
        "nodes": nodes,
        "recommendations": _build_recommendations(lp_data, warnings),
        "_raw": {
            "total_duration_hours": lp_data.get("total_duration_hours"),
            "level": lp_data.get("level"),
            "final_report": final_report,
        },
    }

    # Add metrics as warnings
    if result.get("_n_queries"):
        warnings.append(f"Generated {result['_n_queries']} search queries")
    if result.get("_n_results"):
        warnings.append(f"Found {result['_n_results']} web results")
    if result.get("_n_pages"):
        warnings.append(f"Fetched {result['_n_pages']} pages")
    if result.get("_n_summaries"):
        warnings.append(f"Summarised {result['_n_summaries']} resources")

    return data, warnings


def _enrich_nodes_explanations(nodes: list[dict[str, Any]], query: str) -> None:
    """
    Add explanation and tutorial to each node in-place.
    Reuses prompt logic from the existing prompts.py stage explanations.
    """
    try:
        from .prompts import (  # noqa: E402
            AI_AGENT_STAGE_EXPLANATIONS,
            AI_AGENT_STAGE_TUTORIALS,
            GENERIC_STAGE_EXPLANATION,
            GENERIC_STAGE_TUTORIAL,
        )
    except ImportError:
        # Fallback: use generic explanation
        for idx, node in enumerate(nodes):
            if not node.get("explanation"):
                node["explanation"] = (
                    f"阶段 {idx + 1}「{node.get('title', '')}」"
                    f"将围绕你的目标「{query}」展开。"
                    f"建议按步骤系统学习，完成每个学习目标。"
                )
            if not node.get("tutorial"):
                node["tutorial"] = [
                    f"步骤{i+1}：理解核心概念并完成相关练习"
                    for i in range(5)
                ]
        return

    for idx, node in enumerate(nodes):
        stage_order = node.get("order", idx + 1)
        stage_title = node.get("title", f"阶段 {stage_order}")
        stage_desc = node.get("description", "")

        explanation = _build_node_explanation(
            query, stage_title, stage_desc, stage_order
        )
        tutorial = _build_node_tutorial(stage_title, stage_desc, stage_order)

        node["explanation"] = explanation
        node["tutorial"] = tutorial


def _build_node_explanation(
    query: str, stage_title: str, stage_desc: str, stage_order: int
) -> str:
    from . import prompts  # noqa: E402

    key = None
    lowered = stage_title.lower()
    for category, config in prompts.AI_AGENT_STAGE_EXPLANATIONS.items():
        for keyword in config["keywords"]:
            if keyword in lowered:
                key = category
                break
        if key:
            break

    if key and key in prompts.AI_AGENT_STAGE_EXPLANATIONS:
        body = prompts.AI_AGENT_STAGE_EXPLANATIONS[key]["body"]
    else:
        base_desc = stage_desc.strip()
        body = (
            f"本阶段重点是：{base_desc or f'围绕 {stage_title} 建立可落地的理解与实践能力。'}"
            f" {prompts.GENERIC_STAGE_EXPLANATION}"
        )

    return f"阶段 {stage_order}「{stage_title}」将围绕你的目标「{query}」展开。{body}"


def _build_node_tutorial(
    stage_title: str, stage_desc: str, stage_order: int
) -> list[str]:
    from . import prompts  # noqa: E402

    key = None
    lowered = (stage_title + " " + stage_desc).lower()
    for category in prompts.AI_AGENT_STAGE_EXPLANATIONS:
        for keyword in prompts.AI_AGENT_STAGE_EXPLANATIONS[category]["keywords"]:
            if keyword in lowered:
                key = category
                break
        if key:
            break

    if key and key in prompts.AI_AGENT_STAGE_TUTORIALS:
        return [
            step.format(stage_title=stage_title, stage_order=stage_order)
            for step in prompts.AI_AGENT_STAGE_TUTORIALS[key]
        ]

    desc = stage_desc.strip() or f"学习 {stage_title} 的基础知识"
    return [
        step.format(stage_title=stage_title, stage_order=stage_order, desc=desc)
        for step in prompts.GENERIC_STAGE_TUTORIAL
    ]


# ── Resource search (standalone, no learning path) ─────────────────────────────

async def search_resources_pipeline(
    topic: str,
    max_results: int = 10,
    db=None,
    exclude_urls: list[str] | None = None,
) -> list[dict]:
    """
    Search for web resources on a given topic and return summarised results.
    Stages: generate_queries → search_web → fetch_pages → summarize_resources

    If db is provided, results are cached by (url, topic) to avoid re-fetching
    and re-summarizing the same URLs within the same topic.

    If exclude_urls is provided, those URLs are filtered from results.
    """
    # Import pipeline stages lazily to avoid circular imports at module load
    from ai_path.pipeline.queries import generate_queries
    from ai_path.pipeline.search import search_web
    from ai_path.pipeline.fetch import fetch_pages
    from ai_path.pipeline.summarize import summarize_resources
    from ai_path.models.schemas import PipelineState

    initial: PipelineState = {
        "topic": topic,
        "level": _DEFAULT_LEVEL,
        "learning_depth": _DEFAULT_LEARNING_DEPTH,
        "content_type": _DEFAULT_CONTENT_TYPE,
        "resource_count": _DEFAULT_RESOURCE_COUNT,
        "practical_ratio": _DEFAULT_PRACTICAL_RATIO,
        "current_stage": "search",
        "exclude_urls": list(exclude_urls) if exclude_urls else [],
    }

    # Run query generation
    state = await generate_queries(initial)

    # Run web search
    state = await search_web(state)

    # Run page fetch
    state = await fetch_pages(state)

    # ── Cache layer: check which pages are already cached ──────────────────────
    uncached_pages = []
    cached_results: list[dict] = []
    exclude_set = set(exclude_urls or [])

    if db is not None:
        from app.curd.resource_summary_cache_curd import ResourceSummaryCacheCURD

        for page in state.get("fetched_pages", []):
            # Skip excluded URLs even if cached
            if page.url in exclude_set:
                continue
            hit = ResourceSummaryCacheCURD.get(db, url=page.url, topic=topic)
            if hit:
                import json as _json
                cached_results.append({
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
            else:
                uncached_pages.append(page)

        # Only summarize uncached pages
        state["fetched_pages"] = uncached_pages

    # Run summarisation (only for uncached pages)
    state = await summarize_resources(state)

    # Collect newly summarised results
    new_results: list[dict] = []
    for s in state.get("summaries", []):
        if hasattr(s, "model_dump"):
            d = s.model_dump()
        elif hasattr(s, "dict"):
            d = s.dict()
        else:
            d = dict(s)
        new_results.append({
            "url": d.get("url", ""),
            "title": d.get("title", ""),
            "description": d.get("summary", ""),
            "key_points": d.get("key_points", []),
            "difficulty": d.get("difficulty", "beginner"),
            "resource_type": d.get("resource_type", "article"),
            "learning_stage": d.get("learning_stage", "core"),
            "estimated_minutes": d.get("estimated_minutes", 15),
            "image": d.get("image") or None,
        })

    # ── Write new results to cache ─────────────────────────────────────────────
    if db is not None and new_results:
        from app.curd.resource_summary_cache_curd import ResourceSummaryCacheCURD

        for r in new_results:
            ResourceSummaryCacheCURD.upsert(
                db,
                url=r["url"],
                topic=topic,
                title=r["title"],
                summary=r["description"],
                key_points=r["key_points"],
                difficulty=r["difficulty"],
                resource_type=r["resource_type"],
                learning_stage=r["learning_stage"],
                estimated_minutes=r["estimated_minutes"],
                image=r.get("image"),
            )
        db.commit()

    # Combine cached + new results
    result = cached_results + new_results
    return result[:max_results]
