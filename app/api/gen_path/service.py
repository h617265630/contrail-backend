"""
Service layer for gen_path.
Handles business logic and DB persistence.
"""

from __future__ import annotations
from sqlalchemy.orm import Session


class GenPathService:
    @staticmethod
    def save_outline(db: Session, project_id: str, result: dict) -> None:
        """Save Step 1 outline + sections + summaries to DB."""
        from app.curd.gen_path_curd import GenPathProject, GenPathSection, GenPathSectionResource

        outline = result.get("outline") or {}
        summaries = result.get("summaries", [])

        # Update project outline
        GenPathProject.update_outline(db, project_id, outline)

        # Create sections
        sections_data = outline.get("sections", [])
        created_sections = GenPathSection.create_many(db, project_id, sections_data)

        # Assign summaries to sections (round-robin)
        # Each section gets suggested_resources from the outline
        for section in created_sections:
            section_title = section.get("title", "")
            # Find matching outline section by title
            matching = [s for s in sections_data if s.get("title") == section_title]
            if matching:
                suggested = matching[0].get("suggested_resources", [])
                for res in suggested:
                    GenPathSectionResource.add(
                        db, section["id"], res, added_by="ai"
                    )

    @staticmethod
    def save_tutorial(
        db: Session,
        section_id: str,
        tutorial_md: str,
        key_points: list[str],
    ) -> None:
        """Save Step 2 tutorial to DB."""
        from app.curd.gen_path_curd import GenPathSection
        GenPathSection.update_tutorial(db, section_id, tutorial_md)

    @staticmethod
    def save_resources(
        db: Session,
        section_id: str,
        resources: list[dict],
    ) -> None:
        """Save Step 3 new resources to DB."""
        from app.curd.gen_path_curd import GenPathSectionResource
        for res in resources:
            GenPathSectionResource.add(db, section_id, res, added_by="ai")
