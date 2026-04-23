from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure ai_path is importable
_AI_PATH_ROOT = Path(__file__).resolve().parents[4]
if str(_AI_PATH_ROOT) not in sys.path:
    sys.path.insert(0, str(_AI_PATH_ROOT))

from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_db_dep
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from .service import generate_ai_path_pipeline, generate_ai_path_outline, generate_section_tutorial, search_resources_pipeline


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


class SectionTutorialRequest(BaseModel):
    """Request to generate a detailed tutorial for a specific section."""
    query: str = Field(..., min_length=1, description="Original user learning goal")
    section_title: str = Field(..., description="Section title")
    section_goal: str = Field(..., description="Section description/learning goal")
    resource_urls: list[str] = Field(default_factory=list, description="URLs of resources in this section")
    level: str = Field(default="beginner", description="Learning level")


class SectionTutorialResponse(BaseModel):
    """Response with generated tutorial content."""
    tutorial: str = Field(..., description="LLM-generated detailed tutorial in markdown")
    key_points: list[str] = Field(default_factory=list, description="Key points extracted from resources")


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


@router.post("/generate-outline", response_model=AiPathGenerateResponse)
async def generate_ai_path_outline_endpoint(payload: AiPathGenerateRequest):
    """
    Generate only the learning path outline (search → summarise only, skip organize/report).
    Much faster. Returns stages grouped by learning_stage with resources.
    User can then call /section-tutorial for each stage to get detailed content.
    """
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
        data, warnings = await generate_ai_path_outline(query, prefs)
        return AiPathGenerateResponse(data=data, warnings=warnings)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"ai_path outline failed: {exc}"
        ) from exc


# ── SubNode Detail (Step 2.5) ──────────────────────────────────────────────────

class SubNodeDetailRequest(BaseModel):
    """Request to generate detailed content for a sub-node."""
    topic: str = Field(..., min_length=1, description="Main learning topic")
    section_title: str = Field(..., description="Parent section title")
    subnode_title: str = Field(..., description="Sub-node title")
    subnode_description: str = Field(default="", description="Sub-node description")
    subnode_key_points: list[str] = Field(default_factory=list, description="Key points")
    level: str = Field(default="intermediate", description="Learning level")
    detail_level: str = Field(default="detailed", description="concise | detailed")


class SubNodeDetailResponse(BaseModel):
    """Response with detailed sub-node content."""
    title: str
    description: str
    key_points: list[str]
    detailed_content: str = Field(..., description="Detailed Markdown content")
    code_examples: list[str] = Field(default_factory=list)


@router.post("/subnode-detail", response_model=SubNodeDetailResponse)
async def generate_subnode_detail_endpoint(
    payload: SubNodeDetailRequest,
):
    """Generate detailed content for a sub-node (Step 2.5). Called on-demand when user clicks a sub-node."""
    try:
        from ai_path.pipeline.step2_5_subnode_detail import run_step2_5

        result = await run_step2_5(
            subnode={
                "title": payload.subnode_title,
                "description": payload.subnode_description,
                "key_points": payload.subnode_key_points,
            },
            section_title=payload.section_title,
            topic=payload.topic,
            level=payload.level,
            detail_level=payload.detail_level,
        )

        return SubNodeDetailResponse(
            title=result.title,
            description=result.description,
            key_points=result.key_points,
            detailed_content=result.detailed_content,
            code_examples=result.code_examples,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Sub-node detail generation failed: {exc}"
        ) from exc


@router.post("/section-tutorial", response_model=SectionTutorialResponse)
async def generate_section_tutorial_endpoint(
    payload: SectionTutorialRequest,
    db=Depends(get_db_dep),
):
    """Generate a detailed tutorial for a specific section based on its resources."""
    try:
        result = await generate_section_tutorial(
            query=payload.query,
            section_title=payload.section_title,
            section_goal=payload.section_goal,
            resource_urls=payload.resource_urls,
            level=payload.level,
            db=db,
        )
        return SectionTutorialResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Section tutorial generation failed: {exc}"
        ) from exc


