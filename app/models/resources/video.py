from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Video(Base):
    __tablename__ = "videos"

    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    duration = Column(Integer, nullable=True)
    channel = Column(String(255), nullable=True)
    video_id = Column(String(100), nullable=True)

    resource = relationship("Resource", back_populates="video", uselist=False)

    def __repr__(self):
        return f"<Video(resource_id={self.resource_id})>"
