from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import (
    AbilityModel,
    Intent,
    LearningNode,
    LearningPathOutput,
    LearningPhase,
    Resource,
    TutorialContext,
)
from ._json_utils import extract_json, unwrap_if_nested


def _assign_resources_to_subnodes(
    nodes: list[LearningNode], resources: dict[str, list[Resource]]
) -> list[LearningNode]:
    """根据主节点资源为子节点分配相关资源"""
    for node in nodes:
        node_resources = resources.get(node.title, [])
        if not node_resources:
            continue

        for subnode in node.subnodes:
            # 找出与子节点标题相关的资源
            related = []
            for res in node_resources:
                # 检查资源标题或描述是否包含子节点标题的关键词
                res_text = f"{res.title} {res.description}".lower()
                subnode_keywords = subnode.title.lower().split()
                if any(kw in res_text for kw in subnode_keywords if len(kw) > 1):
                    related.append(res)

            # 如果找不到相关的，但子节点数量 <= 2，可以分配所有资源
            if not related and len(node.subnodes) <= 2:
                related = node_resources[:2]

            subnode.resources = related[:2]  # 每个子节点最多2个资源

    return nodes


def _fallback_generate(
    intent: Intent,
    plan: list[LearningNode],
    resources: dict[str, list[Resource]],
    _tutorial_context: TutorialContext,
) -> LearningPathOutput:
    """无 API key 时的默认生成"""
    nodes = [
        LearningNode(
            order_code=node.order_code,
            title=node.title,
            description=node.description,
            key_points=node.key_points,
            subnodes=node.subnodes,
            resources=resources.get(node.title, []),
        )
        for node in plan
    ]

    # 生成默认的学习阶段
    learning_phases = [
        LearningPhase(phase="第1阶段", duration="2周", nodes=[plan[0].order_code] if len(plan) > 0 else []),
        LearningPhase(phase="第2阶段", duration="2周", nodes=[plan[1].order_code] if len(plan) > 1 else []),
        LearningPhase(phase="第3阶段", duration="2周", nodes=[plan[2].order_code] if len(plan) > 2 else []),
    ]

    # 生成默认的能力模型
    ability_model = [
        AbilityModel(category="前端能力", skills=["组件设计", "状态管理", "UI架构"]),
        AbilityModel(category="后端能力", skills=["API设计", "数据库设计", "鉴权"]),
        AbilityModel(category="工程能力", skills=["CI/CD", "测试", "部署"]),
    ]

    return LearningPathOutput(
        title=f"{intent.goal} 学习路径",
        description="系统化学习路径，按照递进方式构建知识体系。",
        nodes=nodes,
        learning_phases=learning_phases,
        ability_model=ability_model,
        recommendations=[
            f"建议从 {plan[0].title} 开始",
            "每个阶段完成后进行实战练习",
            "定期回顾和总结",
        ] if plan else [],
    )


def _generate_recommendations(
    intent: Intent, plan: list[LearningNode], _phases: list[LearningPhase]
) -> list[str]:
    """根据意图和计划生成个性化建议"""
    recommendations = []

    # 基于用户水平的建议
    level_tips = {
        "beginner": "作为初学者，建议先夯实基础概念，不要急于求成，多做练习",
        "intermediate": "你有一定基础，可以更快推进，但记得加强实战",
        "advanced": "你已经具备相当经验，重点放在项目实战和能力拓展上",
    }
    recommendations.append(level_tips.get(intent.level, level_tips["beginner"]))

    # 基于时间的建议
    if intent.time_budget:
        recommendations.append(f"你的时间安排是 {intent.time_budget}，建议合理分配学习时间")

    # 基于焦点的建议
    if intent.focus:
        recommendations.append(f"重点关注：{', '.join(intent.focus[:3])}")

    # 来自第一阶段的具体建议
    if plan:
        first_node = plan[0]
        recommendations.append(f"建议从「{first_node.title}」开始，这是整个学习路径的基础")
        if first_node.subnodes:
            recommendations.append(f"具体可以先学习「{first_node.subnodes[0].title}」，它是后续内容的前提")

    # 实战建议
    recommendations.append("每个阶段完成后，尝试独立完成一个小项目来巩固所学")

    # 学习方法建议
    recommendations.append("善用 AI 助手辅助学习，但也要培养独立解决问题的能力")

    return recommendations


