from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from app.models.path_item import PathItem
from app.models.path_item_note import PathItemNote
from app.models.user_learning_path import UserLearningPath


class PathItemNoteCURD:
    @staticmethod
    def get_for_item(
        db: Session, *, user_id: int, path_item_id: int
    ) -> Optional[PathItemNote]:
        return (
            db.query(PathItemNote)
            .filter(
                PathItemNote.user_id == user_id,
                PathItemNote.path_item_id == path_item_id,
            )
            .first()
        )

    @staticmethod
    def list_for_items(
        db: Session, *, user_id: int, path_item_ids: Iterable[int]
    ) -> List[PathItemNote]:
        ids = [int(x) for x in path_item_ids]
        if not ids:
            return []
        return (
            db.query(PathItemNote)
            .filter(
                PathItemNote.user_id == user_id,
                PathItemNote.path_item_id.in_(ids),
            )
            .all()
        )

    @staticmethod
    def upsert(
        db: Session,
        *,
        user_id: int,
        path_item_id: int,
        notes: str,
    ) -> PathItemNote:
        now = datetime.utcnow()
        obj = PathItemNoteCURD.get_for_item(
            db, user_id=user_id, path_item_id=path_item_id
        )
        if obj:
            obj.notes = notes
            obj.updated_at = now
            db.add(obj)
            return obj

        obj = PathItemNote(
            user_id=user_id,
            path_item_id=path_item_id,
            notes=notes,
            updated_at=now,
        )
        db.add(obj)
        return obj

    @staticmethod
    def delete(
        db: Session, *, user_id: int, path_item_id: int
    ) -> bool:
        obj = PathItemNoteCURD.get_for_item(
            db, user_id=user_id, path_item_id=path_item_id
        )
        if not obj:
            return False
        db.delete(obj)
        return True

    @staticmethod
    def check_user_owns_learning_path(
        db: Session, *, user_id: int, learning_path_id: int
    ) -> bool:
        assoc = (
            db.query(UserLearningPath)
            .filter(
                UserLearningPath.user_id == user_id,
                UserLearningPath.learning_path_id == learning_path_id,
            )
            .first()
        )
        return assoc is not None

    @staticmethod
    def get_path_item(db: Session, path_item_id: int) -> Optional[PathItem]:
        return db.query(PathItem).filter(PathItem.id == path_item_id).first()

    @staticmethod
    def list_path_item_ids(db: Session, learning_path_id: int) -> List[int]:
        return [
            pid
            for (pid,) in (
                db.query(PathItem.id)
                .filter(PathItem.learning_path_id == learning_path_id)
                .all()
            )
        ]
