from sqlalchemy import Column, Integer, ForeignKey,Boolean,String
from app.db.database import Base
from sqlalchemy.orm import relationship

class UserVideo(Base):
    __tablename__ = 'user_video'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    video_id = Column(Integer, ForeignKey('videos.id'), primary_key=True)
    liked = Column(Boolean, default=False)

    views_count = Column(Integer, default=0)
    is_public=Column(Boolean, default=True)
    status = Column(String(20), default="processing")  # e.g., 'processing', 'available', 'deleted'

    # 关系：关联对象模式，分别与 User / Video 的关联对象集合进行回填
    user = relationship("User", back_populates="user_videos")
    video = relationship("Video", back_populates="user_videos")