from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: str
    file_size: int = Field(ge=0)
    duration: float = Field(ge=0)
    model_config = ConfigDict(from_attributes=True)

class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)



class VideoResponse(VideoBase):
    id: int
    view_count: int
    created_at: str
    updated_at: str
    thumbnail_path: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class VideoCategoryAssign(BaseModel):
    category_ids: List[int]
    model_config = ConfigDict(from_attributes=True)

