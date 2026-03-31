from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from learnpathly_langchain.service import generate_learning_path


router = APIRouter(prefix="/ai-path", tags=["ai-path"])


class AiPathGenerateRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User natural-language goal")


class AiPathGenerateResponse(BaseModel):
    data: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)


def _build_text_first_query(query: str) -> str:
    return (
        f"{query}\n\n"
        "请生成一份“文字讲解为主、资源链接为辅”的学习路径。要求："
        "1) 先给出足够详细的路径总览与核心概念解释；"
        "2) 每个学习节点的description要有可直接学习的知识点、原理、常见误区、操作步骤；"
        "2.1) summary 尽量达到 120 字以上；每个节点description尽量达到 80 字以上；"
        "3) 可以给资源链接，但链接只是补充，不要让回答依赖外链才能理解核心内容；"
        "4) 严格围绕用户原始主题，不要偷换概念。"
    )


def _extract_anchor_terms(query: str) -> list[str]:
    q = str(query or "").strip()
    if not q:
        return []

    quoted = re.findall(r"[\"'`“”‘’]([^\"'`“”‘’]{2,64})[\"'`“”‘’]", q)
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


def _build_stage_explanation(query: str, stage_title: str, stage_desc: str, stage_order: int) -> str:
    base_desc = stage_desc.strip() or f"聚焦 {stage_title} 的核心知识与实操方法。"
    return (
        f"阶段 {stage_order}「{stage_title}」将围绕你的目标“{query}”展开。"
        f"本阶段重点是：{base_desc}"
        "你需要先理解关键概念及其适用边界，再通过小任务验证理解是否正确。"
        "常见误区是只看资料不练习、或直接跳过基础导致后续卡住，建议每次学习后都做一次小结并输出可复用笔记。"
    )


def _build_stage_tutorial(stage_title: str, stage_desc: str, stage_order: int) -> list[str]:
    desc = stage_desc.strip() or f"学习 {stage_title} 的基础知识"
    return [
        f"步骤1（阶段准备）：明确阶段 {stage_order} 的学习目标，列出你当前与“{stage_title}”相关的已知与未知点。",
        f"步骤2（概念学习）：围绕“{stage_title}”系统学习核心原理，重点吸收：{desc}。",
        "步骤3（动手实践）：完成一个最小可运行练习，将抽象概念转化为可验证结果。",
        "步骤4（纠错优化）：对练习结果进行复盘，定位错误原因并做二次改进，形成自己的避坑清单。",
        "步骤5（阶段验收）：用自己的话讲清楚本阶段关键知识，并沉淀一份可复用的学习笔记/操作清单。",
    ]


def _enrich_nodes_with_stage_details(data: dict[str, Any], query: str) -> dict[str, Any]:
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
            explanation = _build_stage_explanation(query, stage_title, stage_desc, stage_order)

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

    return summary_len >= 60 and total_desc_len >= max(180, node_count * 40) and avg_desc_len >= 40


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
        if data is None and any(k in payload_obj for k in ("title", "summary", "nodes")):
            data = payload_obj
    elif isinstance(payload_obj, list):
        data = {"nodes": payload_obj}
    else:
        try:
            as_dict = dict(payload_obj)
            if isinstance(as_dict, dict):
                data = as_dict.get("data")
                warnings = as_dict.get("warnings")
                if data is None and any(k in as_dict for k in ("title", "summary", "nodes")):
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

        retry_query = (
            f"{query}\n\n"
            "请严格围绕用户原始关键词生成路径，不要替换术语，不要扩展为相似但不同概念。"
            "并且要求回答以详细文字讲解为主："
            "summary尽量120字以上、每个节点description尽量80字以上，"
            "且description包含概念解释、关键步骤和常见误区，"
            "让用户不点外部URL也能学到大部分知识。"
        )
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

        merged_warnings = [*warnings, *retry_warnings, "已自动重试：返回内容已按“文字讲解为主、链接为辅”强化"]
        if not _is_text_rich_enough(retry_data):
            merged_warnings.append("当前结果细节仍偏少，建议在提问中补充学习背景、时间投入和目标深度")

        return AiPathGenerateResponse(data=retry_data, warnings=merged_warnings)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LangChain generation failed: {exc}") from exc
