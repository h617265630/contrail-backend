from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Role(Base):
    "role model"
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)  # 角色代码，如：admin, user, moderator
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # 是否为系统内置角色
    level = Column(Integer, default=0)  # 角色等级，数字越小权限越高
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    # 多对多：角色-用户（通过关联表 user_roles）
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )
    # 关联对象集合：Role 与 UserRole 的一对多
    role_users = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    # 多对多：角色-权限（通过关联表 role_permissions） - 集合访问
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
    )
    # 关联对象集合：Role 与 RolePermission 的一对多
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "is_active": self.is_active,
            "level": self.level,
            "permission_count": len(self.permissions) if self.permissions else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    