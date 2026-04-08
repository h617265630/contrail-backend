from pydantic import BaseModel
from typing import Optional, Union, Annotated
from enum import Enum
from app.schemas.resources.video import VideoCreate, VideoResponse
from app.schemas.resources.clip import ClipCreate, ClipResponse

class PathItemType(str, Enum):
    video = "video"
    clip = "clip"


class PathItemBase(BaseModel):
    title: str
    description: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class PathItemCreate(PathItemBase):
    item_type: PathItemType
    # 使用 Discriminated Union 承载具体子类型的数据
    item_data: Annotated[Union[VideoCreate, ClipCreate], "item_type"]

    model_config = {
        "from_attributes": True
    }
class PathItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class PathItemResponse(PathItemBase):
    id: int
    item_type: PathItemType
    item_data: Union[VideoResponse, ClipResponse]

    model_config = {
        "from_attributes": True
    }