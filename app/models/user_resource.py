from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class UserResource(Base):
    __tablename__ = "user_resource"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), primary_key=True)

    # 来源：created=用户自己创建，saved=从公共池添加
    source = Column(
        Enum("created", "saved", name="user_resource_source"),
        nullable=False,
        default="saved",
    )

    # 用户可见性：是否在个人主页/分享页面展示
    is_public = Column(Boolean, default=False, nullable=False)

    # 用户自定义分类（覆盖 resources.category_id，NULL 时用原始分类）
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # 二次修改扩展字段
    custom_notes = Column(Text, nullable=True)      # 个人笔记
    custom_tags = Column(JSON, nullable=True)         # 个人标签（不污染原始 tags）
    personal_rating = Column(Integer, nullable=True)  # 个人评分 1-5
    is_favorite = Column(Boolean, default=False, nullable=False)  # 收藏标记

    created_at = Column(DateTime, default=datetime.utcnow)

    manual_weight = Column(Integer, nullable=True)
    behavior_weight = Column(Integer, nullable=True)
    effective_weight = Column(Integer, nullable=True)

    added_at = Column(DateTime, default=datetime.utcnow)
    last_opened = Column(DateTime, nullable=True)
    open_count = Column(Integer, default=0, nullable=False)
    completion_status = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="user_resources")
    resource = relationship("Resource", back_populates="user_resources")
    category = relationship("Category")

    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", name="uq_user_resource"),
    )
