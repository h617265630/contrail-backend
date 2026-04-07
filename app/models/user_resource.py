from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class UserResource(Base):
    __tablename__ = "user_resource"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), primary_key=True)

    # 用户可见性：是否在个人主页/分享页面展示
    is_public = Column(Boolean, default=False, nullable=False)

    # 用户自定义覆盖字段（不为 NULL 时，优先于 Resource 原始值显示）
    custom_title = Column(String(500), nullable=True)
    custom_summary = Column(Text, nullable=True)
    custom_thumbnail = Column(String(1000), nullable=True)

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

    __table_args__ = (
        UniqueConstraint("user_id", "resource_id", name="uq_user_resource"),
    )
