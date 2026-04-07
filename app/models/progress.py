from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (
        # 每个用户每条路径项只有一条进度记录
        UniqueConstraint("user_id", "path_item_id", name="uq_progress_user_pathitem"),
    )

    # 联合主键：(user_id, path_item_id)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    path_item_id = Column(Integer, ForeignKey("path_items.id"), primary_key=True)

    progress_percentage = Column(Integer, default=0, nullable=False)  # 0-100
    last_watched_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)  # 完成时记录时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User")
    path_item = relationship("PathItem")

    def __repr__(self):
        return f"<Progress user={self.user_id} path_item={self.path_item_id} pct={self.progress_percentage}>"
