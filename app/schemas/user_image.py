from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class UserImageResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    image_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserImageCreate(BaseModel):
    title: Optional[str] = None
