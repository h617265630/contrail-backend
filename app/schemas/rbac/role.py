from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.rbac.permission import PermissionResponse

class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    level: int = Field(0, ge=0, le=1000)
    is_active: bool = True
    
    @field_validator('code')
    def code_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('角色代码只能包含字母、数字和下划线')
        return v.lower()

class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None

class RoleResponse(RoleBase):
    id: int
    is_system: bool
    created_at: datetime
    permissions: List[PermissionResponse] = []
    user_count: int = 0
    
    model_config = {
        "from_attributes": True
    }