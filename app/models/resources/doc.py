from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Doc(Base):
    __tablename__ = "docs"

    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    doc_type = Column(String(50), nullable=True)
    version = Column(String(50), nullable=True)

    resource = relationship("Resource", back_populates="doc", uselist=False)
    



