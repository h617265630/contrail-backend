from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.resources.resource import ResourceResponse


class ResourceKind(str, Enum):
    video = "video"
    document = "document"
    article = "article"


class LearningPathBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    type: Optional[str] = None
    description: Optional[str] = None
    is_public: bool = False
    cover_image_url: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    creator_id: Optional[int] = None
    parent_id: Optional[int] = None
    root_id: Optional[int] = None
    status: Optional[str] = None
    published_at: Optional[str] = None
    fork_count: Optional[int] = 0
    like_count: Optional[int] = 0
    view_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class LearningPathCreate(LearningPathBase):
    # 与 CURD 保持一致，创建时主要使用 title/description
    pass


class LearningPathUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    cover_image_url: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[str] = None

    model_config = {"from_attributes": True}


class PathItemInLearningPathResponse(BaseModel):
    id: int
    learning_path_id: int
    resource_id: int
    resource_type: ResourceKind
    title: str
    order_index: int
    stage: Optional[str] = None
    purpose: Optional[str] = None
    estimated_time: Optional[int] = None
    is_optional: bool = False
    # 按需返回嵌入的资源详情
    resource_data: Optional[ResourceResponse] = None

    model_config = {"from_attributes": True}


class LearningPathResponse(LearningPathBase):
    id: int
    is_active: bool = True

    model_config = {"from_attributes": True}


class LearningPathDetailResponse(LearningPathResponse):
    path_items: List[PathItemInLearningPathResponse] = []

    model_config = {"from_attributes": True}


class AddResourceToLearningPathRequest(BaseModel):
    resource_id: int
    order_index: Optional[int] = None
    stage: Optional[str] = None
    purpose: Optional[str] = None
    estimated_time: Optional[int] = None
    is_optional: Optional[bool] = None

    model_config = {"from_attributes": True}


class LearningPathAttachResponse(BaseModel):
    already_exists: bool
    learning_path: LearningPathResponse

    model_config = {"from_attributes": True}


class LearningPathUserStatusResponse(BaseModel):
    is_saved: bool  # path is in user's collection (attached, not created)
    has_forked: bool  # user has already forked this path

    model_config = {"from_attributes": True}
