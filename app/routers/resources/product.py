from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.curd.resources.product_curd import ProductCURD

from app.schemas.resources.product import ProductCreate, ProductResponse
from app.core.deps import get_db_dep
from typing import List

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db_dep)):
    product = ProductCURD.create_product(db,product_in)
    # user = curd.user.create_user(db, username=user_in.username, email=user_in.email, password=hashed) 作比较
    return product

@router.get("/", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_dep)):
    products = ProductCURD.list_products(db, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db_dep)):
    db_product = ProductCURD.get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

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

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db_dep)):
    product = ProductCURD.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    ProductCURD.delete_product(db, product)
    return None