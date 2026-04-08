from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    id: int
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)



