# 生成一个Categories模型的示例代码
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    level = Column(Integer, default=0)  # 0表示顶级分类
    description = Column(Text, nullable=True)
    is_leaf = Column(Boolean, default=1)  # 1表示是叶子节点，0表示不是叶子节点
    is_system = Column(Boolean, default=True, nullable=False)
    owner_user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("Category", remote_side=[id], backref="children")
    owner = relationship("User", foreign_keys=[owner_user_id])

    # 联合唯一约束：同一 owner 下 name/code 不能重复
    # 系统分类（owner_user_id=NULL）通过 DB 层唯一约束保证
    # 用户自定义分类通过同一 (name/code, owner_user_id) 组合唯一保证
    __table_args__ = (
        UniqueConstraint('name', 'owner_user_id', name='uq_category_name_owner'),
        UniqueConstraint('code', 'owner_user_id', name='uq_category_code_owner'),
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', level={self.level})>"

    def get_full_path(self):
        """获取类别的完整路径"""
        path_parts = [self.name]
        current = self.parent
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        return ' / '.join(path_parts)