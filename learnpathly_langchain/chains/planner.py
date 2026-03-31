from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import Intent, PlanNode
from ._json_utils import extract_json, unwrap_if_nested


def _fallback_plan(intent: Intent) -> list[PlanNode]:
    titles = [
        "LLM 基础与核心概念",
        "Prompt Engineering 实战",
        "RAG 与知识库构建",
        "Agent 与工具调用",
        "评估、优化与上线",
    ]
    plan = [
        PlanNode(
            title=title,
            description=f"围绕{intent.goal}完成该阶段核心能力构建。",
            order=idx + 1,
        )
        for idx, title in enumerate(titles[: settings.max_nodes])
    ]
    return plan


def run_planner(intent: Intent) -> list[PlanNode]:
    if not settings.openai_api_key:
        return _fallback_plan(intent)

    llm_kwargs = {
        "model": settings.model_planner,
        "api_key": settings.openai_api_key,
        "temperature": 0.2,
    }
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url
    llm = ChatOpenAI(**llm_kwargs)
    prompt = ChatPromptTemplate.from_template(
        """
你是课程架构师。根据意图设计递进学习路径，不要输出资源。直接输出 JSON 数组，不要包含其他内容。

意图：{intent}
约束：
- 节点数量 3 到 {max_nodes}
- 每个节点必须可执行、可学习
- 顺序必须递进

输出格式（严格 JSON 数组）：
[{{"title": "阶段名", "description": "该阶段学什么", "order": 1}}, ...]
"""
    )

    chain = prompt | llm
    response = chain.invoke({"intent": intent.model_dump(), "max_nodes": settings.max_nodes})
    data = extract_json(response.content)
    if isinstance(data, dict):
        data = (
            data.get("plan")
            or data.get("nodes")
            or unwrap_if_nested(data, "plan")
            or unwrap_if_nested(data, "nodes")
            or list(data.values())[0]
        )

    if not isinstance(data, list):
        data = [data]

    plan_nodes: list[PlanNode] = []
    for idx, item in enumerate(data):
        if isinstance(item, PlanNode):
            plan_nodes.append(item)
        elif isinstance(item, dict):
            plan_nodes.append(PlanNode(**item))
        elif isinstance(item, str):
            title = item.strip()
            if not title:
                continue
            plan_nodes.append(
                PlanNode(
                    title=title,
                    description=f"围绕{intent.goal}完成该阶段核心能力构建。",
                    order=idx + 1,
                )
            )
        else:
            continue

    plan_nodes.sort(key=lambda n: n.order)
    if len(plan_nodes) < 3:
        return _fallback_plan(intent)
    return plan_nodes
