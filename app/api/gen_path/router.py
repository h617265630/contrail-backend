"""
FastAPI router for gen_path API.
"""

from __future__ import annotations
import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel

from app.core.deps import get_db_dep
from app.api.gen_path.service import GenPathService
from app.curd.gen_path_curd import GenPathCURD

router = APIRouter(prefix="/gen-path", tags=["gen-path"])


# ── Request / Response models ─────────────────────────────────────────────────

class CreateProjectRequest(BaseModel):
    topic: str
    level: str = "intermediate"
    learning_depth: str = "standard"
    content_type: str = "mixed"
    practical_ratio: str = "balanced"


class OutlineResponse(BaseModel):
    project_id: str
    outline: dict
    summaries: list[dict]
    all_urls: list[str]


class TutorialRequest(BaseModel):
    project_id: str
    section_id: str
    resource_urls: list[str]


class TutorialResponse(BaseModel):
    section_id: str
    tutorial: str
    key_points: list[str]
    source_urls: list[str]


class ResourcesRequest(BaseModel):
    project_id: str
    section_id: str
    resource_type_filter: str = "all"
    max_results: int = 6


class ResourcesResponse(BaseModel):
    section_id: str
    resources: list[dict]


class SummaryResponse(BaseModel):
    project_id: str
    summary: str
    github_projects: list[dict]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/outline", response_model=OutlineResponse)
async def create_outline(
    payload: CreateProjectRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db_dep),
):
    """
    Step 1: Generate learning path outline.

    1. Generate diverse search queries based on topic + level
    2. Concurrent web search
    3. Fetch pages
    4. Summarize resources
    5. Organize into outline structure
    6. Persist to database
    """
    # Create project in DB first
    project = GenPathCURD.create(
        db,
        topic=payload.topic,
        level=payload.level,
        learning_depth=payload.learning_depth,
        content_type=payload.content_type,
        practical_ratio=payload.practical_ratio,
    )

    # Run step 1 pipeline in thread pool (it's async but not FastAPI-aware)
    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            from gen_path.pipeline.step1_outline import run_step1
            return loop.run_until_complete(
                run_step1(
                    topic=payload.topic,
                    level=payload.level,
                    learning_depth=payload.learning_depth,
                    content_type=payload.content_type,
                    practical_ratio=payload.practical_ratio,
                )
            )
        finally:
            loop.close()

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_run)
        result = future.result()

    # Save outline and sections to DB
    GenPathService.save_outline(db, project.id, result)

    return OutlineResponse(
        project_id=str(project.id),
        outline=result["outline"],
        summaries=result["summaries"],
        all_urls=result["all_urls"],
    )


@router.get("/projects/{project_id}")
async def get_project(project_id: str, db=Depends(get_db_dep)):
    """Get project by ID with all sections and resources."""
    project = GenPathCURD.get_by_id(db, project_id)
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    sections = GenPathCURD.get_sections(db, project_id)
    return {
        "project": project,
        "sections": sections,
    }


@router.post("/tutorial", response_model=TutorialResponse)
async def generate_tutorial(
    payload: TutorialRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db_dep),
):
    """
    Step 2: Generate detailed tutorial for a specific section.

    1. Fetch content for each resource URL (cache-first)
    2. LLM generates detailed Markdown tutorial
    3. Save tutorial to DB
    """
    section = GenPathCURD.get_section_by_id(db, payload.section_id)
    if not section:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Section not found")

    project = GenPathCURD.get_by_id(db, payload.project_id)
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")

    # Run step 2 in thread pool
    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            from gen_path.pipeline.step2_tutorial import generate_section_tutorial
            return loop.run_until_complete(
                generate_section_tutorial(
                    section_title=section.title,
                    section_goal=section.description or "",
                    learning_goals=section.learning_goals,
                    resource_urls=payload.resource_urls,
                    topic=project.topic,
                    level=project.level,
                )
            )
        finally:
            loop.close()

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_run)
        result = future.result()

    # Save tutorial to DB
    GenPathCURD.update_section_tutorial(
        db, payload.section_id, result["tutorial"]
    )

    # Update project status
    GenPathCURD.update_status(db, payload.project_id, "step2")

    return TutorialResponse(
        section_id=payload.section_id,
        tutorial=result["tutorial"],
        key_points=result["key_points"],
        source_urls=result["source_urls"],
    )


@router.post("/resources", response_model=ResourcesResponse)
async def add_resources(
    payload: ResourcesRequest,
    db=Depends(get_db_dep),
):
    """
    Step 3: Add supplementary resources to a section.

    1. Search for new resources (avoiding existing_urls)
    2. Fetch + summarize
    3. Filter by type (video/article/docs)
    4. Save to DB
    """
    section = GenPathCURD.get_section_by_id(db, payload.section_id)
    if not section:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Section not found")

    # Get existing resources
    existing = GenPathCURD.get_section_resources(db, payload.section_id)
    existing_urls = [r.resource_json.get("url", "") for r in existing]

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            from gen_path.pipeline.step3_resources import search_supplementary_resources
            return loop.run_until_complete(
                search_supplementary_resources(
                    section_title=section.title,
                    section_goal=section.description or "",
                    existing_urls=existing_urls,
                    resource_type_filter=payload.resource_type_filter,
                    max_results=payload.max_results,
                )
            )
        finally:
            loop.close()

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_run)
        new_resources = future.result()

    # Save new resources to DB
    for res in new_resources:
        GenPathCURD.add_section_resource(
            db, payload.section_id, res, added_by="ai"
        )

    GenPathCURD.update_status(db, payload.project_id, "step3")

    return ResourcesResponse(
        section_id=payload.section_id,
        resources=new_resources,
    )


@router.post("/summary", response_model=SummaryResponse)
async def generate_summary(
    project_id: str,
    db=Depends(get_db_dep),
):
    """
    Step 4: Generate final summary + GitHub projects.

    1. Collect all sections' tutorials
    2. LLM generate overall summary
    3. Search GitHub for relevant projects
    4. Save to DB
    """
    project = GenPathCURD.get_by_id(db, project_id)
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")

    sections = GenPathCURD.get_sections(db, project_id)

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            from gen_path.pipeline.step4_summary import generate_final_summary
            sections_data = [
                {
                    "title": s.title,
                    "description": s.description or "",
                    "tutorial_md": s.tutorial_md or "",
                    "resources": [],
                }
                for s in sections
            ]
            return loop.run_until_complete(
                generate_final_summary(
                    topic=project.topic,
                    sections_data=sections_data,
                    level=project.level,
                )
            )
        finally:
            loop.close()

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_run)
        result = future.result()

    # Save to DB
    GenPathCURD.update_final_summary(
        db, project_id, result["summary"], result["github_projects"]
    )
    GenPathCURD.update_status(db, project_id, "done")

    return SummaryResponse(
        project_id=project_id,
        summary=result["summary"],
        github_projects=result["github_projects"],
    )


@router.get("/projects")
async def list_projects(
    limit: int = 20,
    offset: int = 0,
    db=Depends(get_db_dep),
):
    """List user's projects."""
    projects = GenPathCURD.list_by_user(db, limit=limit, offset=offset)
    total = GenPathCURD.count_by_user(db)
    return {"projects": projects, "total": total}


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, db=Depends(get_db_dep)):
    """Delete a project."""
    GenPathCURD.delete(db, project_id)
    return {"success": True}
