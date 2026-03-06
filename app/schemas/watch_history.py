from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WatchHistoryCreate(BaseModel):
    is_watched: bool = True
    watch_time: Optional[datetime] = None


class WatchHistoryResponse(BaseModel):
    id: int
    user_id: int
    video_id: int
    is_watched: bool
    watch_time: datetime

    class Config:
        from_attributes = True
