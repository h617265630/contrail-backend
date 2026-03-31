from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import Intent, LearningPathNode, LearningPathOutput, PlanNode, Resource
from ._json_utils import extract_json, unwrap_if_nested


def _fallback_generate(intent: Intent, plan: list[PlanNode], resources: dict[str, list[Resource]]) -> LearningPathOutput:
    nodes = [
        LearningPathNode(
            title=node.title,
            description=node.description,
            order=node.order,
            resources=resources.get(node.title, []),
        )
        for node in plan
    ]
    return LearningPathOutput(
        title=f"{intent.goal} 学习路径",
        summary="按基础 -> 实战 -> 系统化构建的方式学习，并结合真实资源完成阶段目标。",
        nodes=nodes,
    )


def run_generator(intent: Intent, plan: list[PlanNode], resources: dict[str, list[Resource]]) -> LearningPathOutput:
    if not settings.openai_api_key:
        return _fallback_generate(intent, plan, resources)

    llm_kwargs = {
        "model": settings.model_generator,
        "api_key": settings.openai_api_key,
        "temperature": 0.2,
    }
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url
    llm = ChatOpenAI(**llm_kwargs)
    prompt = ChatPromptTemplate.from_template(
        """
你是学习路径命名专家。根据用户意图，为学习路径生成标题和总结，直接输出 JSON，不要包含其他内容。

意图: {intent}
学习阶段: {stage_titles}

输出格式（严格 JSON）：
{{"title": "学习路径标题", "summary": "2-3句话的整体总结"}}
"""
    )

    stage_titles = [p.title for p in plan]
    try:
        chain = prompt | llm
        response = chain.invoke({"intent": intent.model_dump(), "stage_titles": stage_titles})
        data = extract_json(response.content)
        data = unwrap_if_nested(data, "LearningPathOutput")
        title = data.get("title", f"{intent.goal} 学习路径")
        summary = data.get("summary", "按基础 -> 实战 -> 系统化构建的方式学习。")
    except Exception:
        title = f"{intent.goal} 学习路径"
        summary = "按基础 -> 实战 -> 系统化构建的方式学习，并结合真实资源完成阶段目标。"

    nodes = [
        LearningPathNode(
            title=node.title,
            description=node.description,
            order=node.order,
            resources=resources.get(node.title, []),
        )
        for node in plan
    ]
    return LearningPathOutput(title=title, summary=summary, nodes=nodes)
