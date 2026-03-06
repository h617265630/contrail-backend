from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.models.resources.video import Video

class WatchHistory(Base):
    __tablename__ = 'watch_history'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    video_id = Column(Integer, ForeignKey('videos.id'))
    watch_time = Column(DateTime, default=datetime.now)
    is_watched = Column(Boolean, default=False)
    # 关联到用户和视频表
    user = relationship("User", back_populates="watch_history")
    video = relationship("Video", back_populates="watch_history")

    def __repr__(self):
        return f"<WatchHistory user_id={self.user_id} video_id={self.video_id} watch_time={self.watch_time}>"


    @staticmethod
    def watch_video(db_session, user_id, video_id):
        """插入观看记录并返回该视频的观看次数"""
        watch_record = WatchHistory(user_id=user_id, video_id=video_id)
        db_session.add(watch_record)
        db_session.commit()

        video = db_session.query(Video).filter(Video.id == video_id).first()
        if video:
            return len(video.watch_history)  # 获取观看次数
        return 0
