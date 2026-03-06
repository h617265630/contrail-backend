from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from app.models.rbac.role import Role
from app.models.rbac.permission import Permission
from app.schemas.rbac.role import RoleCreate

class RoleCURD:
    @staticmethod
    def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def get_role_by_code(db: Session, code: str) -> Optional[Role]:
        return db.query(Role).filter(Role.code == code).first()
    
    @staticmethod
    def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        return db.query(Role).order_by(Role.level).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_active_roles(db: Session) -> List[Role]:
        return db.query(Role).filter(Role.is_active == True).order_by(Role.level).all()
    
    @staticmethod
    def create_role(db: Session, role_in: RoleCreate) -> Role:
        db_role = Role(
            name=role_in.name,
            code=role_in.code,
            description=role_in.description,
            level=role_in.level,
            is_active=role_in.is_active
        )
        
        if role_in.permission_ids:
            permissions = db.query(Permission).filter(
                Permission.id.in_(role_in.permission_ids)
            ).all()
            db_role.permissions = permissions
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def update_role(db: Session, role_id: int, role_update: dict) -> Optional[Role]:
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            return None
        
        for field, value in role_update.items():
            if hasattr(db_role, field):
                setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if db_role and not db_role.is_system:  # 不能删除系统角色
            db.delete(db_role)
            db.commit()
            return True
        return False
    
    @staticmethod
    def assign_permissions(db: Session, role_id: int, permission_ids: List[int]) -> Optional[Role]:
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            return None
        
        permissions = db.query(Permission).filter(
            Permission.id.in_(permission_ids)
        ).all()
        
        db_role.permissions = permissions
        db.commit()
        db.refresh(db_role)
        return db_role
