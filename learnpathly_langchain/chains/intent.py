from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..config import settings
from ..schemas import Intent
from ._json_utils import extract_json, unwrap_if_nested


def _fallback_intent(user_input: str) -> Intent:
    lowered = user_input.lower()
    level = "beginner"
    if any(k in lowered for k in ["进阶", "advanced", "深入"]):
        level = "advanced"
    elif any(k in lowered for k in ["中级", "intermediate"]):
        level = "intermediate"

    focus = []
    if any(k in lowered for k in ["理论", "原理", "theory"]):
        focus.append("theory")
    if any(k in lowered for k in ["代码", "项目", "coding", "build"]):
        focus.append("coding")
    if any(k in lowered for k in ["部署", "上线", "deployment"]):
        focus.append("deployment")
    if not focus:
        focus = ["theory", "coding"]

    language = "zh" if any("\u4e00" <= ch <= "\u9fff" for ch in user_input) else settings.default_language
    return Intent(goal=user_input.strip(), level=level, focus=focus, language=language)


def run_intent(user_input: str) -> Intent:
    if not settings.openai_api_key:
        return _fallback_intent(user_input)

    llm_kwargs = {
        "model": settings.model_intent,
        "api_key": settings.openai_api_key,
        "temperature": 0.1,
    }
    if settings.openai_base_url:
        llm_kwargs["base_url"] = settings.openai_base_url
    llm = ChatOpenAI(**llm_kwargs)
    prompt = ChatPromptTemplate.from_template(
        """
你是学习规划助手。请根据用户输入提取结构化意图，直接输出 JSON 对象，不要包含其他内容。
用户输入：{user_input}

输出格式（严格 JSON）：
{{"goal": "学习目标字符串", "level": "beginner|intermediate|advanced", "focus": ["theory|coding|deployment|research"], "language": "zh|en", "time_budget": "用户提到的时间预算，没有则留空"}}
"""
    )

    chain = prompt | llm
    response = chain.invoke({"user_input": user_input})
    data = extract_json(response.content)
    data = unwrap_if_nested(data, "Intent")
    valid_levels = {"beginner", "intermediate", "advanced"}
    if data.get("level") not in valid_levels:
        data["level"] = "beginner"
    if not data.get("focus"):
        data["focus"] = ["theory", "coding"]
    return Intent(**data)
