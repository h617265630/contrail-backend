from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, Enum, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class ResourceType(enum.Enum):
    VIDEO = "video"
    DOCUMENT = "document"
    ARTICLE = "article"
    CLIP = "clip"

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(
        Enum(
            "video",
            "document",
            "article",
            "clip",
            name="resourcetype",
        ),
        nullable=False,
    )
    platform = Column(String(50), nullable=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    source_url = Column(String(2048), nullable=False)
    thumbnail = Column(String(1000), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    difficulty = Column(Integer, nullable=True)
    tags = Column(JSON, nullable=True)
    raw_meta = Column(JSON, nullable=True)
    is_system_public = Column(Boolean, default=False, nullable=False)

    community_score = Column(Integer, default=0, nullable=False)
    save_count = Column(Integer, default=0, nullable=False)
    trending_score = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    
    # 关系：Resource 可以关联多个 PathItem
    path_items = relationship("PathItem", back_populates="resource")

    user_resources = relationship("UserResource", back_populates="resource", cascade="all, delete-orphan")

    category = relationship("Category")

    video = relationship("Video", back_populates="resource", uselist=False)
    doc = relationship("Doc", back_populates="resource", uselist=False)
    article = relationship("Article", back_populates="resource", uselist=False)
    
    @property
    def category_name(self):
        try:
            return getattr(self.category, "name", None)
        except Exception:
            return None

    def __repr__(self):
        return f"<Resource {self.title} ({self.resource_type})>"