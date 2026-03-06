from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy import UniqueConstraint
# 采用多模态或者继承的方式来实现 PathItem

class PathItem(Base):
    __tablename__ = "path_items"
    
    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey('learning_paths.id', ondelete="CASCADE"), nullable=False)  # 所属的学习路径 ID
    resource_id = Column(Integer, ForeignKey('resources.id', ondelete="CASCADE"), nullable=False)  # 对应资源的 ID（指向 Resource.id）
    order_index = Column(Integer, nullable=False)  # 在学习路径中的顺序
    stage = Column(String(100), nullable=True)
    purpose = Column(String(255), nullable=True)
    estimated_time = Column(Integer, nullable=True)
    is_optional = Column(Boolean, default=False, nullable=False)

    # 关系：PathItem 属于一个学习路径
    learning_path = relationship("LearningPath",  back_populates="path_items")
    resource = relationship("Resource", back_populates="path_items")

    __table_args__ = (
        UniqueConstraint('learning_path_id', 'order_index', name='uq_learning_path_order'),
        UniqueConstraint('learning_path_id', 'resource_id', name='uq_learning_path_resource')
    )

    def __repr__(self):
        return f"<PathItem(id={self.id}, learning_path_id={self.learning_path_id}, order_index={self.order_index})>"
