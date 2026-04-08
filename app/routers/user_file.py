from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from urllib.parse import urlparse, unquote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_dep
from app.models.user_file import UserFile
from app.schemas.user_file import UserFileResponse, UserFileUpdateRequest


router = APIRouter(prefix="/user-files", tags=["user-files"])


def _infer_file_type(filename: str, content_type: str | None) -> str:
    ext = os.path.splitext(filename or "")[1].lower()
    if ext == ".md":
        return "md"
    if ext == ".txt":
        return "txt"

    ct = (content_type or "").lower()
    if ct in {"text/markdown", "text/x-markdown"}:
        return "md"
    if ct == "text/plain":
        return "txt"

    return ""


@router.get("/me", response_model=list[UserFileResponse])
def list_my_files(db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    rows = (
        db.query(UserFile)
        .filter(UserFile.user_id == current_user.id)
        .order_by(UserFile.created_at.desc())
        .all()
    )
    return rows


@router.post("/me/upload", response_model=UserFileResponse)
async def upload_my_file(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    content_type = (file.content_type or "").lower()
    file_type = _infer_file_type(file.filename or "", content_type)
    if file_type not in {"md", "txt"}:
        raise HTTPException(status_code=400, detail="Only .md and .txt uploads are supported")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        content_text = data.decode("utf-8")
    except Exception:
        # Fall back gracefully; keeps API usable even if users upload non-utf8 text.
        content_text = data.decode("utf-8", errors="replace")

    files_dir = Path("static") / "user_files"
    files_dir.mkdir(parents=True, exist_ok=True)

    ts = int(datetime.now().timestamp())
    safe_ext = ".md" if file_type == "md" else ".txt"
    filename = f"file_{current_user.id}_{ts}{safe_ext}"
    dest_path = files_dir / filename
    dest_path.write_bytes(data)

    file_url = f"http://localhost:8000/static/user_files/{filename}"

    row = UserFile(
        user_id=current_user.id,
        title=(title or "").strip() or None,
        file_type=file_type,
        original_filename=(file.filename or "").strip() or None,
        content_type=content_type or None,
        size_bytes=len(data),
        content=content_text,
        file_url=file_url,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return row


@router.delete("/me/{file_id}", status_code=204)
def delete_my_file(
    file_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    row = (
        db.query(UserFile)
        .filter(UserFile.id == file_id, UserFile.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="file not found")

    # Best-effort delete the underlying static file.
    try:
        parsed = urlparse(row.file_url or "")
        filename = Path(unquote(parsed.path or "")).name
        if filename:
            files_dir = Path("static") / "user_files"
            target = (files_dir / filename).resolve()
            base = files_dir.resolve()
            if str(target).startswith(str(base)) and target.exists() and target.is_file():
                target.unlink()
    except Exception:
        # Ignore file system errors; DB row deletion is authoritative.
        pass

    db.delete(row)
    db.commit()
    return None


@router.put("/me/{file_id}", response_model=UserFileResponse)
def update_my_file(
    file_id: int,
    payload: UserFileUpdateRequest,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    row = (
        db.query(UserFile)
        .filter(UserFile.id == file_id, UserFile.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="file not found")

    if payload.title is not None:
        row.title = payload.title.strip() or None

    if payload.content is not None:
        row.content = payload.content
        try:
            data = payload.content.encode("utf-8")
            row.size_bytes = len(data)
        except Exception:
            row.size_bytes = None

        try:
            parsed = urlparse(row.file_url or "")
            filename = Path(unquote(parsed.path or "")).name
            if filename:
                files_dir = Path("static") / "user_files"
                target = (files_dir / filename).resolve()
                base = files_dir.resolve()
                if str(target).startswith(str(base)):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
        except Exception:
            pass

    db.add(row)
    db.commit()
    db.refresh(row)
    return row
