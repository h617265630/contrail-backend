from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import Intent, LearningNode, LearningSubNode, TutorialContext
from ._json_utils import extract_json, unwrap_if_nested


def _build_subnodes(parent_order: str, titles: list[str], key_knowledge: list[str] | None = None) -> list[LearningSubNode]:
    """根据子节点标题生成 LearningSubNode 列表"""
    subnodes = []
    for idx, title in enumerate(titles[:4]):
        # 去掉"基础"、"进阶"、"实战"后缀，得到核心技术词
        core_topic = title.replace("基础", "").replace("进阶", "").replace("实战", "").strip()

        # 根据 core_topic 找到相关的 key_knowledge
        related_points = []
        if key_knowledge:
            for kw in key_knowledge:
                if core_topic in kw or kw in core_topic:
                    related_points.append(kw)
            if len(related_points) < 3:
                # 补充一些通用学习点
                related_points.extend([
                    f"{core_topic} 的核心原理",
                    f"{core_topic} 的应用场景",
                    f"{core_topic} 的实践方法",
                ])
        else:
            related_points = [
                f"{core_topic} 的核心原理",
                f"{core_topic} 的应用场景",
                f"{core_topic} 的实践方法",
            ]

        subnode = LearningSubNode(
            order_code=f"{parent_order}.{idx + 1}",
            title=title,
            description=f"学习 {core_topic} 的核心知识与实践",
            learning_points=related_points[:3],
            resources=[],
        )
        subnodes.append(subnode)
    return subnodes


def _find_matching_subnodes(title: str, subnode_titles: dict) -> list[str] | None:
    """模糊匹配找到对应的子节点标题列表"""
    # 精确匹配
    if title in subnode_titles:
        return subnode_titles[title]

    # 模糊匹配：检查 title 是否包含某个 key
    for key, values in subnode_titles.items():
        if key in title or title in key:
            return values

    # 检查 title 中的关键词是否匹配某个 key
    for key, values in subnode_titles.items():
        key_parts = key.lower().split()
        title_parts = title.lower().split()
        if any(kp in title_parts for kp in key_parts):
            return values

    return None


def _fallback_plan(intent: Intent, tutorial_context: TutorialContext) -> list[LearningNode]:
    """无 API key 时的默认规划"""
    suggested_nodes = tutorial_context.suggested_nodes or [
        "基础概念",
        "核心技术",
        "项目实战",
        "部署优化",
    ]

    nodes = []
    for idx, title in enumerate(suggested_nodes[: settings.max_nodes]):
        order_code = str(idx)

        # 从 key_knowledge 中取该节点相关的知识点
        start_idx = idx * 2
        end_idx = start_idx + 3
        key_knowledge = tutorial_context.key_knowledge[start_idx:end_idx] if tutorial_context.key_knowledge else [f"{title}核心知识"]

        # 优先使用 tutorial_context 中的 subnode_titles（带模糊匹配）
        subnode_titles_list = None
        if tutorial_context.subnode_titles:
            subnode_titles_list = _find_matching_subnodes(title, tutorial_context.subnode_titles)

        if not subnode_titles_list:
            # 回退到默认子节点
            subnode_titles_list = [f"{title}基础", f"{title}进阶", f"{title}实战"]

        node = LearningNode(
            order_code=order_code,
            title=title,
            description=f"围绕{intent.goal}的{title}阶段",
            key_points=key_knowledge,
            subnodes=_build_subnodes(order_code, subnode_titles_list),
            resources=[],
        )
        nodes.append(node)

    return nodes


def run_planner(intent: Intent, tutorial_context: TutorialContext) -> list[LearningNode]:
    """根据意图和教程上下文生成学习节点"""
    if not settings.openai_api_key:
        return _fallback_plan(intent, tutorial_context)

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
你是课程架构师。根据意图和教程提炼的信息，设计递进学习路径，直接输出 JSON 数组，不要包含其他内容。

意图：{intent}
教程提炼关键知识点：{key_knowledge}
教程建议阶段（使用这些作为主节点标题）：{suggested_nodes}
每个主节点下的具体子主题（subnode_titles 是字典，key 是主节点名，value 是子主题列表）：{subnode_titles}

