import json
import os
import re
from typing import Any

from dotenv import load_dotenv

from .prompts import build_learning_path_prompt, build_refine_prompt
from .schemas import LearningPathResult

load_dotenv()


from .config import path_gen_settings


def _get_llm():
    """获取 LLM 实例"""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise ImportError("请安装 langchain-openai: pip install langchain-openai")

    settings = path_gen_settings

    if not settings.openai_api_key:
        raise ValueError("未设置 OPENAI_API_KEY 或 MINIMAX_API_KEY 环境变量")

    kwargs = {
        "model": settings.model,
        "api_key": settings.openai_api_key,
        "temperature": settings.temperature,
    }
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url

    return ChatOpenAI(**kwargs)


def _extract_json(text: str) -> dict[str, Any]:
    """从 LLM 输出中提取 JSON"""
    text = text.strip()

    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试提取 ```json ... ``` 块（处理多行 JSON）
    json_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试提取 ``` ... ``` 块
    code_match = re.search(r"```\s*(\{[\s\S]*?\})\s*```", text)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试找到第一个 { 到最后一个 } 之间的内容
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"无法从文本中提取 JSON: {text[:200]}")


def _parse_and_validate(result_text: str) -> LearningPathResult:
    """解析 LLM 输出并验证"""
    data = _extract_json(result_text)

    # 处理可能的嵌套结构
    if "data" in data:
        data = data["data"]

    # 确保有必要的字段
    if "nodes" not in data:
        data["nodes"] = []
    if "title" not in data:
        data["title"] = "学习路径"
    if "summary" not in data:
        data["summary"] = "学习路径已生成"

    return LearningPathResult.model_validate(data)


def generate_learning_path(query: str) -> LearningPathResult:
    """
    根据用户输入生成学习路径

    Args:
        query: 用户输入，如 "我想要学习react 全栈"

    Returns:
        LearningPathResult: 结构化的学习路径结果
    """
    if not query or not query.strip():
        raise ValueError("query 不能为空")

    query = query.strip()

    try:
        llm = _get_llm()
        prompt = build_learning_path_prompt(query)
        chain = prompt | llm

        response = chain.invoke({"query": query})
        result = _parse_and_validate(response.content)

        # 简单的质量检查
        if not result.nodes:
            raise ValueError("生成结果为空")

        # 检查节点描述长度
        for node in result.nodes:
            if len(node.description) < 40:
                # 描述太短，尝试优化
                result = _try_refine(query, result)

        return result

    except ImportError as e:
        raise ImportError(f"LangChain OpenAI 模块未安装: {e}")
    except Exception as e:
        raise RuntimeError(f"生成学习路径失败: {e}")


def _try_refine(query: str, result: LearningPathResult) -> LearningPathResult:
    """尝试优化生成结果"""
    try:
        llm = _get_llm()
        refine_prompt = build_refine_prompt(query)

        # 构建当前结果
        current_json = result.model_dump_json(indent=2)

        full_prompt = f"""
当前生成的学习路径：
{current_json}

{refine_prompt}

请直接输出优化后的完整 JSON，不要有任何解释。
"""
        response = llm.invoke(full_prompt)
        return _parse_and_validate(response.content)
    except Exception:
        # 优化失败，返回原结果
        return result
