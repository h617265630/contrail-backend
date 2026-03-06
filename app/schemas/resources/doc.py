from typing import Optional
from pydantic import BaseModel, ConfigDict


class DocBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DocCreate(DocBase):
    pass

class DocUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)



class DocResponse(DocBase):
    id: int
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)



