from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
# 权限相关
class PermissionBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    module: str = Field(..., min_length=2, max_length=50)
    action: str = Field(..., min_length=2, max_length=50)
    is_active: bool = True
    
    @field_validator('code')
    def code_format(cls, v):
        # 确保权限代码格式为: module.action
        if '.' not in v:
            raise ValueError('权限代码格式应为: 模块.操作')
        return v

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    
    # Pydantic v2 config
    model_config = {
        "from_attributes": True
    }

class PermissionCheck(BaseModel):
    permission_code: str