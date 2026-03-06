from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ClipBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: float
    end_time: float
    clip_duration: float
    clip_method: str
    generated_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClipCreate(ClipBase):
    pass


class ClipUpdate(ClipBase):
    model_config = ConfigDict(from_attributes=True)


class ClipResponse(ClipBase):
    id: int
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)

