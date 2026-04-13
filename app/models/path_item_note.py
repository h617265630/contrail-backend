from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class PathItemNote(Base):
    __tablename__ = "path_item_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    path_item_id = Column(Integer, ForeignKey("path_items.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "path_item_id", name="uq_path_item_note_user_path"),
    )

    user = relationship("User")
    path_item = relationship("PathItem")
