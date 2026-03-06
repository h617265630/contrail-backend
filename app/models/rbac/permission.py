from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Permission(Base):
    """权限模型"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(100), unique=True, index=True, nullable=False)  # 权限代码，如：user.create, user.delete
    description = Column(Text, nullable=True)
    module = Column(String(50), nullable=False)  # 模块，如：user, role, permission
    action = Column(String(50), nullable=False)  # 操作，如：create, read, update, delete
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    # 多对多：权限-角色（通过关联表 role_permissions）
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    # 关联对象集合：Permission 与 RolePermission 的一对多
    permission_roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "module": self.module,
            "action": self.action,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }