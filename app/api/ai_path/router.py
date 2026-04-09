from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from learnpathly_langchain.service import generate_learning_path

from .prompts import (
    AI_AGENT_STAGE_EXPLANATIONS,
    AI_AGENT_STAGE_TUTORIALS,
    GENERIC_STAGE_EXPLANATION,
    GENERIC_STAGE_TUTORIAL,
    TEXT_FIRST_QUERY_TEMPLATE,
    RETRY_QUERY_TEMPLATE,
    AI_AGENT_KEYWORDS,
)


router = APIRouter(prefix="/ai-path", tags=["ai-path"])


class AiPathGenerateRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User natural-language goal")


class AiPathGenerateResponse(BaseModel):
    data: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)


def _build_text_first_query(query: str) -> str:
    return TEXT_FIRST_QUERY_TEMPLATE.format(query=query)


def _extract_anchor_terms(query: str) -> list[str]:
    q = str(query or "").strip()
    if not q:
        return []

    quoted = re.findall(r"[\"'`""'']([^\"'`""'']{2,64})[\"'`""'']", q)
    words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{3,}", q)
    cjk_chunks = re.findall(r"[\u4e00-\u9fff]{2,}", q)

    terms: list[str] = []
    for part in quoted + words + cjk_chunks:
        t = str(part).strip().lower()
        if not t:
            continue
        if t not in terms:
            terms.append(t)

    return terms[:5]


def _flatten_output_text(data: dict[str, Any]) -> str:
    parts: list[str] = []

    def _walk(value: Any):
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(k, str):
                    parts.append(k)
                _walk(v)
        elif isinstance(value, list):
            for item in value:
                _walk(item)
        elif isinstance(value, str):
            parts.append(value)
        elif value is not None:
            parts.append(str(value))

    _walk(data)
    return "\n".join(parts).lower()


def _is_relevant_to_query(data: dict[str, Any], query: str) -> bool:
    anchors = _extract_anchor_terms(query)
    if not anchors:
        return True

    text = _flatten_output_text(data)
    if not text:
        return False

    return any(term in text for term in anchors)


def _is_ai_agent_query(query: str) -> bool:
    lowered = str(query or "").lower()
    return any(keyword in lowered for keyword in AI_AGENT_KEYWORDS)


def _get_stage_key(stage_title: str) -> str | None:
    """Match stage title to a known AI agent stage category."""
    key = stage_title.lower()
    for category, config in AI_AGENT_STAGE_EXPLANATIONS.items():
        for keyword in config["keywords"]:
            if keyword in key:
                return category
    return None


def _build_ai_agent_stage_explanation(
    query: str, stage_title: str, stage_desc: str, stage_order: int
) -> str:
    key = _get_stage_key(stage_title)
    if key and key in AI_AGENT_STAGE_EXPLANATIONS:
        body = AI_AGENT_STAGE_EXPLANATIONS[key]["body"]
    else:
        base_desc = stage_desc.strip()
        body = (
            f"本阶段重点是：{base_desc or f'围绕 {stage_title} 建立可落地的理解与实践能力。'}"
            + GENERIC_STAGE_EXPLANATION
        )

    return f"阶段 {stage_order}「{stage_title}」将围绕你的目标「{query}」展开。{body}"


def _build_ai_agent_stage_tutorial(
    stage_title: str, stage_desc: str, stage_order: int
) -> list[str]:
    key = _get_stage_key(stage_title)
    if key and key in AI_AGENT_STAGE_TUTORIALS:
        return [
            step.format(stage_title=stage_title, stage_order=stage_order)
            for step in AI_AGENT_STAGE_TUTORIALS[key]
        ]

    desc = stage_desc.strip() or f"学习 {stage_title} 的基础知识"
    return [
        step.format(stage_title=stage_title, stage_order=stage_order, desc=desc)
        for step in GENERIC_STAGE_TUTORIAL
    ]


def _build_stage_explanation(
    query: str, stage_title: str, stage_desc: str, stage_order: int
) -> str:
    if _is_ai_agent_query(query):
        return _build_ai_agent_stage_explanation(
            query, stage_title, stage_desc, stage_order
        )

    base_desc = stage_desc.strip() or f"聚焦 {stage_title} 的核心知识与实操方法。"
    return (
        f"阶段 {stage_order}「{stage_title}」将围绕你的目标「{query}」展开。"
        f"本阶段重点是：{base_desc}"
        f"{GENERIC_STAGE_EXPLANATION}"
    )


def _build_stage_tutorial(
    stage_title: str, stage_desc: str, stage_order: int
) -> list[str]:
    if _is_ai_agent_query(stage_desc) or _is_ai_agent_query(stage_title):
        return _build_ai_agent_stage_tutorial(stage_title, stage_desc, stage_order)

    desc = stage_desc.strip() or f"学习 {stage_title} 的基础知识"
    return [
        step.format(stage_title=stage_title, stage_order=stage_order, desc=desc)
        for step in GENERIC_STAGE_TUTORIAL
    ]


