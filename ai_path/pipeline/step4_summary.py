"""
Step 4: Generate final summary + GitHub projects.

1. Summarize all sections' tutorials into a cohesive overview
2. Search GitHub for relevant open-source projects

Each step can be run independently or chained as a workflow.
"""

from __future__ import annotations
import asyncio

from ai_path.models.schemas import GitHubProject
from ai_path.ai_resource.github import search_github
from ai_path.utils.llm import get_llm, parse_json_response


async def generate_final_summary(
    topic: str,
    sections_data: list[dict],
    level: str = "intermediate",
) -> dict:
    """
    Generate final summary + GitHub projects.

    sections_data: list of {
        "title": str,
        "description": str,
        "tutorial_md": str (optional),
        "resources": list[dict] (optional),
    }
    """
    # ── Step 1: LLM generate summary ─────────────────────────────────────────
    sections_text = "\n\n".join([
        f"## {s.get('title', 'Unknown')}\n{s.get('description', '')}"
        + (f"\n\n教程摘要：\n{s.get('tutorial_md', '')[:500]}" if s.get("tutorial_md") else "")
        for s in sections_data
    ])

    prompt = f"""你是一位资深的技术学习路径规划专家。请为以下学习路径生成整体总结。

学习主题：{topic}
难度级别：{level}

各章节内容：
{sections_text}

请生成 Markdown 格式的总结，要求：
1. 整体概述（学习路径的核心价值和方法论）
2. 学习路径图（用文字描述章节之间的递进关系）
3. 学习建议（如何高效学习、避免常见错误）
4. 后续进阶方向（学完之后可以探索哪些方向）

返回 JSON 格式（不要加 markdown 代码块）：
{{
  "summary": "完整的 Markdown 总结内容"
}}"""

    try:
        llm = get_llm(temperature=0.4)
        response = await llm.ainvoke(prompt)
        parsed = parse_json_response(response.content)
        summary = parsed.get("summary", "")
    except Exception:
        summary = f"# {topic} 学习路径总结\n\n恭喜你完成了 {topic} 的学习！请继续探索和实践。"

    # ── Step 2: Search GitHub projects ───────────────────────────────────────
    loop = asyncio.get_event_loop()
    github_results = await loop.run_in_executor(
        None, _search_github_sync, topic
    )

    return {
        "summary": summary,
        "github_projects": github_results,
    }


def _search_github_sync(topic: str) -> list[dict]:
    """Search GitHub for relevant projects."""
    queries = [
        f"{topic} framework agent",
        f"{topic} tutorial open source",
    ]
    all_projects: list[dict] = []
    seen_names: set[str] = set()

    for query in queries:
        try:
            results = search_github(query, limit=6)
            for r in results:
                # r has keys: type, title, url, description, source_score, thumbnail, why_recommended
                name = r.get("title", "")
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_projects.append({
                        "name": name,
                        "url": r.get("url", ""),
                        "description": r.get("description", ""),
                        "stars": 0,
                        "stars_display": "",
                        "language": "",
                        "thumbnail": r.get("thumbnail"),
                    })
        except Exception:
            continue

    # Sort by stars descending (if we had stars data)
    all_projects.sort(key=lambda x: x.get("stars", 0), reverse=True)
    return all_projects[:6]


async def run_step4(
    topic: str,
    sections: list[dict],
    level: str = "intermediate",
) -> dict:
    """
    Generate final summary + GitHub projects.

    Args:
        topic: The learning topic
        sections: List of section dicts (from step2/step3)
        level: Difficulty level

    Returns:
        {
            "summary": str,  # Markdown
            "github_projects": List[dict],
        }
    """
    result = await generate_final_summary(topic, sections, level)
    return {
        "final_summary": result["summary"],
        "summary": result["summary"],
        "github_projects": result["github_projects"],
    }
