from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class UserRole(Base):
    """用户-角色关联表（带额外属性）"""
    __tablename__ = 'user_roles'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    assigned_at = Column(DateTime, default=func.now())

    # 关系
    # 显式声明外键，避免与 assigned_by 同时指向 users.id 导致歧义
    user = relationship("User", back_populates="user_roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="role_users", foreign_keys=[role_id])

class RolePermission(Base):
    """角色-权限关联表（带额外属性）"""
    __tablename__ = 'role_permissions'
    
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)
    granted_at = Column(DateTime, default=func.now())

    # 关系
    role = relationship("Role", back_populates="role_permissions", foreign_keys=[role_id])
    permission = relationship("Permission", back_populates="permission_roles", foreign_keys=[permission_id])
