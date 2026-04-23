from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user_optional, get_current_user
from app.core.deps import get_db_dep
from app.models.category import Category
from app.models.rbac.user import User
from app.api.category.schemas import CategoryCreate, CategoryResponse


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db_dep),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    # Public endpoint: if not authenticated, return only system categories
    # If authenticated, return system categories + user's own categories
    if current_user is None:
        return (
            db.query(Category)
            .filter(Category.is_system.is_(True))
            .order_by(Category.is_system.desc(), Category.id.asc())
            .all()
        )
    return (
        db.query(Category)
        .filter(
            (Category.is_system.is_(True)) | (Category.owner_user_id == current_user.id)
        )
        .order_by(Category.is_system.desc(), Category.id.asc())
        .all()
    )


@router.post("/", response_model=CategoryResponse)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    # Generate code with user prefix to avoid conflicts with system categories
    # User's "AI" → code: u1_ai, System's "AI" → code: ai
    raw_code = (payload.code or "").strip().lower()
    if not raw_code:
        raw_code = name.lower().replace(" ", "_").replace("-", "_")
    # Remove any existing prefix if user provides custom code
    if raw_code.startswith("u") and "_" in raw_code:
        raw_code = raw_code.split("_", 1)[1]
    code = f"u{current_user.id}_{raw_code}"

    exists = db.query(Category).filter(Category.code == code).first()
    if exists:
        raise HTTPException(status_code=409, detail="Category code already exists")

    obj = Category(
        name=name,
        code=code,
        description=payload.description,
        is_system=False,
        owner_user_id=current_user.id,
        level=0,
        is_leaf=True,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
