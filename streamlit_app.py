"""
Streamlit 前端 — 学习路径生成器
调用本地 FastAPI /ai-path/generate 端点，展示结构化学习路径。
"""

import requests
import streamlit as st

API_URL = "http://localhost:8000/ai-path/generate"

RESOURCE_ICONS = {
    "youtube": "▶",
    "github": "⌥",
    "doc": "📄",
    "article": "📝",
    "course": "🎓",
}

RESOURCE_COLORS = {
    "youtube": "#c4302b",
    "github": "#333",
    "doc": "#1a73e8",
    "article": "#2e7d32",
    "course": "#6a1b9a",
}

st.set_page_config(
    page_title="学习路径生成器",
    page_icon="🗺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main .block-container { max-width: 900px; padding: 2rem 2rem 4rem; }

    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .page-subtitle {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 2rem;
    }

    .path-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        margin: 1.5rem 0 0.5rem;
    }
    .path-summary {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.7;
        padding: 1rem 1.25rem;
        background: #f8fafc;
        border-left: 3px solid #3b82f6;
        border-radius: 0 6px 6px 0;
        margin-bottom: 1.5rem;
    }

    .node-card {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        background: #fff;
    }
    .node-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.6rem;
    }
    .node-order {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #3b82f6;
        color: #fff;
        font-size: 0.8rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .node-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1e293b;
    }
    .node-desc {
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.65;
        margin-bottom: 0.75rem;
    }

    .tutorial-block {
        background: #f0f9ff;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
    }
    .tutorial-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #0369a1;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .tutorial-step {
        font-size: 0.875rem;
        color: #334155;
        line-height: 1.6;
        padding: 0.2rem 0;
    }

    .resource-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        text-decoration: none;
        margin: 0.2rem 0.2rem 0.2rem 0;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        color: #334155;
        transition: background 0.15s;
    }
    .resource-chip:hover { background: #e2e8f0; }

    .warning-box {
        background: #fffbeb;
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        color: #92400e;
        margin-top: 1rem;
    }

    div[data-testid="stButton"] > button {
        background: #3b82f6;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        width: 100%;
    }
    div[data-testid="stButton"] > button:hover { background: #2563eb; }

    div[data-testid="stTextArea"] textarea {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        font-size: 0.95rem;
        resize: vertical;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_resources(resources: list[dict]) -> str:
    chips = []
    for r in resources:
        rtype = r.get("type", "doc")
        icon = RESOURCE_ICONS.get(rtype, "🔗")
        title = r.get("title", "资源")[:40]
        url = r.get("url", "#")
        chips.append(f'<a class="resource-chip" href="{url}" target="_blank">{icon} {title}</a>')
    return "".join(chips)


def render_tutorial(steps: list[str]) -> str:
    if not steps:
        return ""
    items = "".join(f'<div class="tutorial-step">• {s}</div>' for s in steps)
    return f'<div class="tutorial-block"><div class="tutorial-title">学习步骤</div>{items}</div>'


def render_node(node: dict) -> str:
    order = node.get("order", "?")
    title = node.get("title", "")
    description = node.get("description", "") or node.get("explanation", "")
    tutorial = node.get("tutorial", [])
    resources = node.get("resources", [])

    tutorial_html = render_tutorial(tutorial)
    resources_html = render_resources(resources) if resources else ""

    return f"""
    <div class="node-card">
        <div class="node-header">
            <div class="node-order">{order}</div>
            <div class="node-title">{title}</div>
        </div>
        <div class="node-desc">{description}</div>
        {tutorial_html}
        {resources_html}
    </div>
    """


def call_api(query: str) -> dict:
    resp = requests.post(API_URL, json={"query": query}, timeout=120)
    resp.raise_for_status()
    return resp.json()


# ── UI ──────────────────────────────────────────────────────────────────────

st.markdown('<div class="page-title">🗺 学习路径生成器</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">输入你想学习的技术方向，AI 为你生成完整的分阶段学习路径，并附上 GitHub / YouTube 精选资源。</div>',
    unsafe_allow_html=True,
)

query = st.text_area(
    label="学习目标",
    placeholder="例如：我想学习 LLM 工程，从零开始到能独立搭建 AI Agent 系统",
    height=100,
    label_visibility="collapsed",
)

generate_clicked = st.button("生成学习路径")

if generate_clicked:
    if not query.strip():
        st.warning("请输入学习目标后再生成。")
    else:
        with st.spinner("正在生成学习路径，请稍候…"):
            try:
                result = call_api(query.strip())
            except requests.exceptions.ConnectionError:
                st.error("无法连接到后端服务，请确认 FastAPI 已在 http://localhost:8000 启动。")
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"API 返回错误：{e.response.status_code} — {e.response.text[:300]}")
                st.stop()
            except Exception as e:
                st.error(f"请求失败：{e}")
                st.stop()

        data = result.get("data", {})
        warnings = result.get("warnings", [])

        path_title = data.get("title", "学习路径")
        path_summary = data.get("summary", "")
        nodes = data.get("nodes", [])

        st.markdown(f'<div class="path-title">{path_title}</div>', unsafe_allow_html=True)

        if path_summary:
            st.markdown(f'<div class="path-summary">{path_summary}</div>', unsafe_allow_html=True)

        if nodes:
            for node in sorted(nodes, key=lambda n: n.get("order", 0)):
                st.markdown(render_node(node), unsafe_allow_html=True)
        else:
            st.info("未能生成学习节点，请尝试更具体的描述。")

        if warnings:
            warning_items = "".join(f"<div>• {w}</div>" for w in warnings)
            st.markdown(
                f'<div class="warning-box"><strong>提示</strong>{warning_items}</div>',
                unsafe_allow_html=True,
            )
