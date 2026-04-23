from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db_dep
from app.curd.resources.resource_curd import ResourceCURD
from ai_path.ai_resource import search_github, search_youtube
from app.models.resource import Resource
from app.models.user_resource import UserResource
from app.models.resources.video import Video
from app.models.resources.doc import Doc
from app.models.resources.article import Article
from app.models.path_item import PathItem
from app.schemas.resources.extract import ChapterItem, UrlExtractRequest, UrlExtractResponse
from app.schemas.resources.resource import (
    ArticleInfo,
    DocInfo,
    ResourceAttachResponse,
    ResourceCreateFromUrl,
    ResourceDetailResponse,
    ResourceResponse,
    ResourceUpdateRequest,
    VideoInfo,
)

router = APIRouter(prefix="/resources", tags=["Resources"])


def _resource_type_value(obj: Resource) -> str:
    rt = getattr(obj, "resource_type", None)
    return (rt.value if hasattr(rt, "value") else str(rt or "")).strip().lower()


@router.post("/extract", response_model=UrlExtractResponse)
def extract_from_url(payload: UrlExtractRequest):
    try:
        meta = ResourceCURD.extract_from_url(str(payload.url))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析失败: {e}")

    return UrlExtractResponse(
        title=meta["title"],
        description=meta.get("description"),
        thumbnail_url=meta.get("thumbnail_url"),
        author=meta.get("author"),
        publish_date=meta.get("publish_date"),
        video_id=meta.get("video_id"),
        duration_seconds=meta.get("duration_seconds"),
        platform=meta.get("platform"),
        chapters=[ChapterItem(**c) for c in (meta.get("chapters") or [])],
    )


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    obj = db.query(Resource).filter(Resource.id == resource_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="resource not found")

    try:
        db.query(Video).filter(Video.resource_id == resource_id).delete(synchronize_session=False)
        db.query(Doc).filter(Doc.resource_id == resource_id).delete(synchronize_session=False)
        db.query(Article).filter(Article.resource_id == resource_id).delete(synchronize_session=False)
        db.query(UserResource).filter(UserResource.resource_id == resource_id).delete(synchronize_session=False)
        db.query(PathItem).filter(PathItem.resource_id == resource_id).delete(synchronize_session=False)
        db.delete(obj)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除失败: {e}")

    return None


