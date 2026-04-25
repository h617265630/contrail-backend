"""
Step 3: Add resources to each section.

Search for supplementary resources (articles/videos/docs) for a given section,
filtering out already-added URLs.

Each step can be run independently or chained as a workflow.
"""

from __future__ import annotations
import asyncio
from typing import Literal

from ai_path.models.schemas import OutlineSection, ResourceSummary
from ai_path.tools.search import web_search
from ai_path.tools.fetch import fetch_page
from ai_path.utils.llm import get_llm, parse_json_response


async def search_supplementary_resources(
    section_title: str,
    section_goal: str,
    existing_urls: list[str],
    resource_type_filter: Literal["video", "article", "docs", "all"] = "all",
    topic: str = "",
    max_results: int = 6,
) -> list[dict]:
    """
    Search for supplementary resources for a section.

    1. Generate search queries based on section info
    2. Search (avoiding existing_urls)
    3. Fetch + summarize
    4. Return new resources filtered by type
    """
    existing_set = set(existing_urls)

    # Generate targeted queries
    queries = [
        f"{section_title} {section_goal}",
        f"{section_title} 教程",
        f"{section_title} 最佳实践",
    ]
    if resource_type_filter == "video":
        queries = [f"{q} video tutorial" for q in queries]
    elif resource_type_filter == "docs":
        queries = [f"{q} official documentation" for q in queries]

    # Run searches concurrently
    all_results = []
    seen: set[str] = existing_set.copy()

    def _search_one(q: str) -> list:
        try:
            return web_search(q, max_results=4)
        except Exception:
            return []

    loop = asyncio.get_event_loop()
    results_lists = await asyncio.gather(
        *[loop.run_in_executor(None, _search_one, q) for q in queries]
    )

    for results in results_lists:
        for r in results:
            if r.url and r.url not in seen:
                seen.add(r.url)
                all_results.append(r)

    # Fetch and summarize concurrently
    semaphore = asyncio.Semaphore(4)

    async def _process_one(r) -> dict | None:
        async with semaphore:
            return await loop.run_in_executor(None, _summarize_one, r, topic)

    summaries = await asyncio.gather(*[_process_one(r) for r in all_results[:max_results]])
    summaries = [s for s in summaries if s is not None]

    # Filter by resource type
    if resource_type_filter != "all":
        summaries = [s for s in summaries if s.get("resource_type") == resource_type_filter]

    return summaries[:max_results]


def _summarize_one(r, topic: str) -> dict | None:
    """Fetch and summarize a single resource."""
    try:
        page = fetch_page(r.url, r.title, r.snippet)
        if not page.fetch_ok and len(page.content) < 50:
            return {
                "url": r.url,
                "title": r.title,
                "description": r.snippet,
                "key_points": [],
                "difficulty": "intermediate",
                "resource_type": _infer_type(r.url),
                "learning_stage": "core",
                "estimated_minutes": 10,
                "image": page.image,
            }

        prompt = f"""分析以下资源，生成简短摘要。

主题：{topic}
标题：{page.title}
内容：{page.content[:2000]}

返回 JSON：
{{
  "url": "{r.url}",
  "title": "标题",
  "summary": "2-3句话摘要",
  "key_points": ["要点1", "要点2"],
  "difficulty": "beginner | intermediate | advanced",
  "resource_type": "article | video | course | docs",
  "learning_stage": "foundation | core | practice | advanced",
  "estimated_minutes": 数字
}}"""

        llm = get_llm(temperature=0.2)
        resp = llm.invoke(prompt)
        parsed = parse_json_response(resp.content)
        parsed["image"] = page.image
        return parsed
    except Exception:
        return None


def _infer_type(url: str) -> str:
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "video"
    if any(k in url_lower for k in ["docs.", "documentation", ".readme"]):
        return "docs"
    if any(k in url_lower for k in ["coursera", "udemy", "pluralsight"]):
        return "course"
    return "article"


async def _process_section(
    section: OutlineSection,
    topic: str,
    existing_urls: list[str],
    max_resources: int = 6,
) -> OutlineSection:
    """Process a single section: search and add resources."""
    # Combine title and goals for search
    section_goal = " ".join(section.learning_goals[:2]) if section.learning_goals else section.description

    try:
        resources_data = await search_supplementary_resources(
            section_title=section.title,
            section_goal=section_goal,
            existing_urls=existing_urls,
            topic=topic,
            max_results=max_resources,
        )

        resources = [
            ResourceSummary(
                url=res["url"],
                title=res["title"],
                summary=res.get("summary", ""),
                key_points=res.get("key_points", []),
                difficulty=res.get("difficulty", "intermediate"),
                resource_type=res.get("resource_type", "article"),
                learning_stage=res.get("learning_stage", "core"),
                estimated_minutes=res.get("estimated_minutes", 15),
                image=res.get("image"),
            )
            for res in resources_data
        ]
    except Exception:
        resources = []

    return OutlineSection(
        title=section.title,
        description=section.description,
        learning_goals=section.learning_goals,
        sub_nodes=section.sub_nodes,
        search_queries=section.search_queries,
        suggested_resources=section.suggested_resources,
        resources=resources,
        estimated_minutes=section.estimated_minutes,
        order=section.order,
    )


async def run_step3(
    sections: list[OutlineSection] | list[dict],
    topic: str = "",
    exclude_urls: list[str] | None = None,
    max_resources_per_section: int = 6,
) -> dict:
    """
    Add supplementary resources to each section.

    Args:
        sections: List of OutlineSection (from step2)
        topic: The main topic
        exclude_urls: URLs to exclude from search
        max_resources_per_section: Max resources per section

    Returns:
        {
            "sections": [OutlineSection with resources, ...],
            "all_exclude_urls": cumulative URLs,
        }
    """
    # Convert dicts to OutlineSection objects
    section_objects = []
    for s in sections:
        if isinstance(s, OutlineSection):
            section_objects.append(s)
        else:
            section_objects.append(OutlineSection(**s))

    # Collect all existing URLs to exclude
    existing_urls = list(exclude_urls or [])
    for s in section_objects:
        existing_urls.extend(s.suggested_resources or [])
        for r in s.resources or []:
            existing_urls.append(r.url)

    # Process sections concurrently
    processed = await asyncio.gather(
        *[
            _process_section(s, topic, existing_urls, max_resources_per_section)
            for s in section_objects
        ]
    )

    # Sort by order
    processed.sort(key=lambda s: s.order)

    # Collect all discovered URLs
    all_exclude = list(set(existing_urls))
    for s in processed:
        for r in s.resources:
            if r.url not in all_exclude:
                all_exclude.append(r.url)

    return {
        "sections": [s.model_dump() for s in processed],
        "sections_with_resources": processed,
        "all_exclude_urls": all_exclude,
    }
