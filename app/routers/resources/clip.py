from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.curd.resources.clip_curd import ClipCURD

from app.schemas.resources.clip import ClipResponse,ClipCreate
from app.core.deps import get_db_dep,get_current_user
from typing import List

router = APIRouter(prefix="/clips", tags=["Clips"])

@router.post("/", response_model=ClipResponse, status_code=status.HTTP_201_CREATED)
def create_clip(clip_in: ClipCreate, db: Session = Depends(get_db_dep)):
    clip = ClipCURD.create_clip(db,clip_in)

    # user = curd.user.create_user(db, username=user_in.username, email=user_in.email, password=hashed) 作比较
    return clip

@router.get("/", response_model=List[ClipResponse])
def read_clips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_dep)):
    clips = ClipCURD.get_clips_by_videoId(db, skip=skip, limit=limit)
    return clips


@router.get("/{clip_id}", response_model=ClipResponse)
def read_clip(clip_id: int, db: Session = Depends(get_db_dep)):
    db_clip = ClipCURD.get_clip(db, clip_id)
    if not db_clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return db_clip
# 暂时没有这个功能
# @router.put("/{video_id}", response_model=schemas.video.VideoResponse)
# def update_video(video_id: str, video_in: VideoUpdate, db: Session = Depends(get_db_dep), current_user: User = Depends(get_current_user)):
#     video = VideoCRUD.get_video(db, video_id)
#     if not video:
#         raise HTTPException(status_code=404, detail="Video not found")
#     if video.owner_id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not authorized to update this video")
    
#     updated_video = VideoCRUD.update_video(db, video, video_in)
#     return updated_video

@router.delete("/{clip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clip(clip_id: int, db: Session = Depends(get_db_dep), current_user = Depends(get_current_user)):
    clip = ClipCURD.get_clip(db, clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    if clip.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this clip")
    
    ClipCURD.delete_clip(db, clip)
    return None

# /random
# /sequential
#/id/like
#/id/note
#/id/notes
