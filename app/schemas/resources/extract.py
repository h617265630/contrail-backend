from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class UrlExtractRequest(BaseModel):
    url: HttpUrl
    model_config = ConfigDict(from_attributes=True)


class ChapterItem(BaseModel):
    start_seconds: int
    timestamp: str
    title: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class UrlExtractResponse(BaseModel):
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[date] = None
    video_id: Optional[str] = None
    duration_seconds: Optional[int] = None
    platform: Optional[str] = None
    chapters: list[ChapterItem] = []
    model_config = ConfigDict(from_attributes=True)
