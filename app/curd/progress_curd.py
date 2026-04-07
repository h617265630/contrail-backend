from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from app.models.path_item import PathItem
from app.models.progress import Progress


class ProgressCURD:
    @staticmethod
    def get_for_item(db: Session, *, user_id: int, path_item_id: int) -> Optional[Progress]:
        return (
            db.query(Progress)
            .filter(Progress.user_id == user_id, Progress.path_item_id == path_item_id)
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
            if pct >= 100 and obj.completed_at is None:
                obj.completed_at = now
            db.add(obj)
            return obj

        obj = Progress(
            user_id=user_id,
            path_item_id=path_item_id,
            progress_percentage=pct,
            last_watched_time=now,
            completed_at=now if pct >= 100 else None,
        )
        db.add(obj)
        return obj
