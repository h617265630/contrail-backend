from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

from app.schemas.resources.resource import ResourceResponse


class ResourceKind(str, Enum):
    video = "video"
    document = "document"
    article = "article"


class LearningPathBase(BaseModel):
    title: str
    type: Optional[str] = None
    description: Optional[str] = None
    is_public: bool = False
    cover_image_url: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    creator_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }


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

    model_config = {
        "from_attributes": True
    }


class UserLearningPathFields(BaseModel):
    """UserLearningPath 覆盖字段，用于用户自定义收藏路径的展示"""
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None
    custom_cover_image_url: Optional[str] = None
    notes: Optional[str] = None
    added_at: Optional[str] = None
    is_pinned: Optional[int] = None

    model_config = {"from_attributes": True}


class LearningPathWithUserOverride(LearningPathBase):
    """带用户覆盖字段的路径响应（用于 list/get 用户路径时）"""
    user_override: UserLearningPathFields | None = None
    item_count: int = 0

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

    model_config = {
        "from_attributes": True
    }


class LearningPathResponse(LearningPathBase):
    id: int
    is_active: bool = True
    item_count: int = 0

    model_config = {
        "from_attributes": True
    }


class LearningPathDetailResponse(LearningPathResponse):
    path_items: List[PathItemInLearningPathResponse] = []

    model_config = {
        "from_attributes": True
    }


class AddResourceToLearningPathRequest(BaseModel):
    resource_id: int
    order_index: Optional[int] = None
    stage: Optional[str] = None
    purpose: Optional[str] = None
    estimated_time: Optional[int] = None
    is_optional: Optional[bool] = None

    model_config = {
        "from_attributes": True
    }


class LearningPathAttachResponse(BaseModel):
    already_exists: bool
    learning_path: LearningPathResponse

    model_config = {
        "from_attributes": True
    }


class UpdateUserLearningPathRequest(BaseModel):
    """用户更新收藏路径的请求：写入 UserLearningPath.custom_* 覆盖字段"""
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None
    custom_cover_image_url: Optional[str] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
