from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.watch_history import WatchHistory
from app.models.resources.video import Video
from app.models.rbac.user import User


class WatchHistoryCURD:
    @staticmethod
    def record_watch(
        db: Session,
        user_id: int,
        video_id: int,
        is_watched: bool = True,
        watch_time: Optional[datetime] = None,
    ) -> WatchHistory:
        # 校验用户与视频是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError("视频不存在")

        record = WatchHistory(
            user_id=user_id,
            video_id=video_id,
            is_watched=is_watched,
            watch_time=watch_time or datetime.now(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_video_watch_count(db: Session, video_id: int) -> int:
        return (
            db.query(func.count(WatchHistory.id))
            .filter(WatchHistory.video_id == video_id)
            .scalar()
            or 0
        )

    @staticmethod
    def get_user_watch_history(
        db: Session, user_id: int, offset: int = 0, limit: int = 50
    ) -> List[WatchHistory]:
        return (
            db.query(WatchHistory)
            .filter(WatchHistory.user_id == user_id)
            .order_by(WatchHistory.watch_time.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
