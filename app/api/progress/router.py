from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_dep
from app.curd.progress_curd import ProgressCURD
from app.api.progress.schemas import ProgressResponse, ProgressUpsertRequest


router = APIRouter(prefix="/progress", tags=["progress"])


def _ensure_user_owns_learning_path(
    db: Session, *, user_id: int, learning_path_id: int
) -> None:
    if not ProgressCURD.check_user_owns_learning_path(
        db, user_id=user_id, learning_path_id=learning_path_id
    ):
        raise HTTPException(
            status_code=403, detail="No permission for this learning path"
        )


def _ensure_user_owns_path_item(
    db: Session, *, user_id: int, path_item_id: int
) -> None:
    item = ProgressCURD.get_path_item(db, path_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="PathItem not found")
    _ensure_user_owns_learning_path(
        db, user_id=user_id, learning_path_id=item.learning_path_id
    )


@router.get("/me", response_model=List[ProgressResponse])
def list_my_progress(
    learning_path_id: int = Query(..., ge=1),
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    _ensure_user_owns_learning_path(
        db, user_id=current_user.id, learning_path_id=learning_path_id
    )

    path_item_ids = ProgressCURD.list_path_item_ids(db, learning_path_id)

    rows = ProgressCURD.list_for_items(
        db, user_id=current_user.id, path_item_ids=path_item_ids
    )
    by_item = {int(r.path_item_id): r for r in rows}

    # Return a row for each path item, defaulting to 0.
    out: List[ProgressResponse] = []
    for pid in path_item_ids:
        hit = by_item.get(int(pid))
        out.append(
            ProgressResponse(
                path_item_id=int(pid),
                progress_percentage=int(getattr(hit, "progress_percentage", 0) or 0),
                last_watched_time=getattr(hit, "last_watched_time", None),
            )
        )
    return out


@router.get("/me/item/{path_item_id}", response_model=ProgressResponse)
def get_my_progress_for_item(
    path_item_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    _ensure_user_owns_path_item(db, user_id=current_user.id, path_item_id=path_item_id)

    hit = ProgressCURD.get_for_item(
        db, user_id=current_user.id, path_item_id=path_item_id
    )
    return ProgressResponse(
        path_item_id=path_item_id,
        progress_percentage=int(getattr(hit, "progress_percentage", 0) or 0),
        last_watched_time=getattr(hit, "last_watched_time", None),
    )


@router.put("/me", response_model=ProgressResponse)
def upsert_my_progress(
    payload: ProgressUpsertRequest,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    _ensure_user_owns_path_item(
        db, user_id=current_user.id, path_item_id=payload.path_item_id
    )

    try:
        obj = ProgressCURD.upsert(
            db,
            user_id=current_user.id,
            path_item_id=payload.path_item_id,
            progress_percentage=payload.progress_percentage,
        )
        db.commit()
        db.refresh(obj)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败: {e}")

    return ProgressResponse(
        path_item_id=int(obj.path_item_id),
        progress_percentage=int(obj.progress_percentage or 0),
        last_watched_time=getattr(obj, "last_watched_time", None),
    )
