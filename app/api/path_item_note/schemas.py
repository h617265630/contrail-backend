from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NoteUpsertRequest(BaseModel):
    path_item_id: int
    notes: str

    model_config = ConfigDict(from_attributes=True)


class NoteResponse(BaseModel):
    path_item_id: int
    notes: str
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
