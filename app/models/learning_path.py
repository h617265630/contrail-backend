from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class PathStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    type = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    cover_image_url = Column(String(2048), nullable=True)

    # 创建者 ID：NULL=系统/管理员创建，creator_id == user_id=用户创建
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)

    # Fork lineage
    parent_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="SET NULL"), nullable=True, index=True)
    root_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="SET NULL"), nullable=True, index=True)

    # 发布状态
    status = Column(Enum(PathStatus), nullable=False, default=PathStatus.draft)
    published_at = Column(DateTime, nullable=True)

    # 统计字段
    fork_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    view_count = Column(Integer, nullable=False, default=0)

    category = relationship("Category")
    users = relationship("User", back_populates="learning_paths", secondary="user_learning_paths")
    path_items = relationship("PathItem", back_populates="learning_path", order_by="PathItem.order_index")
    comments = relationship("LearningPathComment", back_populates="learning_path", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<LearningPath(id={self.id}, title='{self.title}')>"

    @property
    def category_name(self):
        try:
            return getattr(self.category, "name", None)
        except Exception:
            return None

    @property
    def item_count(self) -> int:
        try:
            return len(self.path_items) if hasattr(self, "path_items") and self.path_items else 0
        except Exception:
            return 0