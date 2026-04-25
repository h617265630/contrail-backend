# AI Path Pipeline Memory

## 目录结构

```
ai_path/
├── models/
│   └── schemas.py        # 所有阶段共享的 PipelineState + 数据模型
├── pipeline/
│   ├── queries.py        # 阶段1：LLM 生成搜索词
│   ├── search.py         # 阶段2：并发搜索 + URL 去重
│   ├── fetch.py          # 阶段3：抓取页面内容
│   ├── summarize.py      # 阶段4：LLM 摘要每个资源
│   ├── organize.py       # 阶段5：组织成学习路径结构
│   └── report.py         # 阶段6：生成 Markdown 报告
├── tools/
│   └── search.py         # Tavily / Serper 搜索工具封装
├── ai_resource/
│   ├── github.py         # GitHub API 搜索
│   └── youtube.py        # YouTube 搜索
└── utils/
    └── llm.py            # LLM 客户端（OpenAI / MiniMax）
```

## 流水线顺序

```
generate_queries → search_web → fetch_pages → summarize_resources → organize → report
```

LangGraph 构建入口：`ai_path/pipeline/__init__.py` 的 `build_graph()`

## PipelineState（schemas.py）

TypedDict，所有阶段读写同一个 state 对象：

```python
class PipelineState(TypedDict, total=False):
    # 输入
    topic: str
    level: str
    learning_depth: str    # "quick" | "standard" | "deep"
    content_type: str      # "video" | "article" | "mixed"
    resource_count: str    # "compact" | "standard" | "rich"
    practical_ratio: str   # "theory_first" | "balanced" | "practice_first"

    # 阶段输出
    queries: List[SearchQuery]
    search_results: List[SearchResult]
    fetched_pages: List[FetchedPage]
    summaries: List[ResourceSummary]
    learning_path: Optional[LearningPath]
    final_report: Optional[str]

    # 控制
    current_stage: str
    error: Optional[str]

    # Shuffle 去重（[2026-04-14] 新增）
    exclude_urls: List[str]
```

## 关键参数映射

### resource_count → 查询数量
| resource_count | 查询数 | 目标资源数 |
|---|---|---|
| compact | 4 | ~5 |
| standard | 6 | ~10 |
| rich | 8 | ~15 |

### content_type → prompt 指导语
- `video` → 优先 YouTube、视频课程平台
- `article` → 优先文章、博客、文字教程
- `mixed` → 视频和文章各半

## 搜索工具（tools/search.py）

```python
web_search(query, max_results=5) -> List[SearchResult]
```
- 环境变量 `SEARCH_PROVIDER=tavily`（默认）或 `serper`
- Tavily：`TAVILY_API_KEY`
- Serper：`SERPER_API_KEY`

## search_web 阶段（pipeline/search.py）

- 所有 query 并发执行（`asyncio.gather`）
- 去重逻辑：先把 `state["exclude_urls"]` 加入 `seen` set，再遍历结果
- **重要**：`exclude_urls` 必须在 `initial` state 中传入，否则 Shuffle 无效

## ai_resource 模块

### GitHub 搜索（ai_resource/github.py）
```python
search_github(topic, limit=6) -> List[dict]
# 返回字段：url, title, description, why_recommended, thumbnail
```

#### GitHub 图片获取逻辑（镜像 ResourceCURD.extract_from_url）
- `_fetch_og_image(url)` — HTTP GET + regex 解析 og:image / twitter:image meta 标签
- `_get_github_thumbnail(html_url, full_name)` — 优先级：
  1. 从 repo 页面 fetch og:image
  2. CDN fallback：`opengraph.githubassets.com/1/{full_name}`
  3. GitHub logo
- `_search_github_api` 已改为调用 `_get_github_thumbnail(html_url, full_name)`

### Tavily 搜索（tools/search.py）
- `_search_tavily` 过滤掉所有 `github.com` URL（GitHub 由 GitHub API 单独处理）
- 请求 `max_results + 3` 条以补偿被过滤的条目

## 环境变量（ai_path/.env）

```
OPENAI_API_KEY=
TAVILY_API_KEY=          # 或 SERPER_API_KEY
SEARCH_PROVIDER=tavily   # 或 serper
LLM_PROVIDER=openai      # 或 minimax
```

## ResourceSummary 结构

```python
class ResourceSummary(BaseModel):
    url: str
    title: str
    summary: str                  # 2-4 句话
    key_points: List[str]         # 3-5 条要点
    difficulty: str               # "beginner" | "intermediate" | "advanced"
    resource_type: str            # "article" | "video" | "course" | "docs" | "repo"
    learning_stage: str           # "foundation" | "core" | "practice" | "advanced"
    estimated_minutes: int = 15
    image: str | None = None
```

## 已知修复

### [2026-04-14] Tavily 搜索结果重复 / Shuffle 无效
**根因**：`exclude_urls` 只在 router 层做了后置过滤，未传入 `PipelineState`，Tavily 搜索阶段不感知

**修复**：
1. `schemas.py` — `PipelineState` 新增 `exclude_urls: List[str]`
2. `pipeline/search.py` — `search_web` 从 state 读取并预置到 `seen` set
3. `backend/app/api/ai_path/service.py` — `initial` state 加入 `exclude_urls`；缓存层跳过被排除 URL
