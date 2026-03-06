from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Article(Base):
    __tablename__ = "articles"

    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    publisher = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)

    resource = relationship("Resource", back_populates="article", uselist=False)
