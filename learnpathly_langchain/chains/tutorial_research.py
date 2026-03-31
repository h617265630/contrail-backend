from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import Intent, LearningNode, TutorialContext, TutorialSnippet
from ..tools import search_github, search_web, search_youtube
from ._json_utils import extract_json, unwrap_if_nested


def _build_raw_tutorial_corpus(intent: Intent) -> list[dict]:
    query = intent.goal
    items: list[dict] = []
    items.extend(search_web(f"{query} 教程"))
    items.extend(search_web(f"{query} 实战"))
    items.extend(search_github(f"{query} tutorial"))
    items.extend(search_youtube(f"{query} full course"))
    return items[: max(6, settings.retrieval_top_k * 2)]


def _fallback_tutorial_context(intent: Intent, raw_items: list[dict]) -> tuple[TutorialContext, list[LearningNode]]:
    """返回 TutorialContext 和预设的 LearningNode 列表（用于 fallback）"""
    links: list[str] = []
    for item in raw_items:
        url = item.get("url")
        if isinstance(url, str) and url and url not in links:
            links.append(url)
        if len(links) >= 8:
            break

    # 根据意图生成更具体的知识点
    goal_lower = intent.goal.lower()
    if "llm" in goal_lower or "大语言模型" in intent.goal:
        key_knowledge = [
            "Transformer 架构",
            "注意力机制",
            "Prompt Engineering",
            "RAG 检索增强生成",
            "LangChain",
            "模型微调",
            "向量数据库",
            "Agent 系统",
        ]
        suggested_nodes = [
            "LLM 基础概念",
            "Prompt 工程",
            "RAG 与知识库",
            "LangChain 开发",
            "Agent 与工具调用",
            "项目实战",
        ]
        subnode_titles = {
            "LLM 基础概念": ["Transformer", "注意力机制", "GPT 系列", "开源模型"],
            "Prompt 工程": ["零样本提示", "少样本提示", "思维链", "结构化输出"],
            "RAG 与知识库": ["向量检索", "文本分割", "混合检索", "重排序"],
            "LangChain 开发": ["LCEL", "Chain", "Agent", "Memory"],
            "Agent 与工具调用": ["ReAct", "Tool Use", "Planning", "Reflection"],
            "项目实战": ["需求分析", "架构设计", "编码实现", "测试部署"],
        }
    elif "python" in goal_lower:
        key_knowledge = ["变量与数据类型", "函数与模块", "面向对象", "异步编程", "装饰器", "生成器"]
        suggested_nodes = ["Python 基础", "函数与模块", "面向对象", "项目实战"]
        subnode_titles = {
            "Python 基础": ["变量类型", "控制流", "数据结构", "文件操作"],
            "函数与模块": ["参数传递", "匿名函数", "模块导入", "包管理"],
            "面向对象": ["类与对象", "继承多态", "魔术方法", "设计模式"],
            "项目实战": ["需求分析", "代码实现", "测试优化", "部署上线"],
        }
    elif "react" in goal_lower or "前端" in intent.goal:
        key_knowledge = ["组件化思想", "State 管理", "Hooks", "TypeScript", "Next.js", "Tailwind"]
        suggested_nodes = ["前端基础", "React 核心", "React 进阶", "全栈开发"]
        subnode_titles = {
            "前端基础": ["HTML/CSS", "JavaScript", "ES6+", "DOM 操作"],
            "React 核心": ["JSX", "Component", "State/Hooks", "生命周期"],
            "React 进阶": ["Context", "Redux/Zustand", "性能优化", "测试"],
            "全栈开发": ["Next.js", "API Routes", "数据库", "Auth"],
        }
    else:
        key_knowledge = [
            f"{intent.goal} 核心概念",
            "理论基础",
            "工具生态",
            "最佳实践",
            "项目开发",
        ]
        suggested_nodes = [
            "基础概念",
            "核心技术",
            "项目实战",
            "部署优化",
        ]
        subnode_titles = {
            "基础概念": ["概念1", "概念2", "核心术语"],
            "核心技术": ["技术1", "技术2", "核心用法"],
            "项目实战": ["需求分析", "编码实现", "测试上线"],
            "部署优化": ["性能优化", "监控日志", "持续集成"],
        }

    # 生成预设的 LearningNode 列表
    preset_nodes = []
    for idx, node_title in enumerate(suggested_nodes[: settings.max_nodes]):
        order_code = str(idx)
        node_key_points = key_knowledge[idx * 2 : idx * 2 + 3] if key_knowledge else [f"{node_title}核心知识"]
        node_subnode_titles = subnode_titles.get(node_title, [f"{node_title}基础", f"{node_title}进阶", f"{node_title}实战"])

        subnodes = []
        for sub_idx, sub_title in enumerate(node_subnode_titles[:4]):
            # 尝试找到与子主题相关的 key_knowledge 来生成更具体的 learning_points
            related_knowledge = []
            core_topic = sub_title.replace("基础", "").replace("进阶", "").replace("实战", "").strip()

            if key_knowledge:
                for kw in key_knowledge:
                    # 如果 key_knowledge 中包含子主题的核心词，或者子主题的核心词包含在 key_knowledge 中
                    if any(word in kw for word in core_topic.split() if len(word) > 1):
                        related_knowledge.append(kw)
                # 如果找不到，尝试从节点 key_points 中找
                if not related_knowledge:
                    for kp in node_key_points:
                        if any(word in kp for word in core_topic.split() if len(word) > 1):
                            related_knowledge.append(kp)

            # 根据是否有相关知识生成更具体的 learning_points
            if related_knowledge:
                lp0 = f"理解 {sub_title} 与 {related_knowledge[0]} 的关系及其核心原理"
            else:
                lp0 = f"深入理解 {sub_title} 的核心概念与原理"

            learning_points = [
                lp0,
                f"掌握 {sub_title} 的核心用法与工程实践",
                f"完成 {sub_title} 相关的实战练习与项目应用",
            ]

            subnodes.append({
                "order_code": f"{order_code}.{sub_idx + 1}",
                "title": sub_title,
                "description": f"学习 {sub_title} 的核心知识与实践",
                "learning_points": learning_points,
                "resources": [],
            })

        preset_nodes.append(LearningNode(
            order_code=order_code,
            title=node_title,
            description=f"围绕 {intent.goal} 的 {node_title} 阶段",
            key_points=node_key_points,
            subnodes=subnodes,
            resources=[],
        ))

    snippets = [
        TutorialSnippet(
            title="最小可运行示例",
            language="python",
            snippet="pip install langchain openai",
            source_url=links[0] if links else "",
        )
    ]

    tutorial_context = TutorialContext(
        query=intent.goal,
        key_knowledge=key_knowledge,
        suggested_nodes=suggested_nodes,
        subnode_titles=subnode_titles,
        code_snippets=snippets,
        reference_links=links,
    )

    return tutorial_context, preset_nodes