@router.get("/result/latest")
async def get_latest_result():
    """Load the most recent saved result from ai_path/result/."""
    import glob as _glob
    import json as _json
    from pathlib import Path
    _project_root = Path(__file__).resolve().parents[4]
    _result_dir = _project_root / "ai_path" / "result"
    files = sorted(_result_dir.glob("ai_path_outline_*.json"), reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No saved results found")
    with open(files[0], "r", encoding="utf-8") as f:
        saved_data = _json.load(f)
    return AiPathGenerateResponse(data=saved_data, warnings=[])


@router.get("/result/{filename}")
async def get_saved_result(filename: str):
    """Load a previously saved result from ai_path/result/ for debugging."""
    import json as _json
    from pathlib import Path
    _project_root = Path(__file__).resolve().parents[4]
    _file_path = _project_root / "ai_path" / "result" / filename
    if not _file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    with open(_file_path, "r", encoding="utf-8") as f:
        saved_data = _json.load(f)
    return AiPathGenerateResponse(data=saved_data, warnings=[])


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


# ── Debug / Step-by-step endpoints ─────────────────────────────────────────────

class Step1SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Learning topic")
    level: str = Field(default="beginner", description="Learning level")
    max_results: int = Field(default=10, description="Max resources to fetch")


class Step1SearchResponse(BaseModel):
    step: str = "step1_search"
    message: str
    resources_cached: int
    resources: list[dict]  # Full resource details with content


@router.post("/debug/step1-search", response_model=Step1SearchResponse)
async def debug_step1_search(
    payload: Step1SearchRequest,
    db=Depends(get_db_dep),
):
    """
    Step 1: Search for resources, fetch content, and save summaries to cache.
    Returns list of cached resource URLs for next steps.
    """
    try:
        from .service import search_resources_pipeline

        results = await search_resources_pipeline(
            topic=payload.query,
            max_results=payload.max_results,
            db=db,
            exclude_urls=[],
        )
        db.commit()

        return Step1SearchResponse(
            step="step1_search",
            message=f"Successfully cached {len(results)} resources for '{payload.query}'",
            resources_cached=len(results),
            resources=results,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Step 1 failed: {exc}") from exc


class Step2OutlineRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Learning topic")
    level: str = Field(default="beginner")


class Step2OutlineResponse(BaseModel):
    step: str = "step2_outline"
    message: str
    outline: dict


@router.post("/debug/step2-outline", response_model=Step2OutlineResponse)
async def debug_step2_outline(
    payload: Step2OutlineRequest,
    db=Depends(get_db_dep),
):
    """
    Step 2: Generate learning path outline from cached resources.
    Groups resources by learning_stage (foundation/core/practice/advanced).
    """
    try:
        from .service import generate_ai_path_outline

        data, warnings = await generate_ai_path_outline(
            query=payload.query,
            preferences={"level": payload.level},
        )
        db.commit()

        return Step2OutlineResponse(
            step="step2_outline",
            message=f"Generated outline with {len(data.get('nodes', []))} stages",
            outline=data,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Step 2 failed: {exc}") from exc


class Step3StageDetailRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Original learning topic")
    stage_title: str = Field(..., description="Stage title from outline")
    stage_goal: str = Field(..., description="Stage description/learning goal")
    resource_urls: list[str] = Field(default_factory=list, description="URLs of resources for this stage")
    level: str = Field(default="beginner")


class Step3StageDetailResponse(BaseModel):
    step: str = "step3_stage_detail"
    message: str
    tutorial: str
    key_points: list[str]


@router.post("/debug/step3-stage-detail", response_model=Step3StageDetailResponse)
async def debug_step3_stage_detail(
    payload: Step3StageDetailRequest,
    db=Depends(get_db_dep),
):
    """
    Step 3: Generate detailed knowledge point introduction and resource recommendations
    for a specific stage based on cached resources.
    """
    try:
        from .service import generate_section_tutorial

        result = await generate_section_tutorial(
            query=payload.query,
            section_title=payload.stage_title,
            section_goal=payload.stage_goal,
            resource_urls=payload.resource_urls,
            level=payload.level,
            db=db,
        )

        return Step3StageDetailResponse(
            step="step3_stage_detail",
            message=f"Generated detailed content for stage '{payload.stage_title}'",
            tutorial=result["tutorial"],
            key_points=result["key_points"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Step 3 failed: {exc}") from exc


class Step4StageSummaryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Learning topic")
    stage_title: str = Field(..., description="Stage title")
    stage_goal: str = Field(..., description="Stage description")
    tutorial: str = Field(..., description="Generated tutorial content")


class Step4StageSummaryResponse(BaseModel):
    step: str = "step4_stage_summary"
    message: str
    summary: str
    github_project_hints: list[str]


@router.post("/debug/step4-stage-summary", response_model=Step4StageSummaryResponse)
async def debug_step4_stage_summary(
    payload: Step4StageSummaryRequest,
    db=Depends(get_db_dep),
):
    """
    Step 4: Generate a concise summary for the stage and extract GitHub project hints.
    """
    try:
        import json as _json
        from ai_path.utils.llm import get_llm
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_template("""Based on the following tutorial content for the stage "{stage_title}" about "{query}", provide:

1. A concise 2-3 sentence summary of what was covered
2. 3 GitHub project search keywords/phrases that would help practice this stage's content

Return JSON:
{{
  "summary": "concise summary here",
  "github_project_hints": ["keyword1", "keyword2", "keyword3"]
}}""")

        chain = prompt | get_llm(temperature=0.3) | JsonOutputParser()
        result = await chain.ainvoke({
            "query": payload.query,
            "stage_title": payload.stage_title,
            "tutorial": payload.tutorial[:2000],  # Limit input
        })

        return Step4StageSummaryResponse(
            step="step4_stage_summary",
            message=f"Generated summary for stage '{payload.stage_title}'",
            summary=result.get("summary", ""),
            github_project_hints=result.get("github_project_hints", []),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Step 4 failed: {exc}") from exc


class Step5GithubRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Learning topic")
    summaries: list[str] = Field(default_factory=list, description="Stage summaries for context")
    github_hints: list[str] = Field(default_factory=list, description="GitHub project search hints")


class Step5GithubResponse(BaseModel):
    step: str = "step5_github"
    message: str
    projects: list[dict]


@router.post("/debug/step5-github", response_model=Step5GithubResponse)
async def debug_step5_github(
    payload: Step5GithubRequest,
):
    """
    Step 5: Search GitHub for relevant open-source projects based on topic + summaries + hints.
    """
    try:
        from ai_path.ai_resource.github import search_github

        # Combine all search terms
        search_terms = [payload.query] + payload.summaries[:2] + payload.github_hints
        # Deduplicate and limit
        seen = set()
        unique_terms = []
        for term in search_terms:
            if term.lower() not in seen:
                seen.add(term.lower())
                unique_terms.append(term)
        search_term = " ".join(unique_terms[:5])

        projects = search_github(search_term, limit=6)

        return Step5GithubResponse(
            step="step5_github",
            message=f"Found {len(projects)} GitHub projects",
            projects=projects,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Step 5 failed: {exc}") from exc


# ── LLM-based Smart Outline Generator ─────────────────────────────────────────

async def _generate_smart_outline(
    topic: str,
    resources: list[dict],
    level: str = "beginner",
) -> tuple[dict[str, Any], list[str]]:
    """
    Use LLM to generate a proper structured Chinese learning path outline
    from the given resources.
    """
    import json as _json
    from ai_path.utils.llm import get_llm
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    # Build resources text for prompt
    resources_text = []
    for i, r in enumerate(resources):
        title = r.get("title", "")
        url = r.get("url", "")
        summary = r.get("description", "")[:300]
        resources_text.append(f"{i+1}. {title}\n   URL: {url}\n   摘要: {summary}")

    resources_json_str = "\n".join(resources_text)

    # Depth config
    depth_config = {
        "quick": {"min_sections": 2, "max_sections": 3, "depth_instruction": "简洁明了，聚焦核心知识点"},
        "standard": {"min_sections": 3, "max_sections": 5, "depth_instruction": "平衡深度和广度，每个阶段有清晰的学习目标"},
        "deep": {"min_sections": 5, "max_sections": 7, "depth_instruction": "深入详细，包含前置知识、进阶内容和实践项目"},
    }
    depth_cfg = depth_config.get("standard")  # Default to standard

    # Build prompt with proper escaping using string concatenation
    # JSON example with escaped braces for LangChain
    json_example = (
        "{{\n"
        '  "overview": "整体学习路径概述（2-3句话）",\n'
        '  "total_duration_hours": 估算学习时长（小时数字），\n'
        "  \"sections\": [\n"
        "    {{\n"
        '      "title": "阶段名称（如：理解核心概念）",\n'
        '      "description": "阶段详细描述，说明学生完成此阶段后能做什么",\n'
        '      "learning_goals": ["可执行的学习目标1", "学习目标2", "学习目标3"],\n'
        '      "key_points": ["关键知识点1", "关键知识点2"],\n'
        "      \"resources\": [\n"
        '        {{"url": "资源URL", "title": "资源标题"}}\n'
        "      ],\n"
        '      "order": 1\n'
        "    }}\n"
        "  ]\n"
        "}}"
    )

    prompt_text = (
        "你是一位资深课程设计师，为学生设计一条清晰、高效的学习路径。\n\n"
        "## 学习主题\n"
        + topic + "\n\n"
        "## 学生水平\n"
        + level + "\n\n"
        "## 学习资源\n"
        + resources_json_str + "\n\n"
        "## 任务\n"
        "根据以上资源，设计一条结构清晰的学习路径大纲。\n\n"
        "## 要求\n"
        f"- 生成 {depth_cfg['min_sections']}-{depth_cfg['max_sections']} 个学习阶段\n"
        f"- {depth_cfg['depth_instruction']}\n"
        "- 每个阶段需要包含：阶段名称、详细描述、学习要点、推荐资源\n"
        "- 用中文回答\n"
        "- 阶段顺序：从基础概念 → 核心知识 → 实践应用 → 进阶主题\n\n"
        "## 输出格式（JSON，不要使用markdown代码块）\n"
        + json_example + "\n\n"
        "## 重要提示\n"
        "- 每个资源URL必须出现在某个阶段中\n"
        "- 阶段名称要具体、有意义，避免'阶段1'这样的泛泛名称\n"
        "- 学习目标要具体可衡量"
    )

    try:
        # Use PromptTemplate directly to avoid variable parsing issues
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate(template=prompt_text, input_variables=[])
        chain = prompt | get_llm(temperature=0.3) | JsonOutputParser()
        result = await chain.ainvoke({})

        sections = result.get("sections", [])
        overview = result.get("overview", "")
        total_hours = result.get("total_duration_hours", 0)

        # Transform to nodes format
        nodes = []
        for sec in sections:
            sec_resources = sec.get("resources", [])
            if not isinstance(sec_resources, list):
                sec_resources = []

            # Match resources by URL
            matched_resources = []
            for res in sec_resources:
                res_url = res.get("url", "") if isinstance(res, dict) else str(res)
                for r in resources:
                    if r.get("url") == res_url:
                        matched_resources.append({
                            "url": r.get("url", ""),
                            "title": r.get("title", ""),
                            "description": r.get("description", "")[:200],
                        })
                        break

            # Fallback: assign first 2 unmatched resources
            if len(matched_resources) < 2:
                for r in resources:
                    if r.get("url") not in [mr.get("url") for mr in matched_resources]:
                        matched_resources.append({
                            "url": r.get("url", ""),
                            "title": r.get("title", ""),
                            "description": r.get("description", "")[:200],
                        })
                        if len(matched_resources) >= 3:
                            break

            nodes.append({
                "title": sec.get("title", ""),
                "description": sec.get("description", ""),
                "learning_points": sec.get("learning_goals", []),
                "key_points": sec.get("key_points", []),
                "resources": matched_resources,
                "sub_nodes": [],
                "order": sec.get("order", len(nodes) + 1),
            })

        warnings = [f"Generated {len(nodes)} stages from {len(resources)} resources"]

        outline_data = {
            "title": topic,
            "summary": overview,
            "nodes": nodes,
            "recommendations": [
                f"预计学习时长：约 {total_hours} 小时",
                f"共 {len(nodes)} 个学习阶段",
            ],
            "total_duration_hours": total_hours,
            "_smart_outline": True,
        }

        return outline_data, warnings
    except Exception as exc:
        # No fallback - raise the error
        raise RuntimeError(f"Failed to generate smart outline: {exc}")


# ── Combined Step 1 + 2 ─────────────────────────────────────────────────────────

class CombinedRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Learning topic")
    level: str = Field(default="beginner", description="Learning level")
    max_results: int = Field(default=10, description="Max resources to fetch")
    save_to_file: bool = Field(default=True, description="Save result to ai_path/result directory")


class CombinedResponse(BaseModel):
    step: str = "combined_1_2"
    message: str
    resources: list[dict]
    outline: dict
    file_path: str | None = None


@router.post("/debug/combined", response_model=CombinedResponse)
async def debug_combined(
    payload: CombinedRequest,
    db=Depends(get_db_dep),
):
    """
    Step 1 + Step 2 combined: Search resources, cache, then generate outline.
    Optionally saves result to ai_path/result/{query_slug}_{timestamp}.json
    """
    try:
        import time
        import re
        from .service import search_resources_pipeline, generate_ai_path_outline

        # Step 1: Search and cache resources
        resources = await search_resources_pipeline(
            topic=payload.query,
            max_results=payload.max_results,
            db=db,
            exclude_urls=[],
        )
        db.commit()

        # Step 2: Generate smart outline with LLM (instead of simple grouping)
        outline_data, warnings = await _generate_smart_outline(
            topic=payload.query,
            resources=resources,
            level=payload.level,
        )
        db.commit()

        # Build combined result
        result = {
            "query": payload.query,
            "level": payload.level,
            "resources": resources,
            "outline": outline_data,
            "warnings": warnings,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save to file if requested
        file_path = None
        if payload.save_to_file:
            from pathlib import Path
            # Create slug from query
            slug = re.sub(r"[^a-zA-Z0-9]+", "_", payload.query).lower()
            slug = slug[:50]  # Limit length
            timestamp = int(time.time())
            filename = f"{slug}_{timestamp}.json"
            result_dir = Path("/Users/burn/Code/path/ai_path/result")
            result_dir.mkdir(parents=True, exist_ok=True)
            file_path = result_dir / filename

            import json as _json
            with open(file_path, "w", encoding="utf-8") as f:
                _json.dump(result, f, ensure_ascii=False, indent=2)

        return CombinedResponse(
            step="combined_1_2",
            message=f"Generated outline with {len(outline_data.get('nodes', []))} stages from {len(resources)} resources",
            resources=resources,
            outline=outline_data,
            file_path=str(file_path) if file_path else None,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Combined failed: {exc}") from exc
