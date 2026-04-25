# AIFetchPathly — Project Structure

## Overview

A research-driven learning path generator. Given a topic and level, it searches the web for real tutorials, summarizes them, then builds a personalized learning path.

**Tech stack:** Streamlit + LangGraph (LangChain) + LLM (OpenAI/MiniMax) + Web Search (Tavily/Serper)

---

## Directory Structure

```
aifetchpathly/
├── app.py                  # Streamlit UI — entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .env                    # API keys (not committed)
│
├── models/
│   ├── __init__.py
│   └── schemas.py          # All Pydantic models + TypedDict
│
├── pipeline/               # LangGraph pipeline — 6 sequential stages
│   ├── __init__.py         # build_graph() wires all stages together
│   ├── queries.py          # Stage 1: generate_queries
│   ├── search.py           # Stage 2: search_web
│   ├── fetch.py           # Stage 3: fetch_pages
│   ├── summarize.py       # Stage 4: summarize_resources
│   ├── organize.py        # Stage 5: organize_path
│   └── report.py          # Stage 6: generate_report
│
├── tools/
│   ├── __init__.py
│   ├── search.py          # Web search abstraction (Tavily/Serper)
│   └── fetch.py          # HTTP page fetching + content extraction
│
└── utils/
    ├── __init__.py
    └── llm.py             # LLM factory (OpenAI / MiniMax)
```

---

## Data Flow & 6 Stages

The pipeline is a **linear LangGraph graph** (no branching). Each stage receives `PipelineState`, adds/modifies fields, and passes to the next.

```
topic + level
    │
    ▼
┌─────────────────────┐
│ Stage 1: queries.py  │
│ generate_queries     │  LLM → 6 diverse SearchQuery objects
│ (queries[])          │  (query + purpose per query)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Stage 2: search.py  │
│ search_web          │  All queries run concurrently → deduplicated
│ (search_results[])  │  SearchResult[] (url, title, snippet)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Stage 3: fetch.py   │
│ fetch_pages         │  Concurrent fetch (semaphore=8) per URL
│ (fetched_pages[])   │  FetchedPage (url, title, content or snippet fallback)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Stage 4: summarize.py│
│ summarize_resources │  Concurrent LLM summarization (semaphore=4)
│ (summaries[])       │  → ResourceSummary per page (summary, key_points,
│                      │    difficulty, resource_type, learning_stage, time)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Stage 5: organize.py│
│ organize_path       │  LLM groups summaries into LearningPath
│ (learning_path)     │  with ordered PathSections (3-5 sections,
│                      │    foundation → advanced)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Stage 6: report.py  │
│ generate_report     │  LLM renders polished Markdown report
│ (final_report)      │  (intro, section tables, next steps)
└─────────────────────┘
           ▼
      final_report    ← displayed in Streamlit UI
```

### Stage Details

| Stage | File | Function | Key Input → Output |
|-------|------|----------|--------------------|
| **1** | `queries.py` | `generate_queries` | `topic + level` → `queries[]` (6 SearchQuery) |
| **2** | `search.py` | `search_web` | `queries[]` → `search_results[]` (deduplicated SearchResult) |
| **3** | `fetch.py` | `fetch_pages` | `search_results[]` → `fetched_pages[]` (FetchedPage w/ content) |
| **4** | `summarize.py` | `summarize_resources` | `fetched_pages[]` → `summaries[]` (ResourceSummary per page) |
| **5** | `organize.py` | `organize_path` | `summaries[]` → `learning_path` (LearningPath with PathSections) |
| **6** | `report.py` | `generate_report` | `learning_path` → `final_report` (Markdown string) |

### Schema Models (PipelineState flow)

```
PipelineState (TypedDict):
  topic, level
    ↓ after Stage 1
  queries: List[SearchQuery]       {query: str, purpose: str}
    ↓ after Stage 2
  search_results: List[SearchResult] {url, title, snippet, query}
    ↓ after Stage 3
  fetched_pages: List[FetchedPage]   {url, title, content, fetch_ok}
    ↓ after Stage 4
  summaries: List[ResourceSummary]   {url, title, summary, key_points,
                                      difficulty, resource_type,
                                      learning_stage, estimated_minutes}
    ↓ after Stage 5
  learning_path: LearningPath        {topic, level, overview,
                                      total_duration_hours, sections[]}
    ↓ after Stage 6
  final_report: str (Markdown)
  current_stage: str (control field)
  error: Optional[str]
```

---

## UI (app.py)

Streamlit page with sidebar showing the 6 stages. User inputs topic + level, clicks run, and the pipeline streams results back via `astream_events`. Displays metrics (queries, results, pages, summaries) and renders the final Markdown report.

---

## Key Design Decisions

- **Concurrency:** Stage 2 (search), 3 (fetch), 4 (summarize) all run queries/pages concurrently with semaphores to bound parallelism.
- **Fallback:** Each LLM call has a fallback that produces a minimal result so the pipeline never hard-fails.
- **Deduplication:** Stage 2 deduplicates by URL after gathering all query results.
- **LLM-agnostic:** `utils/llm.py` factory supports OpenAI or MiniMax via env var.
- **Search-agnostic:** `tools/search.py` abstraction supports Tavily or Serper via env var.
