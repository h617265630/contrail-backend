"""
Video resource management API endpoints.

Provides REST API routes for:
- Extracting video metadata from YouTube URLs
- Creating, reading, and deleting videos
- Managing video categories
- Recording and querying watch history
"""

from typing import List
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pytube import YouTube

from app.core.deps import get_current_user, get_db_dep
from app.curd.resources.video_curd import VideoCURD
from app.curd.watch_history_curd import WatchHistoryCURD
from app.schemas.resources.video import VideoCategoryAssign, VideoCreate, VideoResponse
from app.schemas.resources.extract import UrlExtractRequest, UrlExtractResponse
from app.schemas.watch_history import WatchHistoryCreate, WatchHistoryResponse

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("/extract", response_model=UrlExtractResponse)
def extract_video_metadata(payload: UrlExtractRequest):
    """
    Extract title and description from a YouTube video URL.

    Uses pytube to scrape YouTube page metadata. Only YouTube URLs
    are supported; other video platforms will return a 400 error.

    Args:
        payload: Request body containing the video URL.

    Returns:
        UrlExtractResponse with title and description.

    Raises:
        HTTPException: 400 if URL is not YouTube or parsing fails.
    """
    url = str(payload.url)
    host = (urlparse(url).hostname or "").lower()
    if not (host.endswith("youtube.com") or host.endswith("youtu.be")):
        raise HTTPException(status_code=400, detail="目前仅支持 YouTube 链接解析")

    try:
        yt = YouTube(url)
        title = (yt.title or "").strip()
        description = (yt.description or "").strip() or None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析失败: {e}")

    if not title:
        raise HTTPException(status_code=400, detail="解析失败: 未获取到标题")

    return UrlExtractResponse(title=title, description=description)


@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
def create_video(
    video_in: VideoCreate,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    """
    Create a new video resource for the authenticated user.

    Args:
        video_in: Video creation data (URL, title, description, etc.).
        db: Database session.
        current_user: Authenticated user from dependency.

    Returns:
        Created VideoResponse object.
    """
    video = VideoCURD.create_video(db, video_in, owner_id=current_user.id)
    return video


@router.get("/", response_model=List[VideoResponse])
def read_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_dep)):
    """
    Retrieve a paginated list of all videos.

    Args:
        skip: Number of records to skip (offset).
        limit: Maximum number of records to return.
        db: Database session.

    Returns:
        List of VideoResponse objects.
    """
    videos = VideoCURD.get_videos(db, skip=skip, limit=limit)
    return videos


@router.get("/{video_id}", response_model=VideoResponse)
def read_video(video_id: int, db: Session = Depends(get_db_dep)):
    """
    Retrieve a single video by ID.

    Args:
        video_id: Unique identifier of the video.
        db: Database session.

    Returns:
        VideoResponse object.

    Raises:
        HTTPException: 404 if video not found.
    """
    db_video = VideoCURD.get_video(db, video_id)
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    """
    Delete a video by ID.

    Only the video owner can delete their own videos.

    Args:
        video_id: ID of the video to delete.
        db: Database session.
        current_user: Authenticated user from dependency.

    Raises:
        HTTPException: 404 if video not found, 403 if not owner.
    """
    video = VideoCURD.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this video")

    VideoCURD.delete_video(db, video)
    return None


# ============== Category Management ==============

@router.post("/{video_id}/categories/{category_id}")
def add_video_category(
    video_id: int,
    category_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    """
    Add a single category to a video.

    Args:
        video_id: ID of the video to update.
        category_id: ID of the category to add.
        db: Database session.
        current_user: Authenticated user from dependency.

    Returns:
        Success message with video and category IDs.

    Raises:
        HTTPException: 400 if video or category doesn't exist.
    """
    try:
        VideoCURD.add_category_to_video(db, video_id, category_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "分类已添加", "video_id": video_id, "category_id": category_id}


@router.delete("/{video_id}/categories/{category_id}")
def remove_video_category(
    video_id: int,
    category_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    """
    Remove a single category from a video.

    Args:
        video_id: ID of the video to update.
        category_id: ID of the category to remove.
        db: Database session.
        current_user: Authenticated user from dependency.

    Returns:
        Success message with video and category IDs.

    Raises:
        HTTPException: 400 if video doesn't exist.
    """
    try:
        VideoCURD.remove_category_from_video(db, video_id, category_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "分类已移除", "video_id": video_id, "category_id": category_id}


@router.post("/{video_id}/categories")
def assign_video_categories(
    video_id: int,
    data: VideoCategoryAssign,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    """
    Replace all categories of a video with a new set.

    Args:
        video_id: ID of the video to update.
        data: Request body containing list of category IDs.
        db: Database session.
        current_user: Authenticated user from dependency.

    Returns:
        Success message with video and category IDs.

    Raises:
        HTTPException: 400 if video or any category doesn't exist.
    """
    try:
        VideoCURD.assign_categories_to_video(db, video_id, data.category_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "分类已更新", "video_id": video_id, "category_ids": data.category_ids}


# ============== Watch History ==============

@router.post("/{video_id}/watch", response_model=WatchHistoryResponse)
def record_watch(
    video_id: int,
    data: WatchHistoryCreate,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    """
    Record or update a user's watch history for a video.

    Args:
        video_id: ID of the video that was watched.
        data: Watch data including is_watched flag and watch_time.
        db: Database session.
        current_user: Authenticated user from dependency.

    Returns:
        WatchHistoryResponse for the recorded watch event.

    Raises:
        HTTPException: 400 if user or video doesn't exist.
    """
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
def get_watch_count(
    video_id: int,
    db: Session = Depends(get_db_dep),
    current_user=Depends(get_current_user),
):
    """
    Get the total watch count for a video.

    Args:
        video_id: ID of the video.
        db: Database session.
        current_user: Authenticated user from dependency.

    Returns:
        Object containing video_id and watch_count.
    """
    count = WatchHistoryCURD.get_video_watch_count(db, video_id)
    return {"video_id": video_id, "watch_count": count}
