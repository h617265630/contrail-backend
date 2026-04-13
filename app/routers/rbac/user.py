# backend/app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.rbac.user import AvatarUploadResponse, ChangePasswordRequest, UserCreate, UserMeUpdate, UserResponse, Token
from app.curd.rbac.user_curd import UserCURD
from app import auth,curd
from app.core.deps import get_db_dep,get_current_user
from app.core.validators import normalize_email, validate_password, validate_username
from pathlib import Path
from datetime import datetime
import os
import re
import secrets

from pydantic import BaseModel
from app.core.config import settings

from app.models.rbac.user import User
from app.schemas.rbac import UserWithRoles
from app.core.deps import get_db, PermissionChecker

router = APIRouter(prefix="/users", tags=["Users"])


class GoogleLoginRequest(BaseModel):
    id_token: str


def _generate_unique_username(db: Session, email: str) -> str:
    raw = (email or "").split("@", 1)[0].strip().lower()
    base = re.sub(r"[^a-z0-9_]", "", raw)
    if len(base) < 3:
        base = "user" + base
    base = base[:32]

    candidate = base
    suffix = 1
    while UserCURD.get_user_by_username(db, candidate):
        extra = f"{suffix}"
        candidate = (base[: max(0, 32 - len(extra))] + extra)[:32]
        suffix += 1
        if suffix > 9999:
            candidate = f"user{secrets.randbelow(10**9)}"[:32]
            break

    if len(candidate) < 3:
        candidate = (candidate + "user")[:3]
    return candidate


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db_dep)):
    # Pydantic 已完成基础校验；这里再次确保“先校验/规范化、后查库”
    username_norm = validate_username(user_in.username)
    email_norm = normalize_email(str(user_in.email))
    _ = validate_password(user_in.password)

    # check existing
    if UserCURD.get_user_by_username(db, username_norm):
        raise HTTPException(status_code=400, detail="Username already registered")
    if UserCURD.get_user_by_email(db, email_norm):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth.hash_password(user_in.password)
    try:
        user = UserCURD.create_user(db, username=username_norm, email=email_norm, hashed_password=hashed)
    except ValueError as ve:
        # Duplicate checks surfaced from CURD layer
        detail = str(ve)
        # Username/Email duplication -> 409 Conflict 更贴切
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_dep)):
    identifier = (form_data.username or "").strip()
    try:
        if not identifier:
            raise ValueError("Username is required")
        validate_password(form_data.password)
    except ValueError:
        # 避免泄露细节：统一提示
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 支持 username 或 email 登录；精确匹配但大小写无关
    if "@" in identifier:
        try:
            email_norm = normalize_email(identifier)
        except ValueError:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        user = UserCURD.get_user_by_email(db, email_norm)
    else:
        username_norm = validate_username(identifier)
        user = UserCURD.get_user_by_username(db, username_norm)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = auth.create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/google-login", response_model=Token)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db_dep)):
    try:
        from google.oauth2 import id_token as google_id_token
        from google.auth.transport import requests as google_requests
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Google login dependencies are not installed. Please install 'google-auth'.",
        )

    client_id = str(getattr(settings, "GOOGLE_CLIENT_ID", "") or "").strip()
    if not client_id:
        raise HTTPException(status_code=500, detail="Google login is not configured")

    token_str = str(payload.id_token or "").strip()
    if not token_str:
        raise HTTPException(status_code=400, detail="Missing Google token")

    try:
        info = google_id_token.verify_oauth2_token(token_str, google_requests.Request(), client_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {e}")

    email_raw = str(info.get("email") or "").strip()
    if not email_raw:
        raise HTTPException(status_code=400, detail="Google account does not provide an email")

    try:
        email_norm = normalize_email(email_raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid email from Google")

    if info.get("email_verified") is False:
        raise HTTPException(status_code=400, detail="Google email is not verified")

    user = UserCURD.get_user_by_email(db, email_norm)
    if not user:
        username = _generate_unique_username(db, email_norm)
        random_password = secrets.token_urlsafe(32)
        hashed = auth.hash_password(random_password)
        user = UserCURD.create_user(db, username=username, email=email_norm, hashed_password=hashed)

        display_name = str(info.get("name") or "").strip()
        picture = str(info.get("picture") or "").strip()
        if display_name:
            user.display_name = display_name
        if picture:
            user.avatar_url = picture
        db.add(user)
        db.commit()
        db.refresh(user)

    token = auth.create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user = Depends(get_current_user)):
    # current_user 来自 deps.get_current_user（SQLAlchemy User 实例）
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_current_user(payload: UserMeUpdate, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    # Only allow editing non-sensitive profile fields here.
    if payload.display_name is not None:
        current_user.display_name = payload.display_name
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_my_password(payload: ChangePasswordRequest, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    # Validate new password using shared validator (also enforces non-empty)
    validate_password(payload.new_password)

    if not auth.verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    current_user.hashed_password = auth.hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
    return None


@router.post("/me/avatar", response_model=AvatarUploadResponse)
async def upload_my_avatar(file: UploadFile = File(...), db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    # Basic validation
    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        # fall back by content-type
        ext = ".png" if content_type.endswith("png") else ".jpg" if content_type.endswith("jpeg") else ".webp" if content_type.endswith("webp") else ".png"

    avatars_dir = Path("static") / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)

    ts = int(datetime.now().timestamp())
    filename = f"u_{current_user.id}_{ts}{ext}"
    dest_path = avatars_dir / filename

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    dest_path.write_bytes(data)

    avatar_url = f"https://api.learnpathly.com/static/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return AvatarUploadResponse(avatar_url=avatar_url)




# 新增：获取所有用户（需要权限）
@router.get("/", response_model=List[UserWithRoles])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["user.read"]))
):
    """获取用户列表（需要权限：user.read）"""
    users = UserCURD.get_users(db, skip=skip, limit=limit)
    if active_only:
        users = [user for user in users if user.is_active]
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db_dep)):
    db_user = UserCURD.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# 新增：更新用户状态（需要权限）
@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker(["user.update"]))
):
    """更新用户状态（需要权限：user.update）"""
    # 不能禁用自己
    if user_id == current_user.id and not is_active:
        raise HTTPException(status_code=400, detail="不能禁用自己")
    
    user = UserCURD.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能修改超级管理员
    if user.is_superuser and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="不能修改超级管理员")
    
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    
    action = "启用" if is_active else "禁用"
    return {"message": f"用户{action}成功"}

# 新增：设置超级管理员（需要超级管理员权限）
@router.patch("/{user_id}/superuser")
async def set_superuser(
    user_id: int,
    is_superuser: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: get_current_user)
):
    """设置用户为超级管理员（需要自己是超级管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")
    
    user = UserCURD.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能取消自己的超级管理员权限
    if user_id == current_user.id and not is_superuser:
        raise HTTPException(status_code=400, detail="不能取消自己的超级管理员权限")
    
    user.is_superuser = is_superuser
    db.commit()
    db.refresh(user)
    
    action = "设置为" if is_superuser else "取消"
    return {"message": f"用户{action}超级管理员成功"}