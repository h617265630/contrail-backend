"""
4-Step Pipeline for AI Path generation.

Each step can be run independently or chained as a workflow.

Workflow:
  run_workflow(topic, ...) → outline → expanded_outline → sections_with_resources → final_result

Individual steps:
  run_step1(topic, ...) → {outline, search_results, discovered_urls, exclude_urls}
  run_step2(outline, ...) → {outline, sections, expanded_outline}
  run_step3(sections, ...) → {sections, sections_with_resources, all_exclude_urls}
  run_step4(topic, sections, ...) → {summary, github_projects}
"""

from __future__ import annotations
from typing import Optional

from ai_path.models.schemas import LearningOutline, OutlineSection
from ai_path.pipeline.step1_outline import run_step1
from ai_path.pipeline.step2_tutorial import run_step2
from ai_path.pipeline.step3_resources import run_step3
from ai_path.pipeline.step4_summary import run_step4


async def run_workflow(
    topic: str,
    level: str = "intermediate",
    learning_depth: str = "standard",
    content_type: str = "mixed",
    practical_ratio: str = "balanced",
    resource_count: str = "standard",
) -> dict:
    """
    Complete 4-step workflow: generate learning path from topic.

    Args:
        topic: The learning topic
        level: "beginner" | "intermediate" | "advanced"
        learning_depth: "quick" | "standard" | "deep"
        content_type: "video" | "article" | "mixed"
        practical_ratio: "theory_first" | "balanced" | "practice_first"
        resource_count: "compact" | "standard" | "rich"

    Returns:
        {
            "outline": LearningOutline,
            "expanded_outline": LearningOutline,
            "sections": List[dict],
            "sections_with_resources": List[OutlineSection],
            "final_summary": str,
            "github_projects": List[dict],
            "exclude_urls": List[str],
        }
    """
    # Step 1: Generate outline
    step1_result = await run_step1(
        topic=topic,
        level=level,
        learning_depth=learning_depth,
        content_type=content_type,
        practical_ratio=practical_ratio,
        resource_count=resource_count,
    )

    # Step 2: Expand sections with sub-nodes
    step2_result = await run_step2(
        outline=step1_result["outline"],
        topic=topic,
        level=level,
    )

    # Step 3: Add supplementary resources
    step3_result = await run_step3(
        sections=step2_result["sections"],
        topic=topic,
        exclude_urls=step1_result["exclude_urls"],
    )

    # Step 4: Generate summary + GitHub projects
    step4_result = await run_step4(
        topic=topic,
        sections=step3_result["sections"],
        level=level,
    )

    return {
        "outline": step1_result["outline"],
        "expanded_outline": step2_result["expanded_outline"],
        "sections": step3_result["sections"],
        "sections_with_resources": step3_result["sections_with_resources"],
        "final_summary": step4_result["final_summary"],
        "github_projects": step4_result["github_projects"],
        "exclude_urls": step3_result["all_exclude_urls"],
    }


# ── Single step exports ───────────────────────────────────────────────────────

async def run_step1(
    topic: str,
    level: str = "intermediate",
    learning_depth: str = "standard",
    content_type: str = "mixed",
    practical_ratio: str = "balanced",
    resource_count: str = "standard",
    exclude_urls: list[str] | None = None,
) -> dict:
    """
    Step 1: Generate outline from topic.

    Returns:
        {
            "outline": LearningOutline,
            "search_results": List[SearchResult],
            "discovered_urls": List[str],
            "exclude_urls": List[str],
        }
    """
    from ai_path.pipeline.step1_outline import run_step1 as _run
    return await _run(
        topic=topic,
        level=level,
        learning_depth=learning_depth,
        content_type=content_type,
        practical_ratio=practical_ratio,
        resource_count=resource_count,
        exclude_urls=exclude_urls,
    )


async def run_step2(
    outline: LearningOutline | dict,
    topic: str = "",
    level: str = "intermediate",
) -> dict:
    """
    Step 2: Expand sections with detailed sub-nodes.

    Returns:
        {
            "outline": LearningOutline,
            "sections": List[dict],
            "expanded_outline": LearningOutline,
        }
    """
    from ai_path.pipeline.step2_tutorial import run_step2 as _run
    return await _run(outline=outline, topic=topic, level=level)


async def run_step3(
    sections: list[OutlineSection] | list[dict],
    topic: str = "",
    exclude_urls: list[str] | None = None,
    max_resources_per_section: int = 6,
) -> dict:
    """
    Step 3: Add supplementary resources to each section.

    Returns:
        {
            "sections": List[dict],
            "sections_with_resources": List[OutlineSection],
            "all_exclude_urls": List[str],
        }
    """
    from ai_path.pipeline.step3_resources import run_step3 as _run
    return await _run(
        sections=sections,
        topic=topic,
        exclude_urls=exclude_urls,
        max_resources_per_section=max_resources_per_section,
    )


async def run_step4(
    topic: str,
    sections: list[dict],
    level: str = "intermediate",
) -> dict:
    """
    Step 4: Generate summary + GitHub projects.

    Returns:
        {
            "final_summary": str,
            "summary": str,
            "github_projects": List[dict],
        }
    """
    from ai_path.pipeline.step4_summary import run_step4 as _run
    return await _run(topic=topic, sections=sections, level=level)


# ── Re-export models ─────────────────────────────────────────────────────────
from ai_path.models.schemas import (
    LearningOutline,
    OutlineSection,
    SubNode,
    LearningPath,
    PathSection,
    ResourceSummary,
    SearchResult,
    SearchQuery,
    GitHubProject,
    GenPathState,
)

__all__ = [
    # Workflow
    "run_workflow",
    # Steps
    "run_step1",
    "run_step2",
    "run_step3",
    "run_step4",
    # Models
    "LearningOutline",
    "OutlineSection",
    "SubNode",
    "LearningPath",
    "PathSection",
    "ResourceSummary",
    "SearchResult",
    "SearchQuery",
    "GitHubProject",
    "GenPathState",
]
