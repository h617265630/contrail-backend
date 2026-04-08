from sqlalchemy import Column, Integer, ForeignKey
from app.db.database import Base


class VideoCategory(Base):
    __tablename__ = 'video_category'
    # 多对多关联表（联合主键确保唯一配对）
    video_id = Column(Integer, ForeignKey('videos.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)

