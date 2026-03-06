from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class ReaderExtractRequest(BaseModel):
    url: HttpUrl
    model_config = ConfigDict(from_attributes=True)


class ReaderExtractResponse(BaseModel):
    url: str
    title: str
    site_name: Optional[str] = None
    byline: Optional[str] = None
    excerpt: Optional[str] = None
    content_html: str
    word_count: int = 0
    extracted_at: datetime

    model_config = ConfigDict(from_attributes=True)
