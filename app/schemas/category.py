from typing import Optional

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_system: bool

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
