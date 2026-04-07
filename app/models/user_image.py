from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from datetime import datetime

from app.db.database import Base


class UserImage(Base):
    __tablename__ = "user_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    image_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