@router.get("/me/{resource_id}", response_model=ResourceDetailResponse)
def get_my_resource_detail(resource_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    assoc = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == resource_id)
        .first()
    )
    if not assoc:
        raise HTTPException(status_code=404, detail="resource not found")

    obj = (
        db.query(Resource)
        .options(joinedload(Resource.category))
        .filter(Resource.id == resource_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="resource not found")

    # Engagement tracking
    try:
        assoc.last_opened = datetime.now()
        assoc.open_count = int(getattr(assoc, "open_count", 0) or 0) + 1
        db.commit()
        db.refresh(assoc)
    except Exception:
        db.rollback()

    return ResourceDetailResponse(
        id=obj.id,
        resource_type=_resource_type_value(obj),
        platform=getattr(obj, "platform", None),
        title=obj.title,
        summary=getattr(obj, "summary", None),
        source_url=getattr(obj, "source_url", None),
        thumbnail=getattr(obj, "thumbnail", None),
        category_id=getattr(obj, "category_id", None),
        difficulty=getattr(obj, "difficulty", None),
        tags=getattr(obj, "tags", None),
        raw_meta=getattr(obj, "raw_meta", None),
        category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
        manual_weight=getattr(assoc, "manual_weight", None),
        behavior_weight=getattr(assoc, "behavior_weight", None),
        effective_weight=getattr(assoc, "effective_weight", None),
        added_at=getattr(assoc, "added_at", None),
        last_opened=getattr(assoc, "last_opened", None),
        open_count=getattr(assoc, "open_count", None),
        completion_status=getattr(assoc, "completion_status", None),
        community_score=getattr(obj, "community_score", None),
        save_count=getattr(obj, "save_count", None),
        trending_score=getattr(obj, "trending_score", None),
        created_at=getattr(obj, "created_at", None),
        video=VideoInfo.model_validate(obj.video) if getattr(obj, "video", None) else None,
        doc=DocInfo.model_validate(obj.doc) if getattr(obj, "doc", None) else None,
        article=ArticleInfo.model_validate(obj.article) if getattr(obj, "article", None) else None,
    )


@router.get("/me", response_model=list[ResourceResponse])
def list_my_resources(db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    items = (
        db.query(Resource, UserResource)
        .join(UserResource, UserResource.resource_id == Resource.id)
        .options(joinedload(Resource.category))  # Eagerly load category to get category_name
        .filter(UserResource.user_id == current_user.id)
        .order_by(Resource.id.desc())
        .all()
    )
    # Sort by added_at to assign user_seq (1 = first added)
    sorted_items = sorted(items, key=lambda pair: (getattr(pair[1], "added_at", None) or getattr(pair[0], "created_at", None) or ""))
    seq_map: dict[int, int] = {}
    for seq, (r, _ur) in enumerate(sorted_items, start=1):
        seq_map[r.id] = seq
    return [
        ResourceResponse(
            id=r.id,
            resource_type=_resource_type_value(r),
            platform=getattr(r, "platform", None),
            title=r.title,
            summary=getattr(r, "summary", None),
            source_url=getattr(r, "source_url", None),
            thumbnail=getattr(r, "thumbnail", None),
            category_id=getattr(r, "category_id", None),
            category_name=getattr(r.category, "name", None) if getattr(r, "category", None) else None,
            difficulty=getattr(r, "difficulty", None),
            tags=getattr(r, "tags", None),
            raw_meta=getattr(r, "raw_meta", None),
            manual_weight=getattr(ur, "manual_weight", None),
            behavior_weight=getattr(ur, "behavior_weight", None),
            effective_weight=getattr(ur, "effective_weight", None),
            added_at=getattr(ur, "added_at", None),
            last_opened=getattr(ur, "last_opened", None),
            open_count=getattr(ur, "open_count", None),
            completion_status=getattr(ur, "completion_status", None),
            community_score=getattr(r, "community_score", None),
            save_count=getattr(r, "save_count", None),
            trending_score=getattr(r, "trending_score", None),
            created_at=getattr(r, "created_at", None),
            user_seq=seq_map.get(r.id),
        )
        for r, ur in items
    ]


@router.get("", response_model=list[ResourceResponse])
def list_resources(db: Session = Depends(get_db_dep)):
    items = ResourceCURD.list_all(db)
    return [
        ResourceResponse(
            id=r.id,
            resource_type=_resource_type_value(r),
            platform=getattr(r, "platform", None),
            title=r.title,
            summary=getattr(r, "summary", None),
            source_url=getattr(r, "source_url", None),
            thumbnail=getattr(r, "thumbnail", None),
            category_id=getattr(r, "category_id", None),
            category_name=getattr(r.category, "name", None) if getattr(r, "category", None) else None,
            difficulty=getattr(r, "difficulty", None),
            tags=getattr(r, "tags", None),
            raw_meta=getattr(r, "raw_meta", None),
            community_score=getattr(r, "community_score", None),
            save_count=getattr(r, "save_count", None),
            trending_score=getattr(r, "trending_score", None),
            created_at=getattr(r, "created_at", None),
        )
        for r in items
    ]

class SearchResultItem(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    source_score: Optional[float] = None
    type: Optional[str] = None
    thumbnail: Optional[str] = None


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    platform: str


@router.get("/search", response_model=SearchResponse)
def search_resources(
    q: str = Query(..., min_length=1, description="Search keyword"),
    platform: str = Query("github", description="Platform: github, youtube, or all"),
):
    q = q.strip()
    results: list[dict] = []
    if platform in ("github", "all"):
        results.extend(search_github(q))
    if platform in ("youtube", "all"):
        results.extend(search_youtube(q))
    return SearchResponse(
        results=[
            SearchResultItem(
                title=r.get("title", ""),
                url=r.get("url", ""),
                description=r.get("description"),
                source_score=r.get("source_score"),
                type=r.get("type"),
                thumbnail=r.get("thumbnail"),
            )
            for r in results
        ],
        platform=platform,
    )


@router.get("/{resource_id}", response_model=ResourceDetailResponse)
def get_resource_detail(resource_id: int, db: Session = Depends(get_db_dep)):
    obj = (
        db.query(Resource)
        .options(joinedload(Resource.category))
        .filter(Resource.id == resource_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="resource not found")

    return ResourceDetailResponse(
        id=obj.id,
        resource_type=_resource_type_value(obj),
        platform=getattr(obj, "platform", None),
        title=obj.title,
        summary=getattr(obj, "summary", None),
        source_url=getattr(obj, "source_url", None),
        thumbnail=getattr(obj, "thumbnail", None),
        category_id=getattr(obj, "category_id", None),
        category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
        difficulty=getattr(obj, "difficulty", None),
        tags=getattr(obj, "tags", None),
        raw_meta=getattr(obj, "raw_meta", None),
        created_at=getattr(obj, "created_at", None),
        video=VideoInfo.model_validate(obj.video) if getattr(obj, "video", None) else None,
        doc=DocInfo.model_validate(obj.doc) if getattr(obj, "doc", None) else None,
        article=ArticleInfo.model_validate(obj.article) if getattr(obj, "article", None) else None,
    )


@router.post("/me", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_my_resource(payload: ResourceCreateFromUrl, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    try:
        obj = ResourceCURD.create_from_url(
            db,
            user_id=current_user.id,
            url=str(payload.url),
            category_id=payload.category_id,
            is_system_public=False,
            is_public=payload.is_public,
            manual_weight=payload.manual_weight,
        )
        db.commit()
        db.refresh(obj)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建失败: {e}")

    assoc = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == obj.id)
        .first()
    )

    # Re-fetch obj with category for response
    obj = (
        db.query(Resource)
        .options(joinedload(Resource.category))
        .filter(Resource.id == obj.id)
        .first()
    )

    return ResourceResponse(
        id=obj.id,
        resource_type=_resource_type_value(obj),
        platform=getattr(obj, "platform", None),
        title=obj.title,
        summary=getattr(obj, "summary", None),
        source_url=getattr(obj, "source_url", None),
        thumbnail=getattr(obj, "thumbnail", None),
        category_id=getattr(obj, "category_id", None),
        category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
        difficulty=getattr(obj, "difficulty", None),
        tags=getattr(obj, "tags", None),
        raw_meta=getattr(obj, "raw_meta", None),
        manual_weight=getattr(assoc, "manual_weight", None) if assoc else None,
        behavior_weight=getattr(assoc, "behavior_weight", None) if assoc else None,
        effective_weight=getattr(assoc, "effective_weight", None) if assoc else None,
        added_at=getattr(assoc, "added_at", None) if assoc else None,
        last_opened=getattr(assoc, "last_opened", None) if assoc else None,
        open_count=getattr(assoc, "open_count", None) if assoc else None,
        completion_status=getattr(assoc, "completion_status", None) if assoc else None,
        community_score=getattr(obj, "community_score", None),
        save_count=getattr(obj, "save_count", None),
        trending_score=getattr(obj, "trending_score", None),
        created_at=getattr(obj, "created_at", None),
    )


@router.post("/me/{resource_id}", response_model=ResourceResponse)
def add_public_resource_to_my_resources(
    resource_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    obj = db.query(Resource).filter(Resource.id == resource_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="resource not found")

    try:
        ResourceCURD.attach_to_user(db, user_id=current_user.id, resource_id=obj.id)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"添加失败: {e}")

    assoc = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == obj.id)
        .first()
    )

    # Re-fetch obj with category for response
    obj = (
        db.query(Resource)
        .options(joinedload(Resource.category))
        .filter(Resource.id == obj.id)
        .first()
    )

    return ResourceResponse(
        id=obj.id,
        resource_type=_resource_type_value(obj),
        platform=getattr(obj, "platform", None),
        title=obj.title,
        summary=getattr(obj, "summary", None),
        source_url=getattr(obj, "source_url", None),
        thumbnail=getattr(obj, "thumbnail", None),
        category_id=getattr(obj, "category_id", None),
        category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
        difficulty=getattr(obj, "difficulty", None),
        tags=getattr(obj, "tags", None),
        raw_meta=getattr(obj, "raw_meta", None),
        manual_weight=getattr(assoc, "manual_weight", None) if assoc else None,
        behavior_weight=getattr(assoc, "behavior_weight", None) if assoc else None,
        effective_weight=getattr(assoc, "effective_weight", None) if assoc else None,
        added_at=getattr(assoc, "added_at", None) if assoc else None,
        last_opened=getattr(assoc, "last_opened", None) if assoc else None,
        open_count=getattr(assoc, "open_count", None) if assoc else None,
        completion_status=getattr(assoc, "completion_status", None) if assoc else None,
        community_score=getattr(obj, "community_score", None),
        save_count=getattr(obj, "save_count", None),
        trending_score=getattr(obj, "trending_score", None),
        created_at=getattr(obj, "created_at", None),
    )


class AttachPayload(BaseModel):
    manual_weight: Optional[int] = None


@router.post("/me/{resource_id}/attach", response_model=ResourceAttachResponse)
def add_public_resource_to_my_resources_with_status(
    resource_id: int,
    payload: AttachPayload = Body(default=AttachPayload()),
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    obj = db.query(Resource).filter(Resource.id == resource_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="resource not found")

    already_exists = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == obj.id)
        .first()
        is not None
    )

    try:
        ResourceCURD.attach_to_user_with_weight(
            db,
            user_id=current_user.id,
            resource_id=obj.id,
            manual_weight=payload.manual_weight,
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"添加失败: {e}")

    return ResourceAttachResponse(
        already_exists=already_exists,
        resource=ResourceResponse(
            id=obj.id,
            resource_type=_resource_type_value(obj),
            platform=getattr(obj, "platform", None),
            title=obj.title,
            summary=getattr(obj, "summary", None),
            source_url=getattr(obj, "source_url", None),
            thumbnail=getattr(obj, "thumbnail", None),
            category_id=getattr(obj, "category_id", None),
            category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
            difficulty=getattr(obj, "difficulty", None),
            tags=getattr(obj, "tags", None),
            raw_meta=getattr(obj, "raw_meta", None),
            created_at=getattr(obj, "created_at", None),
        ),
    )


@router.delete("/me/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_resource(resource_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    try:
        ResourceCURD.detach_from_user(db, user_id=current_user.id, resource_id=resource_id)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除失败: {e}")

    return None


@router.patch("/me/{resource_id}", response_model=ResourceResponse)
def update_my_resource(
    resource_id: int,
    payload: ResourceUpdateRequest,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    try:
        obj = ResourceCURD.update_for_user(
            db,
            user_id=current_user.id,
            resource_id=resource_id,
            title=payload.title,
            summary=payload.summary,
            platform=payload.platform,
            thumbnail=payload.thumbnail,
            category_id=getattr(payload, "category_id", None),
            difficulty=payload.difficulty,
            tags=payload.tags,
            raw_meta=payload.raw_meta,
        )

        assoc = (
            db.query(UserResource)
            .filter(UserResource.user_id == current_user.id, UserResource.resource_id == resource_id)
            .first()
        )
        if not assoc:
            raise ValueError("user_resource association not found")

        if payload.manual_weight is not None:
            assoc.manual_weight = int(payload.manual_weight)
            assoc.effective_weight = int(payload.manual_weight)

        db.commit()
        db.refresh(obj)
        db.refresh(assoc)
    except ValueError as e:
        db.rollback()
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "association not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败: {e}")

    assoc = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == resource_id)
        .first()
    )

    # Re-fetch obj with category for response
    obj = (
        db.query(Resource)
        .options(joinedload(Resource.category))
        .filter(Resource.id == resource_id)
        .first()
    )

    return ResourceResponse(
        id=obj.id,
        resource_type=_resource_type_value(obj),
        platform=getattr(obj, "platform", None),
        title=obj.title,
        summary=getattr(obj, "summary", None),
        source_url=getattr(obj, "source_url", None),
        thumbnail=getattr(obj, "thumbnail", None),
        category_id=getattr(obj, "category_id", None),
        category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
        difficulty=getattr(obj, "difficulty", None),
        tags=getattr(obj, "tags", None),
        raw_meta=getattr(obj, "raw_meta", None),
        manual_weight=getattr(assoc, "manual_weight", None) if assoc else None,
        behavior_weight=getattr(assoc, "behavior_weight", None) if assoc else None,
        effective_weight=getattr(assoc, "effective_weight", None) if assoc else None,
        added_at=getattr(assoc, "added_at", None) if assoc else None,
        last_opened=getattr(assoc, "last_opened", None) if assoc else None,
        open_count=getattr(assoc, "open_count", None) if assoc else None,
        completion_status=getattr(assoc, "completion_status", None) if assoc else None,
        community_score=getattr(obj, "community_score", None),
        save_count=getattr(obj, "save_count", None),
        trending_score=getattr(obj, "trending_score", None),
        created_at=getattr(obj, "created_at", None),
    )


