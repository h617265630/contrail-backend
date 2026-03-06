from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.category import Category
from app.models.resources.video import Video
from app.models.user_video import UserVideo
from app.schemas.resources.video import VideoCreate

class VideoCURD:
    @staticmethod
    def get_video(db: Session, video_id: int) -> Optional[Video]:
        return db.query(Video).filter(Video.id == video_id).first()
    
    @staticmethod
    def get_videos_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Video]:
        videos = db.query(Video).join(UserVideo,UserVideo.video_id==Video.id)\
                    .filter(UserVideo.user_id == user_id)\
                    .offset(skip)\
                    .limit(limit)\
                    .all()
        return videos
    
    @staticmethod
    def create_video(db: Session, video_in: VideoCreate, owner_id: int) -> Video:
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
        return db.query(Video).offset(skip).limit(limit).all()
    
    
    @staticmethod
    def delete_video(db: Session, video: Video) -> None:
        db.delete(video)
        db.commit() 

    # ============ 分类管理 ============
    @staticmethod
    def add_category_to_video(db: Session, video_id: int, category_id: int) -> Video:
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
    def remove_category_from_video(db: Session, video_id: int, category_id: int) -> Video:
        video = VideoCURD.get_video(db, video_id)
        if not video:
            raise ValueError("视频不存在")
        # 过滤掉对应分类
        video.categories = [c for c in video.categories if c.id != category_id]
        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    def assign_categories_to_video(db: Session, video_id: int, category_ids: List[int]) -> Video:
        video = VideoCURD.get_video(db, video_id)
        if not video:
            raise ValueError("视频不存在")
        if not category_ids:
            # 清空分类
            video.categories = []
            db.commit()
            db.refresh(video)
            return video
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        if len(categories) != len(set(category_ids)):
            # 有不存在的分类 ID
            raise ValueError("部分分类不存在")
        video.categories = categories
        db.commit()
        db.refresh(video)
        return video