def run_generator(
    intent: Intent,
    plan: list[LearningNode],
    resources: dict[str, list[Resource]],
    tutorial_context: TutorialContext,
) -> LearningPathOutput:
    if not settings.openai_api_key:
        return _fallback_generate(intent, plan, resources, tutorial_context)

    llm_kwargs = {
        "model": settings.model_generator,
        "api_key": settings.openai_api_key,
        "temperature": 0.2,
    }
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url
    llm = ChatOpenAI(**llm_kwargs)

    # 生成标题和描述
    title_prompt = ChatPromptTemplate.from_template(
        """
你是学习路径命名专家。根据用户意图，为学习路径生成标题和描述，直接输出 JSON，不要包含其他内容。

意图: {intent}
学习阶段: {stage_titles}

输出格式（严格 JSON）：
{{"title": "学习路径标题", "description": "整体描述"}}
"""
    )

    stage_titles = [p.title for p in plan]
    try:
        chain = title_prompt | llm
        response = chain.invoke({"intent": intent.model_dump(), "stage_titles": stage_titles})
        data = extract_json(response.content)
        data = unwrap_if_nested(data, "LearningPathOutput")
        title = data.get("title", f"{intent.goal} 学习路径")
        description = data.get("description", "系统化学习路径，按照递进方式构建知识体系。")
    except Exception:
        title = f"{intent.goal} 学习路径"
        description = "系统化学习路径，按照递进方式构建知识体系。"

    # 生成学习阶段
    phase_prompt = ChatPromptTemplate.from_template(
        """
根据学习节点，生成推荐的学习阶段顺序，直接输出 JSON 数组，不要包含其他内容。

学习节点: {nodes}

输出格式（严格 JSON 数组）：
[{{"phase": "第1阶段", "duration": "2周", "nodes": ["0", "1"]}}, ...]
"""
    )

    try:
        chain = phase_prompt | llm
        response = chain.invoke({"nodes": [n.model_dump() for n in plan]})
        data = extract_json(response.content)
        if isinstance(data, list):
            learning_phases = [LearningPhase(**p) for p in data if isinstance(p, dict)]
        else:
            learning_phases = []
    except Exception:
        learning_phases = []

    # 生成能力模型
    ability_prompt = ChatPromptTemplate.from_template(
        """
根据学习内容，生成能力模型，直接输出 JSON 数组，不要包含其他内容。

学习目标: {intent}
学习节点: {nodes}
关键知识点: {key_points}

能力模型要求：
- 3-5 个能力分类
- 每个分类下的 skills 要具体，不要泛泛而谈
- 要体现该领域的核心技能

输出格式（严格 JSON 数组）：
[{{"category": "理论理解能力", "skills": ["注意力机制原理", "Transformer架构"]}},
 {{"category": "编程实践能力", "skills": ["Prompt编写", "RAG实现"]}},
 ...]
"""
    )

    key_points = []
    for node in plan:
        key_points.extend(node.key_points[:2])

    try:
        chain = ability_prompt | llm
        response = chain.invoke({"intent": intent.model_dump(), "nodes": [n.title for n in plan], "key_points": key_points})
        data = extract_json(response.content)
        if isinstance(data, list):
            ability_model = [AbilityModel(**a) for a in data if isinstance(a, dict)]
        else:
            ability_model = []
    except Exception:
        ability_model = []

    # 组装节点（带资源）
    nodes = [
        LearningNode(
            order_code=node.order_code,
            title=node.title,
            description=node.description,
            key_points=node.key_points,
            subnodes=node.subnodes,
            resources=resources.get(node.title, []),
        )
        for node in plan
    ]

    # 为子节点分配资源
    nodes = _assign_resources_to_subnodes(nodes, resources)

    # 生成个性化建议
    recommendations = _generate_recommendations(intent, plan, learning_phases)

    return LearningPathOutput(
        title=title,
        description=description,
        nodes=nodes,
        learning_phases=learning_phases,
        ability_model=ability_model,
        recommendations=recommendations,
    )
