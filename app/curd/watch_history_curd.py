"""
Watch history CRUD operations for tracking user video consumption.

Provides database operations for:
- Recording when a user watches a video
- Querying watch counts per video
- Retrieving a user's watch history
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.watch_history import WatchHistory
from app.models.resources.video import Video
from app.models.rbac.user import User


class WatchHistoryCURD:
    """CRUD operations for WatchHistory model."""

    @staticmethod
    def record_watch(
        db: Session,
        user_id: int,
        video_id: int,
        is_watched: bool = True,
        watch_time: Optional[datetime] = None,
    ) -> WatchHistory:
        """
        Record a watch event for a user and video.

        Args:
            db: Database session.
            user_id: ID of the user who watched the video.
            video_id: ID of the video that was watched.
            is_watched: Flag indicating if video was fully watched (default True).
            watch_time: Timestamp of the watch event.
                       Defaults to current time if not provided.

        Returns:
            Created WatchHistory record object.

        Raises:
            ValueError: If user or video does not exist.
        """
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
        """
        Get the total number of watch records for a video.

        Args:
            db: Database session.
            video_id: ID of the video.

        Returns:
            Total count of watch records for the video.
        """
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
        """
        Retrieve a user's watch history ordered by most recent first.

        Args:
            db: Database session.
            user_id: ID of the user whose history to retrieve.
            offset: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            List of WatchHistory objects for the user.
        """
        return (
            db.query(WatchHistory)
            .filter(WatchHistory.user_id == user_id)
            .order_by(WatchHistory.watch_time.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