@router.post("/me", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_my_resource(payload: ResourceCreateFromUrl, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    try:
        obj = ResourceCURD.create_from_url(
            db,
            user_id=current_user.id,
            url=str(payload.url),
            category_id=payload.category_id,
            is_system_public=False,
            is_public=payload.is_public,
            manual_weight=payload.manual_weight,
        )
        db.commit()
        db.refresh(obj)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建失败: {e}")

    assoc = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == obj.id)
        .first()
    )

    # Re-fetch obj with category for response
    obj = (
        db.query(Resource)
        .options(joinedload(Resource.category))
        .filter(Resource.id == obj.id)
        .first()
    )

    return ResourceResponse(
        id=obj.id,
        resource_type=_resource_type_value(obj),
        platform=getattr(obj, "platform", None),
        title=obj.title,
        summary=getattr(obj, "summary", None),
        source_url=getattr(obj, "source_url", None),
        thumbnail=getattr(obj, "thumbnail", None),
        category_id=getattr(obj, "category_id", None),
        category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
        difficulty=getattr(obj, "difficulty", None),
        tags=getattr(obj, "tags", None),
        raw_meta=getattr(obj, "raw_meta", None),
        manual_weight=getattr(assoc, "manual_weight", None) if assoc else None,
        behavior_weight=getattr(assoc, "behavior_weight", None) if assoc else None,
        effective_weight=getattr(assoc, "effective_weight", None) if assoc else None,
        added_at=getattr(assoc, "added_at", None) if assoc else None,
        last_opened=getattr(assoc, "last_opened", None) if assoc else None,
        open_count=getattr(assoc, "open_count", None) if assoc else None,
        completion_status=getattr(assoc, "completion_status", None) if assoc else None,
        community_score=getattr(obj, "community_score", None),
        save_count=getattr(obj, "save_count", None),
        trending_score=getattr(obj, "trending_score", None),
        created_at=getattr(obj, "created_at", None),
    )


