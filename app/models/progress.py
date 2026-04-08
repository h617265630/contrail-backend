from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base

class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    path_item_id = Column(Integer, ForeignKey('path_items.id'))
    last_watched_time = Column(DateTime)
    progress_percentage = Column(Integer)  # 学习进度百分比
    
    # 关系：Progress 属于用户和路径项
    user = relationship("User")
    path_item = relationship("PathItem")
    
    def __repr__(self):
        return f"<Progress {self.user.username} - {self.path_item.id}>"
