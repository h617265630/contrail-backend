from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class ResourceCreateFromUrl(BaseModel):
    url: HttpUrl
    category_id: int
    visibility: Optional[str] = "private"  # "private" | "public"
    is_public: Optional[bool] = False
    manual_weight: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class ResourceUpdateRequest(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    platform: Optional[str] = None
    thumbnail: Optional[str] = None
    category_id: Optional[int] = None
    difficulty: Optional[int] = None
    tags: Optional[dict[str, Any]] = None
    raw_meta: Optional[dict[str, Any]] = None
    manual_weight: Optional[int] = None
    is_public: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)


class UserResourceProfileUpdateRequest(BaseModel):
    """用户个性化字段：与 Resource 固定字段隔离，仅影响 user_resource 表"""
    category_id: Optional[int] = None  # 覆盖原始分类，0 或 null 表示清除覆盖
    custom_notes: Optional[str] = None
    custom_tags: Optional[dict[str, Any]] = None
    personal_rating: Optional[int] = None  # 1-5
    is_favorite: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class VideoInfo(BaseModel):
    duration: Optional[int] = None
    channel: Optional[str] = None
    video_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DocInfo(BaseModel):
    doc_type: Optional[str] = None
    version: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ArticleInfo(BaseModel):
    publisher: Optional[str] = None
    published_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class ResourceResponse(BaseModel):
    id: int
    resource_type: str
    platform: Optional[str] = None
    title: str
    summary: Optional[str] = None
    source_url: str
    thumbnail: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    difficulty: Optional[int] = None
    tags: Optional[dict[str, Any]] = None
    raw_meta: Optional[dict[str, Any]] = None
    is_system_public: Optional[bool] = None
    creator_id: Optional[int] = None
    visibility: Optional[str] = None   # "private" | "public" | None(系统资源)
    source: Optional[str] = None       # "created" | "saved" | None

    manual_weight: Optional[int] = None
    behavior_weight: Optional[int] = None
    effective_weight: Optional[int] = None
    added_at: Optional[datetime] = None
    last_opened: Optional[datetime] = None
    open_count: Optional[int] = None
    completion_status: Optional[bool] = None

    # 二次修改扩展字段
    category_id: Optional[int] = None  # 用户自定义分类覆盖（NULL 时用原始 resources.category_id）
    custom_notes: Optional[str] = None
    custom_tags: Optional[dict[str, Any]] = None
    personal_rating: Optional[int] = None
    is_favorite: Optional[bool] = None

    community_score: Optional[int] = None
    save_count: Optional[int] = None
    trending_score: Optional[int] = None

    created_at: Optional[datetime] = None
    user_seq: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class ResourceDetailResponse(ResourceResponse):
    video: Optional[VideoInfo] = None
    doc: Optional[DocInfo] = None
    article: Optional[ArticleInfo] = None


class ResourceAttachResponse(BaseModel):
    already_exists: bool
    resource: ResourceResponse

    model_config = ConfigDict(from_attributes=True)
