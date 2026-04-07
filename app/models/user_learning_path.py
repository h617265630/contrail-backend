from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from app.db.database import Base


class UserLearningPath(Base):
    __tablename__ = "user_learning_paths"

    # 联合主键: (user_id, learning_path_id)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), primary_key=True)

    # 用户自定义覆盖字段（收藏公共路径时的个性化展示，不影响原始路径）
    custom_title = Column(String(200), nullable=True)
    custom_description = Column(Text, nullable=True)
    custom_cover_image_url = Column(String(2048), nullable=True)
    notes = Column(Text, nullable=True)  # 用户对这条路径的备注

    # 补充缺失字段
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_pinned = Column(Integer, default=0, nullable=False)  # 0=不置顶, 1=置顶

