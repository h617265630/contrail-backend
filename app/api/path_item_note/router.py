from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_dep
from app.curd.path_item_note_curd import PathItemNoteCURD
from app.curd.progress_curd import ProgressCURD
from app.api.path_item_note.schemas import NoteUpsertRequest, NoteResponse

router = APIRouter(prefix="/path-item-notes", tags=["path-item-notes"])


def _ensure_user_owns_path_item(
    db: Session, *, user_id: int, path_item_id: int
) -> None:
    item = PathItemNoteCURD.get_path_item(db, path_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="PathItem not found")
    if not PathItemNoteCURD.check_user_owns_learning_path(
        db, user_id=user_id, learning_path_id=item.learning_path_id
    ):
        raise HTTPException(
            status_code=403, detail="No permission for this learning path"
        )


@router.get("/me", response_model=List[NoteResponse])
def list_my_notes(
    learning_path_id: int = Query(..., ge=1),
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    if not PathItemNoteCURD.check_user_owns_learning_path(
        db, user_id=current_user.id, learning_path_id=learning_path_id
    ):
        raise HTTPException(
            status_code=403, detail="No permission for this learning path"
        )

    path_item_ids = PathItemNoteCURD.list_path_item_ids(db, learning_path_id)
    rows = PathItemNoteCURD.list_for_items(
        db, user_id=current_user.id, path_item_ids=path_item_ids
    )
    by_item = {int(r.path_item_id): r for r in rows}

    out: List[NoteResponse] = []
    for pid in path_item_ids:
        hit = by_item.get(int(pid))
        out.append(
            NoteResponse(
                path_item_id=int(pid),
                notes=getattr(hit, "notes", "") or "",
                updated_at=getattr(hit, "updated_at", None),
            )
        )
    return out


@router.put("/me", response_model=NoteResponse)
def upsert_my_note(
    payload: NoteUpsertRequest,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    _ensure_user_owns_path_item(
        db, user_id=current_user.id, path_item_id=payload.path_item_id
    )

    obj = PathItemNoteCURD.upsert(
        db,
        user_id=current_user.id,
        path_item_id=payload.path_item_id,
        notes=payload.notes,
    )
    db.commit()
    db.refresh(obj)

    return NoteResponse(
        path_item_id=int(obj.path_item_id),
        notes=obj.notes or "",
        updated_at=obj.updated_at,
    )


@router.delete("/me/{path_item_id}", status_code=204)
def delete_my_note(
    path_item_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    _ensure_user_owns_path_item(
        db, user_id=current_user.id, path_item_id=path_item_id
    )

    PathItemNoteCURD.delete(
        db, user_id=current_user.id, path_item_id=path_item_id
    )
    db.commit()
