from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

AIPATH_DIR = Path(__file__).resolve().parents[2] / "AIpath"
if str(AIPATH_DIR) not in sys.path:
    sys.path.insert(0, str(AIPATH_DIR))

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


def _is_ai_agent_query(query: str) -> bool:
    lowered = str(query or "").lower()
    keywords = [
        "ai agent",
        "agent",
        "智能体",
        "langchain",
        "langgraph",
        "rag",
        "tool calling",
        "function calling",
        "multi agent",
    ]
    return any(keyword in lowered for keyword in keywords) or "智能体" in str(query or "")


def _build_ai_agent_stage_explanation(query: str, stage_title: str, stage_desc: str, stage_order: int) -> str:
    stage_key = stage_title.lower()
    base_desc = stage_desc.strip()

    if "llm" in stage_key or "agent 基础" in stage_key:
        body = (
            "这一阶段的目标是先建立对 LLM 与 Agent 的正确认知。你需要理解大模型为什么能够完成问答、总结、规划等任务，"
            "同时分清“聊天机器人”“工作流”“真正具备工具调用与状态管理能力的 Agent”之间的区别。学习时要重点掌握上下文窗口、"
            "提示词对行为的影响、Agent 的输入输出边界，以及 ReAct 这类基础思路。常见误区是把 Agent 理解成一个万能黑盒，"
            "或者只会调用接口却不知道模型为什么会失败。建议你在这一阶段完成一个最小实验：给模型相同任务、不同提示，观察输出差异，"
            "并整理出哪些能力来自模型本身，哪些能力必须靠外部工具和流程补足。"
        )
    elif "prompt" in stage_key or "结构化输出" in stage_key:
        body = (
            "这一阶段重点是把“会问”变成“能稳定产出”。你需要系统学习系统提示词、角色设定、Few-shot 示例、约束条件以及 JSON / Schema 结构化输出。"
            "真正的 Agent 系统必须尽量减少自由发挥，让模型在可控边界内输出可解析结果。常见误区是提示词写得很长却没有明确格式要求，"
            "或者只在 happy path 下测试，忽略异常输入和解析失败。建议你为同一个任务设计 2 到 3 套提示模板，并比较它们在稳定性、可解析性和可扩展性上的差异。"
        )
    elif "rag" in stage_key or "检索" in stage_key:
        body = (
            "这一阶段要解决 Agent “不知道”或“记不住”外部知识的问题。你需要理解 Embedding、向量检索、Chunking、Retriever、Rerank 和召回质量评估的基本原理，"
            "明白 RAG 并不是把资料塞给模型这么简单，而是一个从数据切分、索引、召回到生成整体验证的系统工程。常见误区是只关注向量库选型，"
            "忽略了切分策略、召回质量和引用信息是否真的支撑答案。建议你做一个小型知识库实验，对比不同 chunk 大小和检索策略对回答质量的影响。"
        )
    elif "tool use" in stage_key or "工作流" in stage_key or "langgraph" in stage_key or "langchain" in stage_key:
        body = (
            "这一阶段进入 Agent 的核心工程实现：让模型通过工具与外部世界交互。你需要掌握 Function Calling 的基本机制、工具参数设计、错误处理、状态传递，"
            "以及 LangChain / LangGraph 这类框架如何把“思考 - 调用工具 - 观察结果 - 再决策”串成可执行流程。常见误区是把所有逻辑都塞进一个 prompt，"
            "或让模型直接生成不可控的工具参数。建议你实现一个简单的工具调用 Agent，例如查询天气、检索文档或调用自定义 API，并为工具失败场景补上回退策略。"
        )
    elif "memory" in stage_key or "planning" in stage_key or "multi agent" in stage_key:
        body = (
            "这一阶段关注 Agent 的持续性和复杂任务能力。你需要理解短期记忆、长期记忆、Planning、Reflection、多 Agent 分工协作等机制，"
            "并思考什么时候该让系统记住上下文，什么时候应该重新检索或重新规划。常见误区是把所有历史对话无脑拼接进上下文，导致成本高、噪声大、效果变差；"
            "或者过早引入多 Agent 架构，增加复杂度却没有明显收益。建议你先实现单 Agent 的 planning + memory，再对比引入反思或多 Agent 后的收益是否真实存在。"
        )
    elif "项目实战" in stage_key:
        body = (
            "这一阶段的重点是把前面的能力真正落到一个完整产品里。你需要完成需求拆解、架构设计、评测标准定义、日志监控、上线部署和持续优化。"
            "一个好的 Agent 项目不仅要能跑，还要能解释为什么这样设计、如何评估效果、如何发现失败案例。常见误区是只追求 demo 可用，忽略评测、观测性和安全边界。"
            "建议你选择一个明确场景，例如学习助手、知识库问答助手或自动任务执行助手，输出一份包含流程图、工具列表、评测方法和上线方案的项目总结。"
        )
    else:
        body = (
            f"本阶段重点是：{base_desc or f'围绕 {stage_title} 建立可落地的理解与实践能力。'}"
            "你需要先理解关键概念及其适用边界，再通过小任务验证理解是否正确。"
            "常见误区是只看资料不练习、或直接跳过基础导致后续卡住，建议每次学习后都做一次小结并输出可复用笔记。"
        )

    return f"阶段 {stage_order}「{stage_title}」将围绕你的目标“{query}”展开。{body}"


