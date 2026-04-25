"""
Step 2.5: Generate detailed content for each sub-node.

When user clicks on a sub-node in the frontend, this step generates:
1. Detailed explanation (Markdown)
2. Code examples
3. Related resources

This is called on-demand (lazy loading) to save time.

Cache: Results are cached by (topic, section_title, subnode_title) to avoid regeneration.
"""

from __future__ import annotations
import asyncio
import hashlib
import json
from pathlib import Path

from ai_path.models.schemas import SubNode
from ai_path.utils.llm import get_llm, parse_json_response


# ── Cache directory ────────────────────────────────────────────────────────────

_CACHE_DIR = Path(__file__).resolve().parent.parent / "result" / "subnode_cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_key(topic: str, section_title: str, subnode_title: str, detail_level: str = "detailed") -> str:
    """Generate cache key from topic + section + subnode + detail_level."""
    key_str = f"{topic}|{section_title}|{subnode_title}|{detail_level}"
    return hashlib.md5(key_str.encode()).hexdigest()


def _get_cache_path(cache_key: str) -> Path:
    """Get cache file path."""
    return _CACHE_DIR / f"{cache_key}.json"


def _load_from_cache(cache_key: str) -> SubNode | None:
    """Load cached result if exists."""
    cache_path = _get_cache_path(cache_key)
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SubNode(**data)
        except Exception:
            pass
    return None


def _save_to_cache(cache_key: str, subnode: SubNode) -> None:
    """Save result to cache."""
    cache_path = _get_cache_path(cache_key)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(subnode.model_dump(), f, ensure_ascii=False, indent=2)
    except Exception:
        pass


async def generate_subnode_detail(
    subnode_title: str,
    subnode_description: str,
    subnode_key_points: list[str],
    section_title: str,
    topic: str,
    level: str = "intermediate",
    detail_level: str = "detailed",
) -> SubNode:
    """
    Generate detailed content for a single sub-node.

    Args:
        detail_level: "concise" (30-60s) or "detailed" (2min)

    Returns SubNode with detailed_content, code_examples filled.
    """
    key_points_text = "\n".join([f"- {kp}" for kp in subnode_key_points])

    # Concise prompt (30-60 seconds)
    if detail_level == "concise":
        prompt = f"""你是一位技术教育专家。请为以下知识点生成简洁的讲解。

## 上下文
- 学习主题：{topic}
- 知识点：{subnode_title}
- 简介：{subnode_description}
- 难度：{level}

## 已有关键点
{key_points_text}

## 任务
生成简洁讲解（控制在300字以内），包括：
1. 一段概念解释
2. 一个简短代码示例
3. 3条核心要点

返回 JSON（不要 markdown 代码块）：
{{
  "detailed_content": "简洁的 Markdown 讲解",
  "code_examples": ["一个简短代码示例"]
}}

要求：用中文，简洁明了，直击要点。"""
    else:
        # Detailed prompt (2 minutes)
        prompt = f"""你是一位专业的技术教育专家。请为以下知识点生成详细的讲解内容。

## 上下文
- 学习主题：{topic}
- 所属章节：{section_title}
- 知识点：{subnode_title}
- 简介：{subnode_description}
- 难度级别：{level}

## 已有关键点
{key_points_text}

## 任务
请生成详细的讲解内容，包括：
1. 概念解释（为什么需要这个知识点）
2. 核心原理（它是如何工作的）
3. 代码示例（可运行的代码）
4. 常见问题与注意事项
5. 实践建议

请返回 JSON 格式（不要加 markdown 代码块）：
{{
  "detailed_content": "详细的 Markdown 讲解内容（包含标题、段落、列表等）",
  "code_examples": [
    "代码示例1（带注释）",
    "代码示例2（带注释）"
  ],
  "common_mistakes": ["常见错误1", "常见错误2"],
  "best_practices": ["最佳实践1", "最佳实践2"]
}}

要求：
- 用中文回答
- detailed_content 要详细、易懂，使用 Markdown 格式
- code_examples 要可运行、带注释
- 内容要针对 {level} 级别的学习者"""

    try:
        llm = get_llm(temperature=0.3)
        response = await llm.ainvoke(prompt)
        parsed = parse_json_response(response.content)

        detailed_content = parsed.get("detailed_content", "")
        code_examples = parsed.get("code_examples", [])

        # Enhance detailed_content with code examples
        if code_examples:
            code_section = "\n\n## 代码示例\n\n"
            for i, code in enumerate(code_examples, 1):
                code_section += f"### 示例 {i}\n\n```python\n{code}\n```\n\n"
            detailed_content += code_section

        # Add common mistakes and best practices
        if parsed.get("common_mistakes"):
            detailed_content += "\n\n## 常见错误\n\n"
            for mistake in parsed["common_mistakes"]:
                detailed_content += f"- {mistake}\n"

        if parsed.get("best_practices"):
            detailed_content += "\n\n## 最佳实践\n\n"
            for practice in parsed["best_practices"]:
                detailed_content += f"- {practice}\n"

        return SubNode(
            title=subnode_title,
            description=subnode_description,
            key_points=subnode_key_points,
            detailed_content=detailed_content,
            code_examples=code_examples,
        )
    except Exception:
        # Fallback: return basic content
        return SubNode(
            title=subnode_title,
            description=subnode_description,
            key_points=subnode_key_points,
            detailed_content=f"# {subnode_title}\n\n{subnode_description}\n\n" +
                           "\n".join([f"- {kp}" for kp in subnode_key_points]),
        )


async def run_step2_5(
    subnode: SubNode | dict,
    section_title: str,
    topic: str,
    level: str = "intermediate",
    detail_level: str = "detailed",
) -> SubNode:
    """
    Step 2.5: Generate detailed content for a sub-node.

    Args:
        subnode: The sub-node to expand (SubNode object or dict)
        section_title: Parent section title
        topic: Main learning topic
        level: Difficulty level
        detail_level: "concise" (30-60s) or "detailed" (2min)

    Returns:
        SubNode with detailed_content filled

    Cache: Results are cached by (topic, section_title, subnode_title, detail_level)
    """
    # Handle both SubNode object and dict
    if isinstance(subnode, SubNode):
        subnode_title = subnode.title
        subnode_description = subnode.description
        subnode_key_points = subnode.key_points
    else:
        subnode_title = subnode.get("title", "")
        subnode_description = subnode.get("description", "")
        subnode_key_points = subnode.get("key_points", [])

    # Check cache first
    cache_key = _get_cache_key(topic, section_title, subnode_title, detail_level)
    cached_result = _load_from_cache(cache_key)
    if cached_result:
        return cached_result

    # Generate new content
    result = await generate_subnode_detail(
        subnode_title=subnode_title,
        subnode_description=subnode_description,
        subnode_key_points=subnode_key_points,
        section_title=section_title,
        topic=topic,
        level=level,
        detail_level=detail_level,
    )

    # Save to cache
    _save_to_cache(cache_key, result)

    return result