def run_tutorial_research(intent: Intent) -> tuple[TutorialContext, list[LearningNode]]:
    """返回 TutorialContext 和预设的 LearningNode 列表"""
    raw_items = _build_raw_tutorial_corpus(intent)
    if not settings.openai_api_key:
        return _fallback_tutorial_context(intent, raw_items)

    llm_kwargs = {
        "model": settings.model_planner,
        "api_key": settings.openai_api_key,
        "temperature": 0.1,
    }
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url
    llm = ChatOpenAI(**llm_kwargs)

    # 新的 prompt：直接生成完整的学习节点结构
    prompt = ChatPromptTemplate.from_template(
        """
你是技术教程研究助手 + 课程架构师。根据检索到的教程信息，直接生成完整的递进学习路径 JSON，直接输出 JSON，不要解释、不要其他内容。

学习目标：{goal}
教程候选（标题/描述/链接）：{raw_items}

输出格式（严格 JSON 对象，包含 tutorial_context 和 nodes 两个字段）：
{{
  "tutorial_context": {{
    "query": "学习目标",
    "key_knowledge": ["具体技术点1", "具体技术点2", "具体技术点3", "..."],
    "suggested_nodes": ["具体阶段名称1", "具体阶段名称2", "具体阶段名称3", "..."],
    "subnode_titles": {{
      "具体阶段名称1": ["具体子主题1", "具体子主题2", "具体子主题3"],
      "具体阶段名称2": ["具体子主题1", "具体子主题2", "具体子主题3"]
    }},
    "code_snippets": [...],
    "reference_links": ["https://..."]
  }},
  "nodes": [
    {{
      "order_code": "0",
      "title": "具体阶段名称（必须来自 suggested_nodes）",
      "description": "阶段描述",
      "key_points": ["与该阶段相关的具体知识点1", "知识点2", "知识点3"],
      "subnodes": [
        {{
          "order_code": "0.1",
          "title": "具体子主题（来自 subnode_titles）",
          "description": "子主题描述",
          "learning_points": [
            "深入理解 {title} 的核心原理与机制",
            "掌握 {title} 的核心用法与最佳实践",
            "完成 {title} 相关的实战练习"
          ],
          "resources": []
        }}
      ],
      "resources": []
    }}
  ]
}}

重要要求：
1. key_knowledge 要非常具体，列出该领域的关键技术名词（至少 8 条）
2. suggested_nodes 要具体（至少 4-6 个阶段），不是泛泛的"基础概念"
3. subnode_titles 中每个主节点下的子主题要具体（3-4 个）
4. nodes 中的 title 必须完全匹配 suggested_nodes 中的名称！
5. nodes 中的子节点 title 必须来自 subnode_titles 中对应的列表！
6. 每个子节点的 learning_points 要针对该子主题具体编写！
7. reference_links 必须来自候选链接

高质量 learning_points 示例（请参照这种具体程度）：
- 子主题 "Transformer" → ["理解 Self-Attention 和 Multi-Head Attention 的计算原理", "掌握 Transformer 编码器和解码器的结构与数据流", "能够用 Python 从零实现简化版 Transformer"]
- 子主题 "零样本提示" → ["理解零样本提示的原理、使用场景与局限性", "掌握设计有效零样本提示的技巧（角色设定、格式约束）", "在实际任务中应用零样本提示并评估效果"]
- 子主题 "向量检索" → ["理解向量数据库的原理和 ANN 算法", "掌握 Embedding 模型的选择与使用", "实现基于向量检索的相似度匹配实战"]
"""
    )

    try:
        chain = prompt | llm
        response = chain.invoke({"goal": intent.goal, "raw_items": raw_items})
        data = extract_json(response.content)
        data = unwrap_if_nested(data, "TutorialContext")

        tutorial_context = TutorialContext(**data.get("tutorial_context", {}))
        nodes_data = data.get("nodes", [])

        nodes = []
        for idx, node_data in enumerate(nodes_data):
            if isinstance(node_data, dict):
                node_data.setdefault("order_code", str(idx))
                # 确保子节点的 learning_points 不是空的
                for subnode in node_data.get("subnodes", []):
                    if not subnode.get("learning_points"):
                        subnode["learning_points"] = [
                            f"理解 {subnode.get('title', '')} 的核心概念",
                            f"掌握 {subnode.get('title', '')} 的使用方法",
                            f"完成 {subnode.get('title', '')} 的实战练习",
                        ]
                nodes.append(LearningNode(**node_data))

        # 按 order_code 排序
        nodes.sort(key=lambda n: n.order_code)

        if len(nodes) < 3:
            fallback_ctx, fallback_nodes = _fallback_tutorial_context(intent, raw_items)
            return fallback_ctx, fallback_nodes

        return tutorial_context, nodes

    except Exception:
        fallback_ctx, fallback_nodes = _fallback_tutorial_context(intent, raw_items)
        return fallback_ctx, fallback_nodes