def _build_ai_agent_stage_tutorial(stage_title: str, stage_desc: str, stage_order: int) -> list[str]:
    stage_key = stage_title.lower()
    desc = stage_desc.strip() or f"学习 {stage_title} 的基础知识"

    if "llm" in stage_key or "agent 基础" in stage_key:
        return [
            f"步骤1（建立认知框架）：明确阶段 {stage_order} 的目标，先区分 LLM、工作流和真正 Agent 系统的边界，并写下你当前对“{stage_title}”的理解。",
            "步骤2（理解核心原理）：重点学习上下文窗口、提示词作用方式、Agent 的感知-决策-执行闭环，以及 ReAct 等基础思路。",
            f"步骤3（做对比实验）：围绕“{stage_title}”完成一个最小实验，对同一任务尝试不同提示与不同上下文输入，观察输出差异。",
            "步骤4（识别失败模式）：整理模型幻觉、上下文丢失、指令偏移等典型失败案例，并分析它们分别属于模型问题还是系统设计问题。",
            "步骤5（阶段验收）：用自己的话解释什么场景适合用 Agent、什么场景只需要普通工作流，并产出一页概念对照笔记。",
        ]
    if "prompt" in stage_key or "结构化输出" in stage_key:
        return [
            f"步骤1（定义输出目标）：明确“{stage_title}”阶段需要模型输出什么格式、满足哪些约束、失败时如何兜底。",
            "步骤2（设计提示模板）：分别编写 system prompt、task prompt 和 few-shot 示例，并为关键字段增加格式和边界要求。",
            "步骤3（实现结构化输出）：让模型返回 JSON 或 Schema 兼容格式，验证字段完整性、类型稳定性和解析成功率。",
            "步骤4（补齐异常处理）：专门测试空输入、歧义输入、超长输入和解析失败场景，并为提示模板补错误恢复策略。",
            "步骤5（阶段验收）：沉淀一套你自己的高复用提示模板，并说明它为什么比自然语言自由输出更稳定。",
        ]
    if "rag" in stage_key or "检索" in stage_key:
        return [
            f"步骤1（准备知识源）：围绕“{stage_title}”收集一批高质量资料，并区分哪些内容适合做检索知识库。",
            "步骤2（搭建索引流程）：完成文本切分、Embedding、入库和召回流程，记录不同 chunk 策略对召回效果的影响。",
            "步骤3（实现检索问答）：把 Retriever、Rerank 和生成模型串起来，观察检索结果是否真的支撑最终回答。",
            "步骤4（评估回答质量）：从相关性、覆盖率、引用可靠性和回答幻觉率几个维度评估 RAG 效果。",
            "步骤5（阶段验收）：输出一份小型知识库实践总结，说明你的 chunking、检索和 rerank 方案为什么这样选。",
        ]
    if "tool use" in stage_key or "工作流" in stage_key or "langgraph" in stage_key or "langchain" in stage_key:
        return [
            f"步骤1（定义工具边界）：列出阶段 {stage_order} 中 Agent 需要调用的工具、每个工具的输入输出参数以及失败时的回退规则。",
            "步骤2（接入工具调用）：实现 Function Calling 或框架级工具调用，把模型输出转换为受控的函数参数。",
            "步骤3（串联工作流）：基于 LangChain / LangGraph 或你自己的状态机，把思考、工具执行、结果观察与下一步决策连起来。",
            "步骤4（补齐可靠性）：处理工具超时、参数错误、空结果和重复调用问题，并记录关键日志。",
            "步骤5（阶段验收）：完成一个可重复演示的工具调用 Agent，并说明其状态流转和错误处理机制。",
        ]
    if "memory" in stage_key or "planning" in stage_key or "multi agent" in stage_key:
        return [
            f"步骤1（拆分记忆与规划需求）：明确“{stage_title}”阶段哪些信息要短期保留，哪些应转成长期记忆或外部知识。",
            "步骤2（实现规划链路）：让 Agent 在执行前先生成任务计划，再根据执行结果进行更新或重排。",
            "步骤3（加入反思机制）：为关键任务增加 Reflection 或自检步骤，对比加反思前后的任务完成率。",
            "步骤4（谨慎引入多 Agent）：仅在职责边界清晰时拆分多个 Agent，并比较其复杂度与收益是否匹配。",
            "步骤5（阶段验收）：输出一份关于 memory、planning 和 multi-agent 取舍的设计说明，说明你为什么采用当前方案。",
        ]
    if "项目实战" in stage_key:
        return [
            f"步骤1（定义项目场景）：围绕“{stage_title}”选择一个明确的 Agent 产品场景，写清目标用户、核心任务和成功标准。",
            "步骤2（完成系统设计）：画出系统流程，包括模型、检索、工具、记忆、日志和评测模块之间的关系。",
            "步骤3（实现 MVP）：先做一个最小可运行版本，确保主链路可用，再逐步补充评测、监控和权限控制。",
            "步骤4（做真实评测）：构造一批测试任务，评估正确率、稳定性、响应时间、成本和失败模式。",
            "步骤5（阶段验收）：输出项目总结，至少包含架构图、关键设计决策、评测结果和下一步优化方向。",
        ]

    return [
        f"步骤1（阶段准备）：明确阶段 {stage_order} 的学习目标，列出你当前与“{stage_title}”相关的已知与未知点。",
        f"步骤2（概念学习）：围绕“{stage_title}”系统学习核心原理，重点吸收：{desc}。",
        "步骤3（动手实践）：完成一个最小可运行练习，将抽象概念转化为可验证结果。",
        "步骤4（纠错优化）：对练习结果进行复盘，定位错误原因并做二次改进，形成自己的避坑清单。",
        "步骤5（阶段验收）：用自己的话讲清楚本阶段关键知识，并沉淀一份可复用的学习笔记/操作清单。",
    ]


