from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_

from app.models.rbac.permission import Permission  # ORM 模型
from app.models.rbac.role import Role


class PermissionCURD:
	"""
	RBAC 权限的 CURD 封装。

	约定：
	- code 唯一，且与 module.action 一致（例如 video.read → module=video, action=read）
	- create/update 时做一致性与唯一性检查，抛 ValueError 以便路由层转为 400/409。
	"""

	# ============ 基础查询 ============
	@staticmethod
	def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
		return db.query(Permission).filter(Permission.id == permission_id).first()

	@staticmethod
	def get_by_code(db: Session, code: str) -> Optional[Permission]:
		return db.query(Permission).filter(Permission.code == code).first()

	@staticmethod
	def list_permissions(
		db: Session,
		skip: int = 0,
		limit: int = 100,
		active_only: bool = False,
		module: Optional[str] = None,
		action: Optional[str] = None,
		keyword: Optional[str] = None,
	) -> List[Permission]:
		q = db.query(Permission)
		if active_only:
			q = q.filter(Permission.is_active.is_(True))
		if module:
			q = q.filter(Permission.module == module)
		if action:
			q = q.filter(Permission.action == action)
		if keyword:
			like = f"%{keyword}%"
			q = q.filter(or_(Permission.name.ilike(like), Permission.code.ilike(like)))
		return q.offset(skip).limit(limit).all()

	# ============ 创建 ============
	@staticmethod
	def create_permission(
		db: Session,
		name: str,
		code: str,
		module: str,
		action: str,
		description: Optional[str] = None,
		is_active: bool = True,
	) -> Permission:
		# 一致性校验：code 必须等于 f"{module}.{action}"
		expected_code = f"{module}.{action}"
		if code != expected_code:
			raise ValueError(f"权限代码必须与模块与操作一致: {expected_code}")

		# 唯一性校验
		if PermissionCURD.get_by_code(db, code):
			raise ValueError("权限代码已存在")

		perm = Permission(
			name=name,
			code=code,
			module=module,
			action=action,
			description=description,
			is_active=is_active,
		)
		db.add(perm)
		try:
			db.commit()
		except IntegrityError:
			db.rollback()
			# 二次检查给出清晰错误
			raise ValueError("创建权限失败，可能是唯一约束冲突")
		db.refresh(perm)
		return perm

	# ============ 更新 ============
	@staticmethod
	def update_permission(
		db: Session,
		permission_id: int,
		update_data: Dict[str, Any],
	) -> Optional[Permission]:
		perm = PermissionCURD.get_permission(db, permission_id)
		if not perm:
			return None

		# 如果更新了 module 或 action 或 code，做一致性校验
		module = update_data.get("module", perm.module)
		action = update_data.get("action", perm.action)
		code = update_data.get("code", perm.code)
		expected_code = f"{module}.{action}"
		if code != expected_code:
			raise ValueError(f"权限代码必须与模块与操作一致: {expected_code}")

		# 如果 code 改变，检查唯一
		if code != perm.code and PermissionCURD.get_by_code(db, code):
			raise ValueError("权限代码已存在")

		# 应用其余字段更新
		for k, v in update_data.items():
			setattr(perm, k, v)

		try:
			db.commit()
		except IntegrityError:
			db.rollback()
			raise ValueError("更新权限失败，可能是唯一约束冲突")
		db.refresh(perm)
		return perm

	# ============ 删除 ============
	@staticmethod
	def delete_permission(db: Session, permission_id: int) -> bool:
		perm = PermissionCURD.get_permission(db, permission_id)
		if not perm:
			return False
		db.delete(perm)
		try:
			db.commit()
		except IntegrityError:
			db.rollback()
			return False
		return True

	# ============ 角色赋权 ============
	@staticmethod
	def assign_to_role(db: Session, role_id: int, permission_ids: List[int]) -> None:
		"""为角色批量绑定权限（去重，忽略不存在的权限）。"""
		role = db.query(Role).filter(Role.id == role_id).first()
		if not role:
			raise ValueError("角色不存在")

		# 现有权限集合
		existing_ids = {p.id for p in role.permissions}
		# 找出需要添加的权限
		to_add_ids = [pid for pid in permission_ids if pid not in existing_ids]
		if not to_add_ids:
			return

		new_perms = db.query(Permission).filter(Permission.id.in_(to_add_ids)).all()
		for p in new_perms:
			role.permissions.append(p)

		try:
			db.commit()
		except IntegrityError:
			db.rollback()
			raise ValueError("为角色分配权限失败")

