# backend/app/core/initial_data.py
from sqlalchemy.orm import Session
from app.models.rbac.role import Role
from app.models.rbac.permission import Permission
from app.models.rbac.user import User
from app.models.category import Category
from app import auth


def init_default_categories(db: Session):
    """初始化默认热门分类（用于 CreatePath 下拉选择）"""
    default_categories = [
        {"name": "AI", "code": "ai"},
        {"name": "Design", "code": "design"},
        {"name": "UI", "code": "ui"},
        {"name": "Frontend", "code": "frontend"},
        {"name": "Backend", "code": "backend"},
        {"name": "Handmade", "code": "handmade"},
        {"name": "Other", "code": "other"},
    ]

    for cat in default_categories:
        existing = db.query(Category).filter(Category.code == cat["code"]).first()
        if not existing:
            db.add(
                Category(
                    name=cat["name"],
                    code=cat["code"],
                    level=0,
                    is_leaf=True,
                    is_system=True,
                    owner_user_id=None,
                )
            )

    db.commit()
    print("✅ 默认分类初始化完成")

def init_default_permissions(db: Session):
    """初始化默认权限"""
    default_permissions = [
        # 用户模块权限
        {"name": "查看用户", "code": "user.read", "module": "user", "action": "read"},
        {"name": "创建用户", "code": "user.create", "module": "user", "action": "create"},
        {"name": "更新用户", "code": "user.update", "module": "user", "action": "update"},
        {"name": "删除用户", "code": "user.delete", "module": "user", "action": "delete"},
        {"name": "管理用户角色", "code": "user.role.manage", "module": "user", "action": "role_manage"},
        
        # 角色模块权限
        {"name": "查看角色", "code": "role.read", "module": "role", "action": "read"},
        {"name": "创建角色", "code": "role.create", "module": "role", "action": "create"},
        {"name": "更新角色", "code": "role.update", "module": "role", "action": "update"},
        {"name": "删除角色", "code": "role.delete", "module": "role", "action": "delete"},
        
        # 权限模块权限
        {"name": "查看权限", "code": "permission.read", "module": "permission", "action": "read"},
        {"name": "创建权限", "code": "permission.create", "module": "permission", "action": "create"},
        {"name": "更新权限", "code": "permission.update", "module": "permission", "action": "update"},
        {"name": "删除权限", "code": "permission.delete", "module": "permission", "action": "delete"},
        
        # 视频模块权限
        {"name": "查看视频", "code": "video.read", "module": "video", "action": "read"},
        {"name": "上传视频", "code": "video.upload", "module": "video", "action": "upload"},
        {"name": "编辑视频", "code": "video.update", "module": "video", "action": "update"},
        {"name": "删除视频", "code": "video.delete", "module": "video", "action": "delete"},
        
        # 剪辑模块权限
        {"name": "查看剪辑", "code": "clip.read", "module": "clip", "action": "read"},
        {"name": "创建剪辑", "code": "clip.create", "module": "clip", "action": "create"},
        {"name": "编辑剪辑", "code": "clip.update", "module": "clip", "action": "update"},
        {"name": "删除剪辑", "code": "clip.delete", "module": "clip", "action": "delete"},
    ]
    
    for perm_data in default_permissions:
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
    
    db.commit()
    print("✅ 默认权限初始化完成")

def init_default_roles(db: Session):
    """初始化默认角色"""
    default_roles = [
        {
            "name": "超级管理员",
            "code": "super_admin",
            "description": "系统超级管理员，拥有所有权限",
            "level": 0,
            "is_system": True,
            "is_active": True
        },
        {
            "name": "管理员",
            "code": "admin",
            "description": "系统管理员",
            "level": 10,
            "is_system": True,
            "is_active": True
        },
        {
            "name": "编辑",
            "code": "editor",
            "description": "内容编辑",
            "level": 20,
            "is_system": True,
            "is_active": True
        },
        {
            "name": "普通用户",
            "code": "user",
            "description": "普通用户",
            "level": 100,
            "is_system": True,
            "is_active": True
        },
        {
            "name": "游客",
            "code": "guest",
            "description": "游客（未登录用户）",
            "level": 1000,
            "is_system": True,
            "is_active": True
        }
    ]
    
    for role_data in default_roles:
        existing = db.query(Role).filter(Role.code == role_data["code"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
    
    db.commit()
    
    # 为超级管理员角色分配所有权限
    super_admin = db.query(Role).filter(Role.code == "super_admin").first()
    if super_admin:
        all_permissions = db.query(Permission).all()
        super_admin.permissions = all_permissions
        db.commit()
    
    # 为管理员角色分配管理权限
    admin = db.query(Role).filter(Role.code == "admin").first()
    if admin:
        admin_permissions = db.query(Permission).filter(
            Permission.module.in_(["user", "role", "permission", "video", "clip"])
        ).all()
        admin.permissions = admin_permissions
        db.commit()
    
    # 为编辑角色分配内容管理权限
    editor = db.query(Role).filter(Role.code == "editor").first()
    if editor:
        editor_permissions = db.query(Permission).filter(
            Permission.module.in_(["video", "clip"])
        ).all()
        editor.permissions = editor_permissions
        db.commit()
    
    print("✅ 默认角色初始化完成")

def init_super_admin(db: Session):
    """初始化超级管理员用户"""
    # 检查是否已存在超级管理员
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        return existing_admin
    
    # 创建超级管理员用户
    hashed_password = auth.hash_password("admin123")
    admin_user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hashed_password,
        display_name="系统管理员",
        is_superuser=True,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # 分配超级管理员角色
    super_admin_role = db.query(Role).filter(Role.code == "super_admin").first()
    if super_admin_role:
        admin_user.roles = [super_admin_role]
        db.commit()
    
    print("✅ 超级管理员用户初始化完成")
    return admin_user

def init_default_data(db: Session):
    """初始化所有默认数据"""
    print("正在初始化默认数据...")
    init_default_permissions(db)
    init_default_roles(db)
    init_super_admin(db)
    init_default_categories(db)
    print("🎉 默认数据初始化完成")