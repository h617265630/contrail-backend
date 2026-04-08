from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List, Optional
from app.models.resources.clip import Clip
from app.models.relations import UserVideoLike, UserFollow, LikeType

class ClipCURD:
    @staticmethod
    def get_clip(db: Session, clip_id: int) -> Optional[Clip]:
        return db.query(Clip).filter(Clip.id == clip_id).first()
    
    @staticmethod
    def get_clips_by_videoId(db: Session, video_id: int, skip: int = 0, limit: int = 100) -> List[Clip]:
        clips = db.query(Clip)\
                .filter(Clip.from_video_id == video_id)\
                .offset(skip)\
                .limit(limit)\
                .all()
        return clips
    

    @staticmethod
    def create_clip(db: Session, title: str, video_id: int, **kwargs) -> Clip:
        clip = Clip(title=title, from_video_id=video_id, **kwargs)
        db.add(clip)
        db.commit()
        db.refresh(clip)
        return clip
    
    ### 添加 通过 user 查询，user 查询 喜欢的 保存的片段。

    @staticmethod
    def delete_clip(db: Session, video: Clip) -> None:
        db.delete(video)
        db.commit() 