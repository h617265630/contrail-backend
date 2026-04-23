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

from ai_path.pipeline import run_workflow, run_step1, run_step2, run_step3  # noqa: E402
from ai_path.utils.llm import get_llm  # noqa: E402


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




async def generate_ai_path_outline(
    query: str,
    preferences: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """
    Run Step 1 only (merged with Step 2 - generates outline with sub_nodes in one call).
    Much faster than Step 1 + Step 2 separately.

    Returns (data, warnings) matching AiPathGenerateResponse.data shape.
    """
    clean = _sanitize(preferences)

    warnings: list[str] = []

    # ── Step 1: Generate outline with sub_nodes (merged Step 1 + Step 2) ────────
    step1_result = await run_step1(
        topic=query,
        level=clean.get("level", _DEFAULT_LEVEL),
        learning_depth=clean.get("learning_depth", _DEFAULT_LEARNING_DEPTH),
        content_type=clean.get("content_type", _DEFAULT_CONTENT_TYPE),
        practical_ratio=clean.get("practical_ratio", _DEFAULT_PRACTICAL_RATIO),
        resource_count=_DEFAULT_RESOURCE_COUNT,
    )

    if step1_result.get("search_results"):
        warnings.append(f"Found {len(step1_result['search_results'])} web results")

    # Extract outline (already contains sub_nodes)
    outline = step1_result.get("outline")
    if hasattr(outline, "model_dump"):
        outline_data = outline.model_dump()
    elif isinstance(outline, dict):
        outline_data = outline
    else:
        outline_data = {}

    warnings.append(f"Generated {len(outline_data.get('sections', []))} sections with sub_nodes")

    # Build nodes directly from outline (no Step 2 needed)
    nodes = []
    for sec in outline_data.get("sections", []):
        # Build sub_nodes from section's sub_nodes field
        sub_nodes = []
        for sub in sec.get("sub_nodes", []):
            if isinstance(sub, dict):
                sub_nodes.append({
                    "title": sub.get("title", ""),
                    "description": sub.get("description", ""),
                    "learning_points": sub.get("key_points", []),
                    "resources": [],
                })

        nodes.append({
            "title": sec.get("title", ""),
            "description": sec.get("description", ""),
            "learning_points": sec.get("learning_goals", []),
            "resources": [],
            "sub_nodes": sub_nodes,
            "order": sec.get("order", len(nodes)),
        })

    # Build overview text
    overview = outline_data.get("overview", "") or f"关于「{query}」的完整学习路径，包含 {len(nodes)} 个章节"

    data = {
        "title": query,
        "summary": overview,
        "description": overview,
        "nodes": nodes,
        "recommendations": [
            f"共 {len(nodes)} 个章节",
            f"约 {outline_data.get('total_duration_hours', 0):.1f} 小时学习时长",
        ],
        "_raw": {
            "total_duration_hours": outline_data.get("total_duration_hours"),
            "level": outline_data.get("level"),
        },
    }

    # ── Save result to ai_path/result/ ─────────────────────────────────────────
    try:
        import json as _json
        from datetime import datetime as _dt
        _result_dir = _AI_PATH_ROOT / "ai_path" / "result"
        _result_dir.mkdir(parents=True, exist_ok=True)
        _timestamp = _dt.now().strftime("%Y%m%d_%H%M%S")
        _filename = f"ai_path_outline_{_timestamp}.json"
        _save_path = _result_dir / _filename
        with open(_save_path, "w", encoding="utf-8") as _f:
            _json.dump(data, _f, ensure_ascii=False, indent=2)
        warnings.append(f"Result saved to {_filename}")
    except Exception:
        pass  # Non-blocking, don't fail the request

    return data, warnings


# ── Main service ───────────────────────────────────────────────────────────────

async def generate_ai_path_pipeline(
    query: str,
    preferences: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """
    Run the new 4-step pipeline and return transformed data + warnings.

    preferences may contain: level, learning_depth, content_type, practical_ratio.
    Unknown or invalid keys/values are silently dropped by _sanitize().

    Returns (data, warnings) where data matches AiPathGenerateResponse.data shape.
    """
    clean = _sanitize(preferences)

    warnings: list[str] = []

    # Run the complete 4-step workflow
    workflow_result = await run_workflow(
        topic=query,
        level=clean.get("level", _DEFAULT_LEVEL),
        learning_depth=clean.get("learning_depth", _DEFAULT_LEARNING_DEPTH),
        content_type=clean.get("content_type", _DEFAULT_CONTENT_TYPE),
        practical_ratio=clean.get("practical_ratio", _DEFAULT_PRACTICAL_RATIO),
        resource_count=_DEFAULT_RESOURCE_COUNT,
    )

    # Extract data
    outline = workflow_result.get("outline")
    if hasattr(outline, "model_dump"):
        outline_data = outline.model_dump()
    else:
        outline_data = outline or {}

    sections_with_resources = workflow_result.get("sections_with_resources", [])
    if not isinstance(sections_with_resources, list):
        sections_with_resources = []

    # Build nodes from sections with resources
    nodes = []
    for sec in outline_data.get("sections", []):
        section_title = sec.get("title", "")

        # Find matching section with resources
        matched_resources = []
        for swr in sections_with_resources:
            swr_title = swr.title if hasattr(swr, "title") else swr.get("title", "")
            if swr_title == section_title:
                for res in swr.resources if hasattr(swr, "resources") else swr.get("resources", []):
                    if isinstance(res, dict):
                        matched_resources.append({
                            "url": res.get("url", ""),
                            "title": res.get("title", ""),
                            "description": res.get("summary", ""),
                        })
                break

        # Build sub_nodes from learning_goals
        sub_nodes = []
        for idx, goal in enumerate(sec.get("learning_goals", [])):
            sub_nodes.append({
                "title": goal,
                "description": f"Goal {idx + 1} of section '{section_title}'",
                "learning_points": [goal],
                "resources": [],
            })

        nodes.append({
            "title": section_title,
            "description": sec.get("description", ""),
            "learning_points": sec.get("learning_goals", []),
            "resources": matched_resources,
            "sub_nodes": sub_nodes,
            "order": sec.get("order", len(nodes) + 1),
        })

    # Enrich node explanations
    _enrich_nodes_explanations(nodes, query)

    final_summary = workflow_result.get("final_summary", "")
    summary = outline_data.get("overview", "") or (final_summary[:300] if final_summary else "")

    data = {
        "title": query,
        "summary": summary,
        "nodes": nodes,
        "recommendations": [
            f"Estimated time: ~{outline_data.get('total_duration_hours', 0):.1f} hours",
            f"Designed for: {outline_data.get('level', 'intermediate')} level",
        ],
        "_raw": {
            "total_duration_hours": outline_data.get("total_duration_hours"),
            "level": outline_data.get("level"),
            "final_summary": final_summary,
            "github_projects": workflow_result.get("github_projects", []),
        },
    }

    # Add metrics as warnings
    warnings.append(f"Found {len(workflow_result.get('exclude_urls', []))} total URLs discovered")

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

    Uses the new 4-step pipeline (step1 → step3) to find and summarize resources.

    If db is provided, results are cached by (url, topic) to avoid re-fetching
    and re-summarizing the same URLs within the same topic.

    If exclude_urls is provided, those URLs are filtered from results.
    """
    # Step 1: Generate outline + search results
    step1_result = await run_step1(
        topic=topic,
        level=_DEFAULT_LEVEL,
        learning_depth=_DEFAULT_LEARNING_DEPTH,
        content_type=_DEFAULT_CONTENT_TYPE,
        practical_ratio=_DEFAULT_PRACTICAL_RATIO,
        resource_count=_DEFAULT_RESOURCE_COUNT,
        exclude_urls=list(exclude_urls) if exclude_urls else None,
    )

    search_results = step1_result.get("search_results", [])
    if not isinstance(search_results, list):
        search_results = []

    # Collect URLs from search results
    discovered_urls = [r.url if hasattr(r, "url") else r.get("url", "") for r in search_results]
    discovered_urls = [u for u in discovered_urls if u]

    # ── Cache layer: check which URLs are already cached ──────────────────────
    cached_results: list[dict] = []
    uncached_urls: list[str] = []
    exclude_set = set(exclude_urls or [])

    if db is not None:
        from app.curd.resource_summary_cache_curd import ResourceSummaryCacheCURD

        for r in search_results:
            url = r.url if hasattr(r, "url") else r.get("url", "")
            if not url or url in exclude_set:
                continue
            hit = ResourceSummaryCacheCURD.get(db, url=url, topic=topic)
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
                uncached_urls.append(url)

    # If all cached, return early
    if db is not None and not uncached_urls:
        return cached_results[:max_results]

    # Step 3: Get supplementary resources for outline sections
    outline = step1_result.get("outline")
    sections_data = []
    if outline:
        if hasattr(outline, "sections"):
            sections_data = [s.model_dump() if hasattr(s, "model_dump") else dict(s) for s in outline.sections]
        elif isinstance(outline, dict):
            sections_data = outline.get("sections", [])

    step3_result = await run_step3(
        sections=sections_data,
        topic=topic,
        exclude_urls=list(exclude_set) + discovered_urls,
    )

    # Collect new results from step 3
    new_results: list[dict] = []
    for sec in step3_result.get("sections", []):
        for res in sec.get("resources", []):
            if isinstance(res, dict):
                url = res.get("url", "")
                if url and url not in exclude_set:
                    new_results.append({
                        "url": url,
                        "title": res.get("title", ""),
                        "description": res.get("summary", ""),
                        "key_points": res.get("key_points", []),
                        "difficulty": res.get("difficulty", "beginner"),
                        "resource_type": res.get("resource_type", "article"),
                        "learning_stage": res.get("learning_stage", "core"),
                        "estimated_minutes": res.get("estimated_minutes", 15),
                        "image": res.get("image"),
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


# ── Section Tutorial Generation ───────────────────────────────────────────────

_TUTORIAL_PROMPT_TEMPLATE = """You are an expert educator creating a detailed learning tutorial.

## Learning Context
- Topic: {query}
- Section: {section_title}
- Level: {level}
- Section Goal: {section_goal}

## Source Resources
{source_resources}

---

## Task
Based on the source resources above, write a comprehensive tutorial in markdown format that:
1. Explains the core concepts clearly with examples
2. Provides step-by-step guidance
3. Includes common pitfalls and how to avoid them
4. Suggests practical exercises or mini-projects
5. Connects concepts back to the overall learning goal

Write in Chinese. Use clear markdown formatting with headings, code blocks, and bullet points where appropriate.

## Output Format
Return a single JSON object (no markdown fences):
{{
  "tutorial": "<detailed markdown tutorial>",
  "key_points": ["<key point 1>", "<key point 2>", "<key point 3>", "<key point 4>", "<key point 5>"]
}}
"""


async def generate_section_tutorial(
    query: str,
    section_title: str,
    section_goal: str,
    resource_urls: list[str],
    level: str = "beginner",
    db=None,
) -> dict:
    """
    Generate a detailed tutorial for a specific learning path section.

    1. Fetch content for each resource URL (from cache or fresh)
    2. Use LLM to generate a comprehensive tutorial
    3. Return tutorial markdown + key points
    """
    import json as _json
    from ai_path.tools.fetch import fetch_page
    from ai_path.models.schemas import FetchedPage
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from ai_path.utils.llm import get_llm

    # ── Step 1: Gather resource content ───────────────────────────────────────
    resource_contents: list[str] = []

    for url in resource_urls:
        content = ""
        title = url

        # Try cache first
        if db is not None:
            from app.curd.resource_summary_cache_curd import ResourceSummaryCacheCURD

            hit = ResourceSummaryCacheCURD.get(db, url=url, topic=query)
            if hit:
                title = hit.title or url
                content = hit.summary or ""
                if hit.key_points:
                    try:
                        kps = _json.loads(hit.key_points)
                        if isinstance(kps, list) and kps:
                            content = f"({title})\n" + "\n".join(f"- {kp}" for kp in kps)
                    except Exception:
                        pass

        # Fresh fetch if not cached or no cache content
        if not content and db is None:
            # No db means skip cache, just fetch
            page = await _fetch_page_sync(url)
            title = page.get("title", url)
            content = page.get("content", "")[:2000]
        elif not content:
            # Fetch fresh for this URL
            page = await _fetch_page_sync(url)
            title = page.get("title", url)
            content = page.get("content", "")[:2000]

        if content:
            resource_contents.append(f"### {title}\nURL: {url}\n{content[:1500]}")

    # Build source resources text
    source_text = "\n\n".join(resource_contents) if resource_contents else "（未找到资源内容）"

    # ── Step 2: Generate tutorial with LLM ───────────────────────────────────
    prompt = _TUTORIAL_PROMPT_TEMPLATE.format(
        query=query,
        section_title=section_title,
        section_goal=section_goal,
        level=level,
        source_resources=source_text,
    )

    try:
        llm = get_llm(temperature=0.3)
        chain = ChatPromptTemplate.from_template(_TUTORIAL_PROMPT_TEMPLATE) | llm | JsonOutputParser()
        result_data = await chain.ainvoke({
            "query": query,
            "section_title": section_title,
            "section_goal": section_goal,
            "level": level,
            "source_resources": source_text,
        })
        tutorial = result_data.get("tutorial", "")
        key_points = result_data.get("key_points", [])
    except Exception as exc:
        # Fallback: return a simple generated tutorial
        tutorial = _generate_fallback_tutorial(query, section_title, section_goal, level, resource_contents)
        key_points = _extract_key_points_fallback(resource_contents)

    return {
        "tutorial": tutorial,
        "key_points": key_points,
    }


def _generate_fallback_tutorial(
    query: str,
    section_title: str,
    section_goal: str,
    level: str,
    resource_contents: list[str],
) -> str:
    """Generate a basic tutorial when LLM fails."""
    content_text = "\n\n".join(resource_contents[:3]) if resource_contents else ""
    return f"""# {section_title}

## 概述
{section_goal}

## 学习目标
- 理解 {section_title} 的核心概念
- 掌握相关的基础技能
- 能够独立完成相关练习

## 详细内容

{content_text[:1000] if content_text else '暂无详细内容，请参考上述资源链接。'}

## 实践建议
1. 先理解核心概念
2. 完成相关练习
3. 总结学习笔记
4. 尝试独立应用

## 注意事项
- 注重基础概念的理解
- 多动手实践
- 及时总结归纳
"""


def _extract_key_points_fallback(resource_contents: list[str]) -> list[str]:
    """Extract key points from resource contents as fallback."""
    points = []
    for content in resource_contents[:3]:
        # Simple extraction: take first few lines as key points
        lines = content.split("\n")
        for line in lines[2:6]:  # Skip title and URL lines
            line = line.strip().lstrip("-*•").strip()
            if line and len(line) > 10 and len(line) < 200:
                points.append(line)
            if len(points) >= 5:
                break
        if len(points) >= 5:
            break
    return points[:5]


async def _fetch_page_sync(url: str) -> dict:
    """Fetch a page synchronously (runs in thread pool)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_fetch_page, url)


def _sync_fetch_page(url: str) -> dict:
    """Synchronous page fetch."""
    from ai_path.tools.fetch import fetch_page as _fetch_page

    page = _fetch_page(url, fallback_title=url, fallback_snippet="")
    return {
        "url": page.url,
        "title": page.title,
        "content": page.content,
        "image": page.image,
    }