@router.post("/me/{resource_id}", response_model=ResourceResponse)
def add_public_resource_to_my_resources(
    resource_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    obj = db.query(Resource).filter(Resource.id == resource_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="resource not found")

    try:
        ResourceCURD.attach_to_user(db, user_id=current_user.id, resource_id=obj.id)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"添加失败: {e}")

    assoc = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == obj.id)
        .first()
    )

    # Re-fetch obj with category for response
    obj = (
        db.query(Resource)
        .options(joinedload(Resource.category))
        .filter(Resource.id == obj.id)
        .first()
    )

    return ResourceResponse(
        id=obj.id,
        resource_type=_resource_type_value(obj),
        platform=getattr(obj, "platform", None),
        title=obj.title,
        summary=getattr(obj, "summary", None),
        source_url=getattr(obj, "source_url", None),
        thumbnail=getattr(obj, "thumbnail", None),
        category_id=getattr(obj, "category_id", None),
        category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
        difficulty=getattr(obj, "difficulty", None),
        tags=getattr(obj, "tags", None),
        raw_meta=getattr(obj, "raw_meta", None),
        manual_weight=getattr(assoc, "manual_weight", None) if assoc else None,
        behavior_weight=getattr(assoc, "behavior_weight", None) if assoc else None,
        effective_weight=getattr(assoc, "effective_weight", None) if assoc else None,
        added_at=getattr(assoc, "added_at", None) if assoc else None,
        last_opened=getattr(assoc, "last_opened", None) if assoc else None,
        open_count=getattr(assoc, "open_count", None) if assoc else None,
        completion_status=getattr(assoc, "completion_status", None) if assoc else None,
        community_score=getattr(obj, "community_score", None),
        save_count=getattr(obj, "save_count", None),
        trending_score=getattr(obj, "trending_score", None),
        created_at=getattr(obj, "created_at", None),
    )


