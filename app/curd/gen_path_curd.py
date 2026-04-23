"""
CRUD operations for gen_path tables.
"""

from __future__ import annotations
import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class GenPathProject:
    @staticmethod
    def create(
        db: Session,
        topic: str,
        level: str = "intermediate",
        learning_depth: str = "standard",
        content_type: str = "mixed",
        practical_ratio: str = "balanced",
        user_id: str | None = None,
    ) -> dict:
        """Create a new gen_path project."""
        project_id = db.execute(
            text("SELECT gen_random_uuid()::text"),
        ).scalar()
        db.execute(
            text("""
                INSERT INTO gen_path_projects
                    (id, user_id, topic, level, learning_depth, content_type, practical_ratio, status)
                VALUES
                    (:id, :user_id, :topic, :level, :learning_depth, :content_type, :practical_ratio, 'step1')
            """),
            {
                "id": project_id,
                "user_id": user_id,
                "topic": topic,
                "level": level,
                "learning_depth": learning_depth,
                "content_type": content_type,
                "practical_ratio": practical_ratio,
            },
        )
        db.commit()
        return {"id": project_id, "topic": topic}

    @staticmethod
    def get_by_id(db: Session, project_id: str) -> Optional[dict]:
        row = db.execute(
            text("SELECT * FROM gen_path_projects WHERE id = :id"),
            {"id": project_id},
        ).fetchone()
        if not row:
            return None
        return dict(row._mapping)

    @staticmethod
    def update_outline(
        db: Session,
        project_id: str,
        outline_json: dict,
    ) -> None:
        db.execute(
            text("""
                UPDATE gen_path_projects
                SET outline_json = :outline_json, updated_at = NOW()
                WHERE id = :id
            """),
            {"outline_json": json.dumps(outline_json), "id": project_id},
        )
        db.commit()

    @staticmethod
    def update_final_summary(
        db: Session,
        project_id: str,
        summary: str,
        github_projects: list[dict],
    ) -> None:
        db.execute(
            text("""
                UPDATE gen_path_projects
                SET final_summary = :summary,
                    github_projects_json = :github,
                    updated_at = NOW()
                WHERE id = :id
            """),
            {
                "summary": summary,
                "github": json.dumps(github_projects),
                "id": project_id,
            },
        )
        db.commit()

    @staticmethod
    def update_status(
        db: Session,
        project_id: str,
        status: str,
    ) -> None:
        db.execute(
            text("""
                UPDATE gen_path_projects
                SET status = :status, updated_at = NOW()
                WHERE id = :id
            """),
            {"status": status, "id": project_id},
        )
        db.commit()

    @staticmethod
    def list_by_user(
        db: Session,
        user_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[dict]:
        rows = db.execute(
            text("""
                SELECT * FROM gen_path_projects
                WHERE (:user_id IS NULL OR user_id = :user_id)
                ORDER BY updated_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"user_id": user_id, "limit": limit, "offset": offset},
        ).fetchall()
        return [dict(r._mapping) for r in rows]

    @staticmethod
    def count_by_user(db: Session, user_id: str | None = None) -> int:
        row = db.execute(
            text("""
                SELECT COUNT(*) FROM gen_path_projects
                WHERE (:user_id IS NULL OR user_id = :user_id)
            """),
            {"user_id": user_id},
        ).scalar()
        return row or 0

    @staticmethod
    def delete(db: Session, project_id: str) -> None:
        db.execute(
            text("DELETE FROM gen_path_projects WHERE id = :id"),
            {"id": project_id},
        )
        db.commit()


class GenPathSection:
    @staticmethod
    def create_many(
        db: Session,
        project_id: str,
        sections: list[dict],
    ) -> List[dict]:
        """Create multiple sections for a project."""
        created = []
        for idx, section in enumerate(sections):
            section_id = db.execute(
                text("SELECT gen_random_uuid()::text"),
            ).scalar()
            db.execute(
                text("""
                    INSERT INTO gen_path_sections
                        (id, project_id, title, description, learning_goals_json,
                         search_queries_json, order_index)
                    VALUES
                        (:id, :project_id, :title, :description,
                         :learning_goals, :search_queries, :order_index)
                """),
                {
                    "id": section_id,
                    "project_id": project_id,
                    "title": section.get("title", ""),
                    "description": section.get("description", ""),
                    "learning_goals": json.dumps(section.get("learning_goals", [])),
                    "search_queries": json.dumps(section.get("search_queries", [])),
                    "order_index": idx,
                },
            )
            created.append({"id": section_id, **section})
        db.commit()
        return created

    @staticmethod
    def get_by_project(db: Session, project_id: str) -> List[dict]:
        rows = db.execute(
            text("""
                SELECT * FROM gen_path_sections
                WHERE project_id = :project_id
                ORDER BY order_index
            """),
            {"project_id": project_id},
        ).fetchall()
        return [dict(r._mapping) for r in rows]

    @staticmethod
    def get_by_id(db: Session, section_id: str) -> Optional[dict]:
        row = db.execute(
            text("SELECT * FROM gen_path_sections WHERE id = :id"),
            {"id": section_id},
        ).fetchone()
        if not row:
            return None
        return dict(row._mapping)

    @staticmethod
    def update_tutorial(
        db: Session,
        section_id: str,
        tutorial_md: str,
    ) -> None:
        db.execute(
            text("""
                UPDATE gen_path_sections
                SET tutorial_md = :tutorial_md
                WHERE id = :id
            """),
            {"tutorial_md": tutorial_md, "id": section_id},
        )
        db.commit()


class GenPathSectionResource:
    @staticmethod
    def add(
        db: Session,
        section_id: str,
        resource_json: dict,
        added_by: str = "ai",
    ) -> str:
        resource_id = db.execute(
            text("SELECT gen_random_uuid()::text"),
        ).scalar()
        db.execute(
            text("""
                INSERT INTO gen_path_section_resources
                    (id, section_id, resource_json, added_by)
                VALUES
                    (:id, :section_id, :resource_json, :added_by)
            """),
            {
                "id": resource_id,
                "section_id": section_id,
                "resource_json": json.dumps(resource_json),
                "added_by": added_by,
            },
        )
        db.commit()
        return resource_id

    @staticmethod
    def get_by_section(db: Session, section_id: str) -> List[dict]:
        rows = db.execute(
            text("""
                SELECT * FROM gen_path_section_resources
                WHERE section_id = :section_id
                ORDER BY created_at
            """),
            {"section_id": section_id},
        ).fetchall()
        return [dict(r._mapping) for r in rows]


# ── Convenience aliases ────────────────────────────────────────────────────────

GenPathCURD = type("GenPathCURD", (), {
    "create": GenPathProject.create,
    "get_by_id": GenPathProject.get_by_id,
    "update_outline": GenPathProject.update_outline,
    "update_final_summary": GenPathProject.update_final_summary,
    "update_status": GenPathProject.update_status,
    "list_by_user": GenPathProject.list_by_user,
    "count_by_user": GenPathProject.count_by_user,
    "delete": GenPathProject.delete,
    "get_sections": GenPathSection.get_by_project,
    "get_section_by_id": GenPathSection.get_by_id,
    "create_sections": GenPathSection.create_many,
    "update_section_tutorial": GenPathSection.update_tutorial,
    "get_section_resources": GenPathSectionResource.get_by_section,
    "add_section_resource": GenPathSectionResource.add,
})()
