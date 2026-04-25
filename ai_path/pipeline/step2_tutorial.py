"""
Step 2: Expand each section with detailed sub-nodes.

For each section in the outline:
1. Generate 3-5 sub-nodes (detailed learning points)
2. Expand section description
3. Add search queries for detailed resources

Each step can be run independently or chained as a workflow.
"""

from __future__ import annotations
import asyncio

from ai_path.models.schemas import LearningOutline, OutlineSection, SubNode
from ai_path.utils.llm import get_llm, parse_json_response


async def expand_section(
    section: OutlineSection,
    topic: str,
    level: str = "intermediate",
) -> OutlineSection:
    """Expand a section into detailed sub-nodes with learning points."""
    prompt = f"""你是专业的技术教育专家。请为以下章节生成详细的学习子节点。

主题：{topic}
章节标题：{section.title}
章节简介：{section.description}
难度级别：{level}

请返回 JSON 格式（不要加 markdown 代码块）：
{{
  "expanded_title": "扩展后的章节标题（更具体）",
  "description": "章节的详细描述（2-3句话）",
  "sub_nodes": [
    {{
      "title": "子节点标题1",
      "description": "子节点详细说明",
      "key_points": ["关键点1", "关键点2", "关键点3"],
      "practical_exercise": "实践练习建议",
      "search_keywords": ["搜索关键词1", "搜索关键词2"]
    }},
    ...
  ],
  "estimated_minutes": 总学习时长（分钟）
}}"""

    try:
        llm = get_llm(temperature=0.3)
        response = await llm.ainvoke(prompt)
        parsed = parse_json_response(response.content)

        sub_nodes = [
            SubNode(**node)
            for node in parsed.get("sub_nodes", [])[:5]  # max 5 sub-nodes
        ]

        return OutlineSection(
            title=parsed.get("expanded_title", section.title),
            description=parsed.get("description", section.description),
            learning_goals=section.learning_goals,
            sub_nodes=sub_nodes,
            search_queries=section.search_queries,
            suggested_resources=section.suggested_resources,
            estimated_minutes=parsed.get("estimated_minutes", 60),
            order=section.order,
        )
    except Exception:
        # Fallback: create basic sub-nodes from learning_goals
        fallback_sub_nodes = [
            SubNode(
                title=goal,
                description=f"学习并掌握 {goal}",
                key_points=[goal],
                practical_exercise="完成相关练习",
                search_keywords=[goal, topic],
            )
            for goal in section.learning_goals[:5]
        ]

        return OutlineSection(
            title=section.title,
            description=section.description,
            learning_goals=section.learning_goals,
            sub_nodes=fallback_sub_nodes,
            search_queries=section.search_queries,
            suggested_resources=section.suggested_resources,
            estimated_minutes=section.estimated_minutes,
            order=section.order,
        )


async def run_step2(
    outline: LearningOutline | dict,
    topic: str = "",
    level: str = "intermediate",
) -> dict:
    """
    Expand each section in the outline with detailed sub-nodes.

    Args:
        outline: The outline from step1 (LearningOutline or dict)
        topic: The main topic
        level: difficulty level

    Returns:
        Expanded outline with sub-nodes for each section
    """
    # Handle both LearningOutline object and dict
    if isinstance(outline, dict):
        sections_data = outline.get("sections", [])
        topic = topic or outline.get("topic", "")
        level = outline.get("level", level)
    else:
        sections_data = outline.sections
        topic = topic or outline.topic
        level = outline.level

    if not sections_data:
        return {"outline": outline, "sections": [], "expanded_outline": outline}

    # Ensure sections are OutlineSection objects
    sections = []
    for s in sections_data:
        if isinstance(s, OutlineSection):
            sections.append(s)
        else:
            sections.append(OutlineSection(**s))

    # Expand each section concurrently
    expanded_sections = await asyncio.gather(
        *[expand_section(s, topic, level) for s in sections]
    )

    # Reorder by order field
    expanded_sections.sort(key=lambda s: s.order)

    # Build new LearningOutline
    if isinstance(outline, LearningOutline):
        expanded_outline = LearningOutline(
            topic=outline.topic,
            level=outline.level,
            overview=outline.overview,
            total_duration_hours=outline.total_duration_hours,
            sections=expanded_sections,
        )
    else:
        expanded_outline = LearningOutline(
            topic=topic,
            level=level,
            overview=outline.get("overview", ""),
            total_duration_hours=outline.get("total_duration_hours", 0),
            sections=expanded_sections,
        )

    return {
        "outline": expanded_outline,
        "sections": [s.model_dump() for s in expanded_sections],
        "expanded_outline": expanded_outline,
    }
