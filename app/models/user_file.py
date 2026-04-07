from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db.database import Base


class UserFile(Base):
    __tablename__ = "user_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String(200), nullable=True)
    file_type = Column(String(20), nullable=False)  # md | txt

    original_filename = Column(String(512), nullable=True)
    content_type = Column(String(200), nullable=True)
    size_bytes = Column(Integer, nullable=True)

    content = Column(Text, nullable=True)

    file_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