def _enrich_nodes_with_stage_details(
    data: dict[str, Any], query: str
) -> dict[str, Any]:
    nodes = data.get("nodes") if isinstance(data.get("nodes"), list) else []
    if not nodes:
        return data

    enriched_nodes: list[dict[str, Any]] = []
    for idx, raw in enumerate(nodes):
        if not isinstance(raw, dict):
            continue

        stage_order = int(raw.get("order") or (idx + 1))
        stage_title = str(raw.get("title") or "").strip() or f"阶段 {stage_order}"
        stage_desc = str(raw.get("description") or "").strip()

        explanation = str(raw.get("explanation") or "").strip()
        if not explanation:
            explanation = _build_stage_explanation(
                query, stage_title, stage_desc, stage_order
            )

        tutorial_raw = raw.get("tutorial")
        tutorial: list[str]
        if isinstance(tutorial_raw, list):
            tutorial = [str(x).strip() for x in tutorial_raw if str(x).strip()]
        elif isinstance(tutorial_raw, str) and tutorial_raw.strip():
            tutorial = [tutorial_raw.strip()]
        else:
            tutorial = []

        if not tutorial:
            tutorial = _build_stage_tutorial(stage_title, stage_desc, stage_order)

        node = dict(raw)
        node["explanation"] = explanation
        node["tutorial"] = tutorial
        if not stage_desc:
            node["description"] = explanation
        enriched_nodes.append(node)

    merged = dict(data)
    merged["nodes"] = enriched_nodes
    return merged


def _is_text_rich_enough(data: dict[str, Any]) -> bool:
    summary = str(data.get("summary") or "").strip()
    nodes = data.get("nodes") if isinstance(data.get("nodes"), list) else []
    node_descs = [
        str((n or {}).get("description") or (n or {}).get("explanation") or "").strip()
        for n in nodes
        if isinstance(n, dict)
    ]

    summary_len = len(summary)
    total_desc_len = sum(len(x) for x in node_descs)
    node_count = len(node_descs)
    avg_desc_len = (total_desc_len / node_count) if node_count else 0

    if node_count == 0:
        return False

    return (
        summary_len >= 60
        and total_desc_len >= max(180, node_count * 40)
        and avg_desc_len >= 40
    )


def _parse_generation_result(result: Any) -> tuple[dict[str, Any], list[str]]:
    if hasattr(result, "model_dump"):
        payload_obj = result.model_dump()
    elif hasattr(result, "dict"):
        payload_obj = result.dict()
    else:
        payload_obj = result

    data: Any = {}
    warnings: Any = []

    if isinstance(payload_obj, dict):
        data = payload_obj.get("data")
        warnings = payload_obj.get("warnings")
        if data is None and any(
            k in payload_obj for k in ("title", "summary", "nodes")
        ):
            data = payload_obj
    elif isinstance(payload_obj, list):
        data = {"nodes": payload_obj}
    else:
        try:
            as_dict = dict(payload_obj)
            if isinstance(as_dict, dict):
                data = as_dict.get("data")
                warnings = as_dict.get("warnings")
                if data is None and any(
                    k in as_dict for k in ("title", "summary", "nodes")
                ):
                    data = as_dict
        except Exception:
            data = {}
            warnings = []

    data = data or {}
    warnings = warnings or []
    if not isinstance(data, dict):
        data = {}
    if not isinstance(warnings, list):
        warnings = []

    return data, [str(w) for w in warnings]


@router.post("/generate", response_model=AiPathGenerateResponse)
def generate_ai_path(payload: AiPathGenerateRequest) -> AiPathGenerateResponse:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    try:
        warnings: list[str] = []
        try:
            first_result = generate_learning_path(_build_text_first_query(query))
            data, first_warnings = _parse_generation_result(first_result)
            data = _enrich_nodes_with_stage_details(data, query)
            warnings.extend(first_warnings)
        except Exception:
            fallback_result = generate_learning_path(query)
            data, fallback_warnings = _parse_generation_result(fallback_result)
            data = _enrich_nodes_with_stage_details(data, query)
            warnings.extend(fallback_warnings)
            warnings.append("文本强化生成失败，已回退基础模式")

        is_relevant = _is_relevant_to_query(data, query)
        is_text_rich = _is_text_rich_enough(data)
        if is_relevant and is_text_rich:
            return AiPathGenerateResponse(data=data, warnings=warnings)

        if is_relevant:
            merged_warnings = list(warnings)
            if not is_text_rich:
                merged_warnings.append(
                    "当前结果细节仍偏少，建议在提问中补充学习背景、时间投入和目标深度"
                )
            return AiPathGenerateResponse(data=data, warnings=merged_warnings)

        retry_query = RETRY_QUERY_TEMPLATE.format(query=query)
        try:
            retry_result = generate_learning_path(retry_query)
            retry_data, retry_warnings = _parse_generation_result(retry_result)
            retry_data = _enrich_nodes_with_stage_details(retry_data, query)
        except Exception:
            if is_relevant:
                warnings.append("细节增强重试失败，已返回当前可用结果")
                return AiPathGenerateResponse(data=data, warnings=warnings)
            raise

        if not _is_relevant_to_query(retry_data, query):
            raise HTTPException(
                status_code=422,
                detail="生成结果与输入关键词不匹配，请换一种更明确的描述再试，或补充该对象的定义/上下文。",
            )

        merged_warnings = [
            *warnings,
            *retry_warnings,
            "已自动重试：返回内容已按「文字讲解为主、链接为辅」强化",
        ]
        if not _is_text_rich_enough(retry_data):
            merged_warnings.append(
                "当前结果细节仍偏少，建议在提问中补充学习背景、时间投入和目标深度"
            )

        return AiPathGenerateResponse(data=retry_data, warnings=merged_warnings)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"LangChain generation failed: {exc}"
        ) from exc