def _build_stage_explanation(query: str, stage_title: str, stage_desc: str, stage_order: int) -> str:
    if _is_ai_agent_query(query):
        return _build_ai_agent_stage_explanation(query, stage_title, stage_desc, stage_order)

    base_desc = stage_desc.strip() or f"聚焦 {stage_title} 的核心知识与实操方法。"
    return (
        f"阶段 {stage_order}「{stage_title}」将围绕你的目标“{query}”展开。"
        f"本阶段重点是：{base_desc}"
        "你需要先理解关键概念及其适用边界，再通过小任务验证理解是否正确。"
        "常见误区是只看资料不练习、或直接跳过基础导致后续卡住，建议每次学习后都做一次小结并输出可复用笔记。"
    )


def _build_stage_tutorial(stage_title: str, stage_desc: str, stage_order: int) -> list[str]:
    if _is_ai_agent_query(stage_desc) or _is_ai_agent_query(stage_title):
        return _build_ai_agent_stage_tutorial(stage_title, stage_desc, stage_order)

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

        if is_relevant:
            merged_warnings = list(warnings)
            if not is_text_rich:
                merged_warnings.append("当前结果细节仍偏少，建议在提问中补充学习背景、时间投入和目标深度")
            return AiPathGenerateResponse(data=data, warnings=merged_warnings)

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
