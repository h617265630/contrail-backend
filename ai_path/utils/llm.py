"""
LLM provider factory.
Default: MiniMax Token Plan (M2.7). Supports OpenAI via LLM_PROVIDER=openai.
"""

from __future__ import annotations
import json
import os
import re
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    provider = os.getenv("LLM_PROVIDER", "minimax").lower()

    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=os.environ["OPENAI_API_KEY"],
            temperature=temperature,
        )

    # Default: MiniMax Token Plan
    # Docs: https://platform.minimaxi.com/document/ChatCompletion%20v1
    # Models: MiniMax-M2.7 | MiniMax-M2.7-highspeed
    return ChatOpenAI(
        model=os.getenv("MINIMAX_MODEL", "MiniMax-M2.7"),
        api_key=os.environ["MINIMAX_API_KEY"],
        base_url="https://api.minimaxi.com/v1",
        temperature=temperature,
    )


def parse_json_response(content: str) -> dict | list:
    """
    Parse JSON from LLM response content.
    Handles markdown code blocks and extracts JSON.
    Also handles thinking tags from MiniMax M2.7.
    """
    # Remove thinking tags (MiniMax M2.7 specific)
    if "<think>" in content or "</think>" in content:
        # Remove everything between <think> and </think>
        import re as _re
        content = _re.sub(r"<think>.*?</think>", "", content, flags=_re.DOTALL)

    # Remove markdown code blocks
    content = re.sub(r"```(?:json)?\s*", "", content.strip())
    content = re.sub(r"\s*```", "", content.strip())

    # Try direct json.loads
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON object from content (more robust)
    # Find the largest valid JSON object
    json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            if isinstance(result, dict) and result.get("sections"):
                return result
        except json.JSONDecodeError:
            pass

    # Try to find nested JSON with sections
    sections_match = re.search(r'"sections"\s*:\s*\[.*?\]', content, re.DOTALL)
    if sections_match:
        try:
            # Wrap in braces to make valid JSON
            wrapped = "{" + sections_match.group() + "}"
            return json.loads(wrapped)
        except json.JSONDecodeError:
            pass

    # Try to extract JSON array
    array_match = re.search(r"\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]", content, re.DOTALL)
    if array_match:
        try:
            return json.loads(array_match.group())
        except json.JSONDecodeError:
            pass

    # Return empty dict as fallback
    return {}
