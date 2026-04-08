from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_dep
from app.curd.resources.video_curd import VideoCURD
from app.curd.watch_history_curd import WatchHistoryCURD
from app.schemas.resources.video import VideoCategoryAssign, VideoCreate, VideoResponse
from app.schemas.watch_history import WatchHistoryCreate, WatchHistoryResponse

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
def create_video(video_in: VideoCreate, db: Session = Depends(get_db_dep), current_user = Depends(get_current_user)):
    video = VideoCURD.create_video(db,video_in,owner_id=current_user.id)

    # user = curd.user.create_user(db, username=user_in.username, email=user_in.email, password=hashed) 作比较
    return video

@router.get("/", response_model=List[VideoResponse])
def read_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_dep)):
    videos = VideoCURD.get_videos(db, skip=skip, limit=limit)
    return videos


@router.get("/{video_id}", response_model=VideoResponse)
def read_video(video_id: int, db: Session = Depends(get_db_dep)):
    db_video = VideoCURD.get_video(db, video_id)
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

 

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(video_id: int, db: Session = Depends(get_db_dep), current_user = Depends(get_current_user)):
    video = VideoCURD.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this video")
    
    VideoCURD.delete_video(db, video)
    return None

# ============ 分类管理 ============
@router.post("/{video_id}/categories/{category_id}")
def add_video_category(video_id: int, category_id: int, db: Session = Depends(get_db_dep), current_user = Depends(get_current_user)):
    try:
        video = VideoCURD.add_category_to_video(db, video_id, category_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "分类已添加", "video_id": video_id, "category_id": category_id}

@router.delete("/{video_id}/categories/{category_id}")
def remove_video_category(video_id: int, category_id: int, db: Session = Depends(get_db_dep), current_user = Depends(get_current_user)):
    try:
        video = VideoCURD.remove_category_from_video(db, video_id, category_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "分类已移除", "video_id": video_id, "category_id": category_id}

@router.post("/{video_id}/categories")
def assign_video_categories(video_id: int, data: VideoCategoryAssign, db: Session = Depends(get_db_dep), current_user = Depends(get_current_user)):
    try:
        video = VideoCURD.assign_categories_to_video(db, video_id, data.category_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "分类已更新", "video_id": video_id, "category_ids": data.category_ids}

# ============ 观看记录 ============
@router.post("/{video_id}/watch", response_model=WatchHistoryResponse)
def record_watch(
    video_id: int,
    data: WatchHistoryCreate,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    try:
        record = WatchHistoryCURD.record_watch(
            db,
            user_id=current_user.id,
            video_id=video_id,
            is_watched=data.is_watched,
            watch_time=data.watch_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return record

@router.get("/{video_id}/watch/count")
def get_watch_count(video_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    count = WatchHistoryCURD.get_video_watch_count(db, video_id)
    return {"video_id": video_id, "watch_count": count}