class AttachPayload(BaseModel):
    manual_weight: Optional[int] = None


@router.post("/me/{resource_id}/attach", response_model=ResourceAttachResponse)
def add_public_resource_to_my_resources_with_status(
    resource_id: int,
    payload: AttachPayload = Body(default=AttachPayload()),
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    obj = db.query(Resource).filter(Resource.id == resource_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="resource not found")

    already_exists = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == obj.id)
        .first()
        is not None
    )

    try:
        ResourceCURD.attach_to_user_with_weight(
            db,
            user_id=current_user.id,
            resource_id=obj.id,
            manual_weight=payload.manual_weight,
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"添加失败: {e}")

    return ResourceAttachResponse(
        already_exists=already_exists,
        resource=ResourceResponse(
            id=obj.id,
            resource_type=_resource_type_value(obj),
            platform=getattr(obj, "platform", None),
            title=obj.title,
            summary=getattr(obj, "summary", None),
            source_url=getattr(obj, "source_url", None),
            thumbnail=getattr(obj, "thumbnail", None),
            category_id=getattr(obj, "category_id", None),
            category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
            difficulty=getattr(obj, "difficulty", None),
            tags=getattr(obj, "tags", None),
            raw_meta=getattr(obj, "raw_meta", None),
            created_at=getattr(obj, "created_at", None),
        ),
    )