约束：
- 主节点数量 3 到 {max_nodes}
- 主节点标题必须使用 suggested_nodes 中的名称！
- 子节点标题必须使用 subnode_titles 中对应主节点的子主题列表！
- 主节点编号用 0, 1, 2 ... 表示
- 子节点编号用 0.1, 0.2, 1.1, 1.2 ... 表示
- 每个子节点列出 3 个学习重点(learning_points)
- 顺序必须递进

重要示例：
如果 suggested_nodes = ["LLM 基础概念", "Prompt 工程"]
且 subnode_titles = {{"LLM 基础概念": ["Transformer", "注意力机制", "GPT 系列"], "Prompt 工程": ["零样本提示", "少样本提示"]}}

则输出应该是：
[{{
  "order_code": "0",
  "title": "LLM 基础概念",
  "description": "...",
  "key_points": [...],
  "subnodes": [
    {{"order_code": "0.1", "title": "Transformer", ...}},
    {{"order_code": "0.2", "title": "注意力机制", ...}},
    {{"order_code": "0.3", "title": "GPT 系列", ...}}
  ]
}}, {{
  "order_code": "1",
  "title": "Prompt 工程",
  ...
}}]

输出格式（严格 JSON 数组）：
[{{
  "order_code": "0",
  "title": "主节点名称（必须来自 suggested_nodes）",
  "description": "阶段描述",
  "key_points": ["具体知识点1", "具体知识点2", "具体知识点3"],
  "subnodes": [
    {{"order_code": "0.1", "title": "子主题（必须来自 subnode_titles）", "description": "", "learning_points": ["重点1", "重点2", "重点3"], "resources": []}}
  ],
  "resources": []
}}, ...]
"""
    )

    chain = prompt | llm
    response = chain.invoke(
        {
            "intent": intent.model_dump(),
            "max_nodes": settings.max_nodes,
            "key_knowledge": tutorial_context.key_knowledge,
            "suggested_nodes": tutorial_context.suggested_nodes,
            "subnode_titles": tutorial_context.subnode_titles,
        }
    )

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

    plan_nodes: list[LearningNode] = []
    for idx, item in enumerate(data):
        if isinstance(item, LearningNode):
            plan_nodes.append(item)
        elif isinstance(item, dict):
            node_data = dict(item)
            # 确保有 order_code
            if "order_code" not in node_data:
                node_data["order_code"] = str(idx)
            plan_nodes.append(LearningNode(**node_data))
        elif isinstance(item, str):
            title = item.strip()
            if not title:
                continue
            plan_nodes.append(
                LearningNode(
                    order_code=str(idx),
                    title=title,
                    description=f"围绕{intent.goal}的{title}阶段",
                    key_points=tutorial_context.key_knowledge[idx * 3 : idx * 3 + 3] if tutorial_context.key_knowledge else [f"{title}核心知识"],
                    subnodes=_build_subnodes(str(idx), [f"{title}基础", f"{title}进阶", f"{title}实战"]),
                    resources=[],
                )
            )
        else:
            continue

    # 按 order_code 排序
    plan_nodes.sort(key=lambda n: n.order_code)
    if len(plan_nodes) < 3:
        return _fallback_plan(intent, tutorial_context)

    # 后处理：优化 learning_points，使其更具体
    for node in plan_nodes:
        if node.subnodes and tutorial_context.key_knowledge:
            # 尝试找到与主节点相关的 key_knowledge
            related_knowledge = []
            for kw in tutorial_context.key_knowledge:
                if any(word in kw.lower() for word in node.title.lower().split()):
                    related_knowledge.append(kw)

            if not related_knowledge:
                related_knowledge = tutorial_context.key_knowledge[:3]

            for subnode in node.subnodes:
                if len(subnode.learning_points) == 3:
                    # 替换为更具体的 learning_points
                    subnode.learning_points = [
                        f"理解 {subnode.title} 的核心概念与 {related_knowledge[0] if related_knowledge else '相关技术'} 的关系" if related_knowledge else f"理解 {subnode.title} 的核心概念",
                        f"掌握 {subnode.title} 在实际项目中的应用方法",
                        f"完成 {subnode.title} 相关的动手实践任务",
                    ]

    return plan_nodes
