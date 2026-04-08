from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProgressUpsertRequest(BaseModel):
    path_item_id: int
    progress_percentage: int = Field(ge=0, le=100)

    model_config = ConfigDict(from_attributes=True)


class ProgressResponse(BaseModel):
    path_item_id: int
    progress_percentage: int
    last_watched_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