@router.delete("/me/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_resource(resource_id: int, db: Session = Depends(get_db_dep), current_user=Depends(get_current_user)):
    try:
        ResourceCURD.detach_from_user(db, user_id=current_user.id, resource_id=resource_id)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"删除失败: {e}")

    return None


@router.patch("/me/{resource_id}", response_model=ResourceResponse)
def update_my_resource(
    resource_id: int,
    payload: ResourceUpdateRequest,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    try:
        obj = ResourceCURD.update_for_user(
            db,
            user_id=current_user.id,
            resource_id=resource_id,
            title=payload.title,
            summary=payload.summary,
            platform=payload.platform,
            thumbnail=payload.thumbnail,
            category_id=getattr(payload, "category_id", None),
            difficulty=payload.difficulty,
            tags=payload.tags,
            raw_meta=payload.raw_meta,
        )

        assoc = (
            db.query(UserResource)
            .filter(UserResource.user_id == current_user.id, UserResource.resource_id == resource_id)
            .first()
        )
        if not assoc:
            raise ValueError("user_resource association not found")

        if payload.manual_weight is not None:
            assoc.manual_weight = int(payload.manual_weight)
            assoc.effective_weight = int(payload.manual_weight)

        db.commit()
        db.refresh(obj)
        db.refresh(assoc)
    except ValueError as e:
        db.rollback()
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "association not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败: {e}")

    assoc = (
        db.query(UserResource)
        .filter(UserResource.user_id == current_user.id, UserResource.resource_id == resource_id)
        .first()
    )

    # Re-fetch obj with category for response
    obj = (
        db.query(Resource)
        .options(joinedload(Resource.category))
        .filter(Resource.id == resource_id)
        .first()
    )

    return ResourceResponse(
        id=obj.id,
        resource_type=_resource_type_value(obj),
        platform=getattr(obj, "platform", None),
        title=obj.title,
        summary=getattr(obj, "summary", None),
        source_url=getattr(obj, "source_url", None),
        thumbnail=getattr(obj, "thumbnail", None),
        category_id=getattr(obj, "category_id", None),
        category_name=getattr(obj.category, "name", None) if getattr(obj, "category", None) else None,
        difficulty=getattr(obj, "difficulty", None),
        tags=getattr(obj, "tags", None),
        raw_meta=getattr(obj, "raw_meta", None),
        manual_weight=getattr(assoc, "manual_weight", None) if assoc else None,
        behavior_weight=getattr(assoc, "behavior_weight", None) if assoc else None,
        effective_weight=getattr(assoc, "effective_weight", None) if assoc else None,
        added_at=getattr(assoc, "added_at", None) if assoc else None,
        last_opened=getattr(assoc, "last_opened", None) if assoc else None,
        open_count=getattr(assoc, "open_count", None) if assoc else None,
        completion_status=getattr(assoc, "completion_status", None) if assoc else None,
        community_score=getattr(obj, "community_score", None),
        save_count=getattr(obj, "save_count", None),
        trending_score=getattr(obj, "trending_score", None),
        created_at=getattr(obj, "created_at", None),
    )
