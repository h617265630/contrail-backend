"""
Pydantic / TypedDict schemas for aifetchpathly pipeline.

Flow:
  topic + level
    → SearchQuery[]
    → SearchResult[]
    → FetchedPage[]
    → ResourceSummary[]
    → LearningPath
    → final_report (Markdown str)
"""

from __future__ import annotations
from typing import List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


# ── Intermediate search / fetch models ────────────────────────────────────────

class SearchQuery(BaseModel):
    query: str
    purpose: str  # e.g. "overview", "beginner tutorial", "hands-on project"


class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    query: str  # which query produced this result


class FetchedPage(BaseModel):
    url: str
    title: str
    content: str          # extracted plain text (truncated to ~3000 chars)
    fetch_ok: bool = True  # False = fell back to snippet
    image: str | None = None  # og:image or twitter:image URL


# ── Summary model (one per resource) ──────────────────────────────────────────

class ResourceSummary(BaseModel):
    url: str
    title: str
    summary: str                  # 2–4 sentence summary
    key_points: List[str]         # 3–5 bullet points
    difficulty: str               # "beginner" | "intermediate" | "advanced"
    resource_type: str            # "article" | "video" | "course" | "docs" | "repo"
    learning_stage: str           # "foundation" | "core" | "practice" | "advanced"
    estimated_minutes: int = 15   # reading / watch time
    image: str | None = None      # og:image or twitter:image URL


# ── Learning path structure ────────────────────────────────────────────────────

class PathSection(BaseModel):
    title: str
    description: str
    learning_goals: List[str]
    resources: List[ResourceSummary]
    order: int


class LearningPath(BaseModel):
    topic: str
    level: str
    overview: str
    total_duration_hours: float
    sections: List[PathSection]


# ── LangGraph pipeline state ───────────────────────────────────────────────────

class PipelineState(TypedDict, total=False):
    # Inputs
    topic: str
    level: str

    # Learning path preferences
    learning_depth: str     # "quick" | "standard" | "deep"
    content_type: str      # "video" | "article" | "mixed"
    resource_count: str    # "compact" (5) | "standard" (10) | "rich" (15)
    practical_ratio: str    # "theory_first" | "balanced" | "practice_first"

    # Stage outputs
    queries: List[SearchQuery]
    search_results: List[SearchResult]
    fetched_pages: List[FetchedPage]
    summaries: List[ResourceSummary]
    learning_path: Optional[LearningPath]
    final_report: Optional[str]

    # Control
    current_stage: str
    error: Optional[str]

    # Shuffle / deduplication
    exclude_urls: List[str]


# ── New 4-Step Pipeline Models ─────────────────────────────────────────────────

class SubNode(BaseModel):
    """A detailed learning sub-node within a section."""
    title: str
    description: str
    key_points: List[str]
    practical_exercise: str = ""
    search_keywords: List[str] = []
    # Step 2.5: Detailed content (generated on demand)
    detailed_content: str = ""  # Markdown content with detailed explanation
    code_examples: List[str] = []  # Code snippets
    related_resources: List[str] = []  # URLs of related resources


class OutlineSection(BaseModel):
    """A section in the learning outline."""
    title: str
    description: str
    learning_goals: List[str] = []  # Simple string goals (Step 1 output)
    sub_nodes: List[SubNode] = []   # Detailed sub-nodes (Step 2 output)
    search_queries: List[str] = []
    suggested_resources: List[str] = []
    resources: List[ResourceSummary] = []  # Supplementary resources (Step 3)
    estimated_minutes: int = 60
    order: int = 0


class LearningOutline(BaseModel):
    """The complete learning outline (Step 1 output)."""
    topic: str
    level: str
    overview: str
    total_duration_hours: float
    sections: List[OutlineSection]


class SectionTutorial(BaseModel):
    """Tutorial content for a section."""
    section_title: str
    tutorial_md: str = ""  # Markdown tutorial content
    key_points: List[str] = []
    source_urls: List[str] = []


class GitHubProject(BaseModel):
    """A GitHub project recommendation."""
    name: str
    url: str
    description: str
    stars: int = 0
    stars_display: str = ""
    language: str = ""
    thumbnail: str | None = None


class GenPathState(TypedDict, total=False):
    """State for the new 4-step pipeline."""
    # Inputs
    topic: str
    level: str
    learning_depth: str      # "quick" | "standard" | "deep"
    content_type: str        # "video" | "article" | "mixed"
    practical_ratio: str     # "theory_first" | "balanced" | "practice_first"
    resource_count: str       # "compact" | "standard" | "rich"
    exclude_urls: List[str]  # For deduplication

    # Step 1 output
    search_results: List[SearchResult]
    outline: Optional[LearningOutline]
    discovered_urls: List[str]

    # Step 2 output (outline with expanded sections)
    expanded_outline: Optional[LearningOutline]

    # Step 3 output
    sections_with_resources: List[OutlineSection]

    # Step 4 output
    final_summary: Optional[str]
    github_projects: List[GitHubProject]

    # Control
    current_step: int
    error: Optional[str]
