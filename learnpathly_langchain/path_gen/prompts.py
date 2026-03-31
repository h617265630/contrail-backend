from langchain_core.prompts import ChatPromptTemplate


def build_learning_path_prompt(query: str) -> ChatPromptTemplate:
    """
    构建生成学习路径的 Prompt
    要求 LLM 输出严格符合 LearningPathResult 结构的 JSON
    """
    template = """你是一个专业的学习路径规划专家。根据用户输入，生成一份结构化的学习路径。

用户输入：{query}

请严格按照以下 JSON 格式输出，不要包含任何其他内容：

{{
    "title": "学习路径标题",
    "summary": "2-3句话的整体概览，介绍该学习路径的核心内容和学习方法",
    "nodes": [
        {{
            "title": "关键学习点1（如 React 基础/状态管理/全栈开发等）",
            "description": "详细介绍，包含核心概念、关键步骤、常见误区等，至少80字",
            "sub_nodes": [
                {{
                    "title": "子学习点标题",
                    "description": "子学习点的详细描述，至少80字",
                    "resources": [
                        {{"url": "https://..."}}
                    ]
                }}
            ],
            "resources": [
                {{"url": "https://github.com/..."}},
                {{"url": "https://youtube.com/..."}},
                {{"url": "https://react.dev/..."}}
            ]
        }}
    ]
}}

要求：
1. title 要简洁明确，如 "React 全栈学习路径"
2. summary 要概括整体学习思路和方法
3. 每个节点的 description 至少 80 字，包含可直接学习的知识点和实践步骤
4. sub_nodes 是该关键学习点下的子主题，如果没有子主题则为空数组
5. resources 只放 URL，每个节点建议 2-5 个高质量资源链接
6. 资源类型要多样化：GitHub 仓库、YouTube 视频、官方文档、优质博客等
7. 严格按照 JSON 格式输出，不要有任何额外文本

请生成学习路径："""
    return ChatPromptTemplate.from_template(template)


def build_refine_prompt(original_query: str) -> str:
    """构建优化提示词，当首次生成结果不够详细时使用"""
    return f"""
请严格按照用户原始意图「{original_query}」生成学习路径。

补充要求：
1. 每个节点的 description 必须达到 120 字以上
2. 每个子节点的 description 必须达到 80 字以上
3. 确保所有资源链接都是有效的
4. 保持 JSON 格式不变
"""
