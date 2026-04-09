from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from app.models.path_item import PathItem
from app.models.progress import Progress
from app.models.user_learning_path import UserLearningPath


class ProgressCURD:
    @staticmethod
    def get_for_item(db: Session, *, user_id: int, path_item_id: int) -> Optional[Progress]:
        return (
            db.query(Progress)
            .filter(Progress.user_id == user_id, Progress.path_item_id == path_item_id)
            .order_by(Progress.id.desc())
            .first()
        )

    @staticmethod
    def list_for_items(db: Session, *, user_id: int, path_item_ids: Iterable[int]) -> List[Progress]:
        ids = [int(x) for x in path_item_ids]
        if not ids:
            return []
        return (
            db.query(Progress)
            .filter(Progress.user_id == user_id, Progress.path_item_id.in_(ids))
            .all()
        )

    @staticmethod
    def upsert(
        db: Session,
        *,
        user_id: int,
        path_item_id: int,
        progress_percentage: int,
    ) -> Progress:
        pct = int(progress_percentage)
        if pct < 0 or pct > 100:
            raise ValueError("progress_percentage must be 0..100")

        # Ensure the path item exists.
        hit = db.query(PathItem).filter(PathItem.id == path_item_id).first()
        if not hit:
            raise ValueError("PathItem not found")

        obj = ProgressCURD.get_for_item(db, user_id=user_id, path_item_id=path_item_id)
        now = datetime.utcnow()

        if obj:
            # Never decrease progress.
            obj.progress_percentage = max(int(obj.progress_percentage or 0), pct)
            obj.last_watched_time = now
            db.add(obj)
            return obj

        obj = Progress(
            user_id=user_id,
            path_item_id=path_item_id,
            progress_percentage=pct,
            last_watched_time=now,
        )
        db.add(obj)
        return obj

    @staticmethod
    def check_user_owns_learning_path(
        db: Session, *, user_id: int, learning_path_id: int
    ) -> bool:
        """Check if user owns (has attached) the learning path. Returns True if owned."""
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
        """Get a path item by ID."""
        return db.query(PathItem).filter(PathItem.id == path_item_id).first()

    @staticmethod
    def list_path_item_ids(db: Session, learning_path_id: int) -> List[int]:
        """Get all path item IDs for a learning path."""
        return [
            pid
            for (pid,) in (
                db.query(PathItem.id)
                .filter(PathItem.learning_path_id == learning_path_id)
                .all()
            )
        ]
