from typing import List
from pydantic import BaseModel
from app.schemas.rbac.user import UserResponse
from app.schemas.rbac.role import RoleResponse


class UserRoleAssign(BaseModel):
	"""为某个用户分配多个角色的请求体。"""
	role_ids: List[int]


class UserWithRoles(UserResponse):
	"""带有角色列表的用户响应模型。"""
	roles: List[RoleResponse] = []

	model_config = {
		"from_attributes": True
	}

