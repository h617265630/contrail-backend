from sqlalchemy import Column, Integer, String,DateTime,Boolean,Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    type = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    cover_image_url = Column(String(2048), nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    category = relationship("Category")
    # relationships 
    #users - learning_paths 多对多关系
    users = relationship("User",back_populates="learning_paths",secondary="user_learning_paths")
    #path_items -learnging_paths 多对多关系
    path_items = relationship("PathItem", back_populates="learning_path",order_by="PathItem.order_index")
    # 评论关系
    comments = relationship("LearningPathComment", back_populates="learning_path", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<LearningPath(id={self.id}, title='{self.title}')>"

    @property
    def category_name(self):
        try:
            return getattr(self.category, "name", None)
        except Exception:
            return None