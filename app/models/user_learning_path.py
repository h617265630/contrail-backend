from sqlalchemy import Column, Integer, ForeignKey
from app.db.database import Base

class UserLearningPath(Base):
    __tablename__ = "user_learning_paths"
    # sqlalchemy 自动处理联合主键，id不需要
    Base.metadata,
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    learning_path_id = Column(Integer, ForeignKey('learning_paths.id'), primary_key=True)
