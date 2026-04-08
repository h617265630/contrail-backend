from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import os

from app.core.deps import get_current_user, get_db_dep
from app.models.user_image import UserImage
from app.schemas.user_image import UserImageResponse


router = APIRouter(prefix="/user-images", tags=["user-images"])


@router.get("/me", response_model=list[UserImageResponse])
def list_my_images(db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    rows = (
        db.query(UserImage)
        .filter(UserImage.user_id == current_user.id)
        .order_by(UserImage.created_at.desc())
        .all()
    )
    return rows


@router.post("/me/upload", response_model=UserImageResponse)
async def upload_my_image(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    content_type = (file.content_type or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        ext = ".png" if content_type.endswith("png") else ".jpg" if content_type.endswith("jpeg") else ".webp" if content_type.endswith("webp") else ".png"

    images_dir = Path("static") / "user_images"
    images_dir.mkdir(parents=True, exist_ok=True)

    ts = int(datetime.now().timestamp())
    filename = f"img_{current_user.id}_{ts}{ext}"
    dest_path = images_dir / filename

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    dest_path.write_bytes(data)

    image_url = f"http://localhost:8000/static/user_images/{filename}"

    row = UserImage(
        user_id=current_user.id,
        title=(title or "").strip() or None,
        image_url=image_url,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return row
