from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.curd.resources.doc_curd import DocCURD

# from app.schemas.product import ProductCreate, ProductResponse
from app.schemas.resources.doc import DocCreate, DocResponse
from app.core.deps import get_db_dep
from typing import List

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/", response_model=DocResponse, status_code=status.HTTP_201_CREATED)
def create_doc(doc_in: DocCreate, db: Session = Depends(get_db_dep)):
    doc = DocCURD.create_doc(db,doc_in)
    # user = curd.user.create_user(db, username=user_in.username, email=user_in.email, password=hashed) 作比较
    return doc

@router.get("/", response_model=List[DocResponse])
def read_docs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_dep)):
    docs = DocCURD.list_docs(db, skip=skip, limit=limit)
    return docs


@router.get("/{doc_id}", response_model=DocResponse)
def read_doc(doc_id: int, db: Session = Depends(get_db_dep)):
    db_doc = DocCURD.get_doc(db, doc_id)
    if not db_doc:
        raise HTTPException(status_code=404, detail="doc not found")
    return db_doc

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

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doc(doc_id: int, db: Session = Depends(get_db_dep)):
    doc = DocCURD.get_doc(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="doc not found")
    DocCURD.delete_doc(db, doc)
    return None