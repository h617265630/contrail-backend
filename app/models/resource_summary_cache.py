from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class ResourceSummaryCache(Base):
    __tablename__ = "resource_summary_cache"

    id = Column(Integer, primary_key=True, index=True)
    # Hash of (url, topic) — unique constraint ensures one summary per URL per topic
    cache_key = Column(String(64), nullable=False, unique=True, index=True)
    url = Column(Text, nullable=False)
    topic = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    key_points = Column(Text, nullable=True)  # JSON string
    difficulty = Column(String(32), nullable=True)
    resource_type = Column(String(32), nullable=True)
    learning_stage = Column(String(32), nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    image = Column(Text, nullable=True)
    fetched_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("ix_resource_summary_cache_url_topic", "url", "topic"),
    )
