# AI Path

> AI 驱动的学习路径生成服务 — 基于 LangGraph + LLM

## 概述

AI Path 是一个独立的学习路径生成服务，使用 LangGraph 构建 AI 工作流，通过网络搜索真实的学习资源，并生成个性化学习路径。

## 特性

- **智能搜索** — 搜索 GitHub、YouTube 和网络的真实学习资源
- **LLM 驱动** — 使用大语言模型理解学习意图和生成路径
- **可配置参数** — 支持学习深度、内容类型、理论/实践比例等
- **订阅层级** — Free / Basic / Pro / Ultra 四级限制
- **独立部署** — 可作为独立 Streamlit 应用运行

## 技术栈

- **LangGraph** — AI 流程编排
- **OpenAI** — GPT-4o 模型
- **MiniMax** — 备选 LLM 供应商
- **Tavily / Serper** — 搜索引擎
- **Streamlit** — 用户界面

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入 API 密钥
```

### 3. 启动服务
```bash
streamlit run app.py
```

访问 http://localhost:8501

## 环境变量

```bash
# LLM 配置
OPENAI_API_KEY=sk-...           # OpenAI API 密钥
LLM_PROVIDER=openai             # openai 或 minimax

# 搜索配置
SEARCH_PROVIDER=tavily           # tavily 或 serper
TAVILY_API_KEY=tvly-...         # Tavily API 密钥
SERPER_API_KEY=...               # Serper API 密钥 (可选)

# GitHub Token (可选)
GITHUB_TOKEN=ghp_...

# YouTube API Key (可选)
YOUTUBE_API_KEY=...
```

## 目录结构

```
ai_path/
├── ai_resource/          # 资源搜索工具
│   ├── __init__.py
│   ├── github.py        # GitHub 搜索
│   ├── youtube.py        # YouTube 搜索
│   └── utils.py         # 工具函数
├── models/              # 数据模型
│   ├── schemas.py       # Pydantic 模型
│   └── __init__.py
├── pipeline/            # LangGraph 流程
│   ├── __init__.py      # build_graph 入口
│   ├── queries.py       # 查询生成
│   ├── search.py        # 资源搜索
│   ├── fetch.py         # 内容抓取
│   ├── summarize.py     # 内容摘要
│   └── ...
├── tools/               # AI 工具
│   └── search.py        # 搜索封装
├── utils/               # 工具函数
│   ├── subscription.py  # 订阅管理
│   └── ...
├── app.py              # Streamlit 应用入口
├── requirements.txt
├── .env.example
└── .gitignore
```

## 工作流程

```
用户输入学习主题
       │
       ▼
┌──────────────────┐
│ 1. generate_queries │
│ 生成多个搜索查询    │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 2. search_web      │
│ 多源资源搜索       │
│ - Tavily/Serper    │
│ - GitHub           │
│ - YouTube          │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 3. fetch_pages     │
│ 抓取页面内容       │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 4. summarize      │
│ AI 摘要生成       │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 5. plan_path      │
│ 生成学习路径       │
└──────────────────┘
       │
       ▼
   学习路径结果
```

## API 调用

### Python 直接调用

```python
from ai_path.pipeline import build_graph
from ai_path.models.schemas import PipelineState

# 构建图
graph = build_graph()

# 执行
state: PipelineState = {
    "topic": "学习 React",
    "level": "beginner",
    "learning_depth": "standard",
    "content_type": "mixed",
    "resource_count": "standard",
    "practical_ratio": "balanced",
}

result = graph.invoke(state)
learning_path = result["learning_path"]
```

### 作为 FastAPI 服务

AI Path 已集成到 backend 的 `/ai-path` 端点：

```python
POST /ai-path/generate
{
    "query": "学习 React",
    "level": "beginner",
    "learning_depth": "standard",
    "content_type": "mixed",
    "resource_count": "standard",
    "practical_ratio": "balanced"
}
```

## 订阅层级

| 层级 | 路径数/天 | 资源数/路径 | 功能 |
|------|-----------|-------------|------|
| Free | 3 | 5 | 基础功能 |
| Basic | 10 | 10 | 全部资源 |
| Pro | 30 | 15 | 深度学习 |
| Ultra | 无限 | 无限 | 全部功能 |

## 模型配置

### Intent Detection (意图识别)
```bash
MODEL_INTENT=gpt-4o-mini
```

### Planner (路径规划)
```bash
MODEL_PLANNER=gpt-4o
```

### Generator (内容生成)
```bash
MODEL_GENERATOR=gpt-4.1
```

## 搜索工具

### GitHub 搜索
```python
from ai_path.ai_resource import search_github

results = search_github("React framework", limit=5)
# 返回: [{title, url, description, source_score, thumbnail, ...}]
```

### YouTube 搜索
```python
from ai_path.ai_resource import search_youtube

results = search_youtube("React tutorial", limit=5)
# 返回: [{title, url, description, source_score, thumbnail, ...}]
```

## Streamlit 界面

运行 `streamlit run app.py` 后：

1. **输入学习主题** — 描述想学习的内容
2. **选择参数** — 学习深度、内容类型等
3. **生成路径** — 点击生成 AI 学习路径
4. **查看结果** — 分阶段展示学习路径和资源

## 开发

### 添加新的搜索源
在 `ai_resource/` 添加新的搜索模块：

```python
# ai_resource/new_source.py
def search_new_source(query: str, limit: int = 5) -> list[dict]:
    # 实现搜索逻辑
    pass
```

### 添加新的 Pipeline 阶段
在 `pipeline/` 添加新的处理函数：

```python
# pipeline/new_stage.py
def new_stage(state: PipelineState) -> PipelineState:
    # 处理逻辑
    return state
```

然后在 `build_graph()` 中注册：

```python
graph.add_node("new_stage", new_stage)
```

## License

MIT
