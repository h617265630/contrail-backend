"""
Video CRUD operations for resource management.

Provides database operations for video resources including:
- Video creation, retrieval, and deletion
- User-video association management
- Video category assignment and management
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.category import Category
from app.models.resources.video import Video
from app.models.user_video import UserVideo
from app.schemas.resources.video import VideoCreate


class VideoCURD:
    """CRUD operations for Video model."""

    @staticmethod
    def get_video(db: Session, video_id: int) -> Optional[Video]:
        """
        Retrieve a video by its ID.

        Args:
            db: Database session.
            video_id: Unique identifier of the video.

        Returns:
            Video object if found, None otherwise.
        """
        return db.query(Video).filter(Video.id == video_id).first()

    @staticmethod
    def get_videos_by_user(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Video]:
        """
        Retrieve all videos owned by a specific user.

        Args:
            db: Database session.
            user_id: ID of the owning user.
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            List of Video objects belonging to the user.
        """
        videos = (
            db.query(Video)
            .join(UserVideo, UserVideo.video_id == Video.id)
            .filter(UserVideo.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return videos

    @staticmethod
    def create_video(db: Session, video_in: VideoCreate, owner_id: int) -> Video:
        """
        Create a new video and associate it with an owner.

        Args:
            db: Database session.
            video_in: Video creation data schema.
            owner_id: ID of the user who will own this video.

        Returns:
            Newly created Video object.

        Raises:
            Exception: If video is already associated with the user.
        """
        data = video_in.model_dump(exclude_unset=True)
        video = Video(**data)
        db.add(video)
        db.commit()
        db.refresh(video)

        # 创建用户-视频关联记录
        user_video = UserVideo(user_id=owner_id, video_id=video.id)
        try:
            db.add(user_video)
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("This video is already associated with the user.")

        return video

    @staticmethod
    def get_videos(db: Session, skip: int = 0, limit: int = 100) -> List[Video]:
        """
        Retrieve a paginated list of all videos.

        Args:
            db: Database session.
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            List of Video objects.
        """
        return db.query(Video).offset(skip).limit(limit).all()

    @staticmethod
    def delete_video(db: Session, video: Video) -> None:
        """
        Delete a video from the database.

        Args:
            db: Database session.
            video: Video instance to delete.
        """
        db.delete(video)
        db.commit()

    # ============== Category Management ==============

    @staticmethod
    def add_category_to_video(
        db: Session, video_id: int, category_id: int
    ) -> Video:
        """
        Add a single category to a video.

        Args:
            db: Database session.
            video_id: ID of the video to update.
            category_id: ID of the category to add.

        Returns:
            Updated Video object.

        Raises:
            ValueError: If video or category does not exist.
        """
        video = VideoCURD.get_video(db, video_id)
        if not video:
            raise ValueError("视频不存在")
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise ValueError("分类不存在")

        # 避免重复添加
        if any(c.id == category_id for c in video.categories):
            return video
        video.categories.append(category)
        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    def remove_category_from_video(
        db: Session, video_id: int, category_id: int
    ) -> Video:
        """
        Remove a single category from a video.

        Args:
            db: Database session.
            video_id: ID of the video to update.
            category_id: ID of the category to remove.

        Returns:
            Updated Video object.

        Raises:
            ValueError: If video does not exist.
        """
        video = VideoCURD.get_video(db, video_id)
        if not video:
            raise ValueError("视频不存在")

        # 过滤掉对应分类
        video.categories = [c for c in video.categories if c.id != category_id]
        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    def assign_categories_to_video(
        db: Session, video_id: int, category_ids: List[int]
    ) -> Video:
        """
        Replace all categories of a video with a new set.

        Args:
            db: Database session.
            video_id: ID of the video to update.
            category_ids: List of category IDs to assign.
                         Empty list clears all categories.

        Returns:
            Updated Video object.

        Raises:
            ValueError: If video does not exist or any category ID is invalid.
        """
        video = VideoCURD.get_video(db, video_id)
        if not video:
            raise ValueError("视频不存在")

        if not category_ids:
            # 清空分类
            video.categories = []
            db.commit()
            db.refresh(video)
            return video

        categories = db.query(Category).filter(
            Category.id.in_(category_ids)
        ).all()
        if len(categories) != len(set(category_ids)):
            # 有不存在的分类 ID
            raise ValueError("部分分类不存在")

        video.categories = categories
        db.commit()
        db.refresh(video)
        return video