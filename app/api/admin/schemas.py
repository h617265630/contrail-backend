from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_learning_paths: int
    public_learning_paths: int
    total_resources: int
    total_categories: int
    users_last_7_days: int = 0
    paths_last_7_days: int = 0
    resources_last_7_days: int = 0

    model_config = {"from_attributes": True}


class AdminUserItem(BaseModel):
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: List[str] = []

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    users: List[AdminUserItem]
    total: int
    skip: int
    limit: int


class AdminLearningPathItem(BaseModel):
    id: int
    title: str
    is_public: bool
    is_active: bool
    category_name: Optional[str] = None
    created_at: datetime
    user_count: int = 0

    model_config = {"from_attributes": True}


class AdminLearningPathListResponse(BaseModel):
    paths: List[AdminLearningPathItem]
    total: int


class AdminResourceItem(BaseModel):
    id: int
    title: str
    resource_type: str
    platform: Optional[str] = None
    category_name: Optional[str] = None
    save_count: int
    trending_score: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminResourceListResponse(BaseModel):
    resources: List[AdminResourceItem]
    total: int


class DailyCountItem(BaseModel):
    date: str
    count: int


class CategoryCountItem(BaseModel):
    name: str
    count: int


class TopResourceItem(BaseModel):
    title: str
    save_count: int


class AdminAnalyticsResponse(BaseModel):
    daily_users: List[DailyCountItem]
    daily_paths: List[DailyCountItem]
    daily_resources: List[DailyCountItem]
    top_categories: List[CategoryCountItem]
    top_resources: List[TopResourceItem]

    model_config = {"from_attributes": True}
