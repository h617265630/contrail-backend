from datetime import datetime

from pydantic import BaseModel


class UserFileResponse(BaseModel):
    id: int
    user_id: int
    title: str | None = None
    file_type: str
    original_filename: str | None = None
    content_type: str | None = None
    size_bytes: int | None = None
    content: str | None = None
    file_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserFileUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
