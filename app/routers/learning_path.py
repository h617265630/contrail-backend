from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db_dep, get_current_user
from app.schemas.learning_path import (
	LearningPathCreate,
	LearningPathUpdate,
	LearningPathResponse,
	LearningPathDetailResponse,
	PathItemInLearningPathResponse,
	AddResourceToLearningPathRequest,
	ResourceKind,
	LearningPathAttachResponse,
	UpdateUserLearningPathRequest,
	LearningPathWithUserOverride,
	UserLearningPathFields,
)
from app.curd.learning_path_curd import LearningPathCURD
from app.curd.path_item_curd import PathItemCURD
from app.models.user_learning_path import UserLearningPath
from app.models.learning_path import LearningPath
from app.models.path_item import PathItem
from app.models.resource import Resource
from app.schemas.resources.resource import ResourceResponse


router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])


def _resource_type_value(obj: Resource) -> str:
	rt = getattr(obj, "resource_type", None)
	val = rt.value if hasattr(rt, "value") else (str(rt) if rt is not None else "")
	return (val or "").strip().lower() or "unknown"


def _to_resource_response(obj: Resource) -> ResourceResponse:
	return ResourceResponse(
		id=obj.id,
		resource_type=_resource_type_value(obj),
		platform=getattr(obj, "platform", None),
		title=obj.title,
		summary=getattr(obj, "summary", None),
		source_url=getattr(obj, "source_url", None),
		thumbnail=getattr(obj, "thumbnail", None),
		category_id=getattr(obj, "category_id", None),
		category_name=getattr(obj, "category_name", None),
		difficulty=getattr(obj, "difficulty", None),
		tags=getattr(obj, "tags", None),
		raw_meta=getattr(obj, "raw_meta", None),
		created_at=getattr(obj, "created_at", None),
	)


def _to_resource_kind(obj: Resource | None) -> ResourceKind:
	if obj is None:
		return ResourceKind.article
	val = _resource_type_value(obj)
	try:
		return ResourceKind(val)
	except Exception:
		return ResourceKind.article


@router.post("/", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
def create_learning_path(
	payload: LearningPathCreate,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	try:
		lp = LearningPathCURD.create_learning_path(
			db=db,
			user_id=current_user.id,
			title=payload.title,
			type=getattr(payload, "type", None),
			description=payload.description,
			is_public=payload.is_public,
			cover_image_url=getattr(payload, "cover_image_url", None),
			category_id=payload.category_id,
		)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	return lp


@router.get("/public", response_model=List[LearningPathResponse])
def list_public_learning_paths(
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	db: Session = Depends(get_db_dep),
):
	return LearningPathCURD.list_public_learning_paths(db, skip=skip, limit=limit)


@router.post("/{learning_path_id}/fork", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
def fork_learning_path(
	learning_path_id: int,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	try:
		lp = LearningPathCURD.fork_learning_path(db, source_path_id=learning_path_id, user_id=current_user.id)
	except ValueError as e:
		raise HTTPException(status_code=404, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Fork failed: {e}")
	return lp


@router.get("/public/{learning_path_id}", response_model=LearningPathDetailResponse)
def get_public_learning_path_detail(
	learning_path_id: int,
	db: Session = Depends(get_db_dep),
):
	lp = LearningPathCURD.get_learning_path_with_items(db, learning_path_id)
	if not lp or (not bool(getattr(lp, "is_public", False))) or (not bool(getattr(lp, "is_active", True))):
		raise HTTPException(status_code=404, detail="LearningPath not found")

	items: List[PathItemInLearningPathResponse] = []
	for it in lp.path_items:
		res = getattr(it, "resource", None)
		resource_data = _to_resource_response(res) if res is not None else None
		items.append(
			PathItemInLearningPathResponse(
				id=it.id,
				learning_path_id=it.learning_path_id,
				resource_id=it.resource_id,
				resource_type=_to_resource_kind(res),
				title=(getattr(res, "title", "") if res is not None else ""),
				order_index=it.order_index,
				stage=getattr(it, "stage", None),
				purpose=getattr(it, "purpose", None),
				estimated_time=getattr(it, "estimated_time", None),
				is_optional=bool(getattr(it, "is_optional", False)),
				resource_data=resource_data,
			)
		)

	return LearningPathDetailResponse(
		id=lp.id,
		title=lp.title,
		type=getattr(lp, "type", None),
		description=lp.description,
		is_public=lp.is_public,
		cover_image_url=getattr(lp, "cover_image_url", None),
		category_id=getattr(lp, "category_id", None),
		category_name=getattr(lp, "category_name", None),
		is_active=lp.is_active,
		path_items=items,
	)


@router.get("/", response_model=List[LearningPathWithUserOverride])
def list_learning_paths(
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	rows = LearningPathCURD.get_learning_paths_by_user_with_assoc(db, current_user.id, skip=skip, limit=limit)
	return [
		LearningPathWithUserOverride(
			id=lp.id,
			title=getattr(assoc, "custom_title", None) or lp.title,
			type=getattr(lp, "type", None),
			description=getattr(assoc, "custom_description", None) or getattr(lp, "description", None),
			is_public=getattr(lp, "is_public", False),
			cover_image_url=getattr(assoc, "custom_cover_image_url", None) or getattr(lp, "cover_image_url", None),
			category_id=getattr(lp, "category_id", None),
			category_name=getattr(lp, "category_name", None),
			creator_id=getattr(lp, "creator_id", None),
			is_active=getattr(lp, "is_active", True),
			item_count=getattr(lp, "item_count", 0),
			user_override=UserLearningPathFields(
				custom_title=getattr(assoc, "custom_title", None),
				custom_description=getattr(assoc, "custom_description", None),
				custom_cover_image_url=getattr(assoc, "custom_cover_image_url", None),
				notes=getattr(assoc, "notes", None),
				added_at=str(getattr(assoc, "added_at", None) or "") or None,
				is_pinned=getattr(assoc, "is_pinned", 0),
			),
		)
		for lp, assoc in rows
	]


@router.patch("/me/{learning_path_id}", response_model=LearningPathWithUserOverride)
def update_my_learning_path(
	learning_path_id: int,
	payload: UpdateUserLearningPathRequest,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	try:
		lp, assoc = LearningPathCURD.update_user_learning_path(
			db,
			user_id=current_user.id,
			learning_path_id=learning_path_id,
			custom_title=payload.custom_title,
			custom_description=payload.custom_description,
			custom_cover_image_url=payload.custom_cover_image_url,
			notes=payload.notes,
		)
		db.commit()
		db.refresh(lp)
		db.refresh(assoc)
	except ValueError as e:
		db.rollback()
		raise HTTPException(status_code=404, detail=str(e))
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=400, detail=f"更新失败: {e}")

	return LearningPathWithUserOverride(
		id=lp.id,
		title=getattr(assoc, "custom_title", None) or lp.title,
		type=getattr(lp, "type", None),
		description=getattr(assoc, "custom_description", None) or getattr(lp, "description", None),
		is_public=getattr(lp, "is_public", False),
		cover_image_url=getattr(assoc, "custom_cover_image_url", None) or getattr(lp, "cover_image_url", None),
		category_id=getattr(lp, "category_id", None),
		category_name=getattr(lp, "category_name", None),
		creator_id=getattr(lp, "creator_id", None),
		is_active=getattr(lp, "is_active", True),
		item_count=getattr(lp, "item_count", 0),
		user_override=UserLearningPathFields(
			custom_title=getattr(assoc, "custom_title", None),
			custom_description=getattr(assoc, "custom_description", None),
			custom_cover_image_url=getattr(assoc, "custom_cover_image_url", None),
			notes=getattr(assoc, "notes", None),
			added_at=str(getattr(assoc, "added_at", None) or "") or None,
			is_pinned=getattr(assoc, "is_pinned", 0),
		),
	)


@router.post("/me/{learning_path_id}/attach", response_model=LearningPathAttachResponse)
def attach_public_learning_path_to_me(
	learning_path_id: int,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	# Only allow attaching public + active learning paths.
	lp = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
	if not lp or (not bool(getattr(lp, "is_public", False))) or (not bool(getattr(lp, "is_active", True))):
		raise HTTPException(status_code=404, detail="LearningPath not found")

	already_exists = (
		db.query(UserLearningPath)
		.filter(
			UserLearningPath.user_id == current_user.id,
			UserLearningPath.learning_path_id == learning_path_id,
		)
		.first()
		is not None
	)

	if not already_exists:
		try:
			db.add(UserLearningPath(user_id=current_user.id, learning_path_id=learning_path_id))
			db.commit()
		except Exception as e:
			db.rollback()
			raise HTTPException(status_code=400, detail=f"添加失败: {e}")

	return LearningPathAttachResponse(
		already_exists=already_exists,
		learning_path=LearningPathResponse.model_validate(lp),
	)


def _ensure_ownership(db: Session, user_id: int, learning_path_id: int) -> LearningPath:
	lp = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
	if not lp:
		raise HTTPException(status_code=404, detail="LearningPath not found")
	assoc = (
		db.query(UserLearningPath)
		.filter(
			UserLearningPath.user_id == user_id,
			UserLearningPath.learning_path_id == learning_path_id,
		)
		.first()
	)
	if not assoc:
		raise HTTPException(status_code=403, detail="No permission for this learning path")
	return lp


@router.get("/{learning_path_id}", response_model=LearningPathDetailResponse)
def get_learning_path_detail(
	learning_path_id: int,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	_ensure_ownership(db, current_user.id, learning_path_id)
	lp = LearningPathCURD.get_learning_path_with_items(db, learning_path_id)
	if not lp:
		raise HTTPException(status_code=404, detail="LearningPath not found")

	# 将 ORM 的 path_items 映射为 schema
	items: List[PathItemInLearningPathResponse] = []
	for it in lp.path_items:
		res = getattr(it, "resource", None)
		resource_data = _to_resource_response(res) if res is not None else None
		items.append(
			PathItemInLearningPathResponse(
				id=it.id,
				learning_path_id=it.learning_path_id,
				resource_id=it.resource_id,
				resource_type=_to_resource_kind(res),
				title=(getattr(res, "title", None) or f"Resource {it.resource_id}"),
				order_index=it.order_index,
				stage=getattr(it, "stage", None),
				purpose=getattr(it, "purpose", None),
				estimated_time=getattr(it, "estimated_time", None),
				is_optional=bool(getattr(it, "is_optional", False)),
				resource_data=resource_data,
			)
		)

	return LearningPathDetailResponse(
		id=lp.id,
		title=lp.title,
		type=getattr(lp, "type", None),
		description=lp.description,
		is_public=lp.is_public,
		cover_image_url=getattr(lp, "cover_image_url", None),
		category_id=getattr(lp, "category_id", None),
		category_name=getattr(lp, "category_name", None),
		is_active=lp.is_active,
		path_items=items,
	)


@router.delete("/{learning_path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_learning_path(
	learning_path_id: int,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	lp = _ensure_ownership(db, current_user.id, learning_path_id)
	try:
		LearningPathCURD.delete_learning_path(db, lp)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception:
		raise HTTPException(status_code=500, detail="Failed to delete learning path")
	return None


@router.patch("/{learning_path_id}", response_model=LearningPathResponse)
def update_learning_path(
	learning_path_id: int,
	payload: LearningPathUpdate,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	lp = _ensure_ownership(db, current_user.id, learning_path_id)

	# Apply partial updates.
	data = payload.model_dump(exclude_unset=True)
	for key, value in data.items():
		setattr(lp, key, value)

	try:
		db.add(lp)
		db.commit()
		db.refresh(lp)
	except Exception as e:
		db.rollback()
		raise HTTPException(status_code=400, detail=f"更新失败: {e}")

	return lp


@router.post("/{learning_path_id}/items", response_model=PathItemInLearningPathResponse, status_code=status.HTTP_201_CREATED)
def add_resource_to_learning_path(
	learning_path_id: int,
	payload: AddResourceToLearningPathRequest,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	_ensure_ownership(db, current_user.id, learning_path_id)

	try:
		item = LearningPathCURD.add_resource_to_learning_path(
			db=db,
			learning_path_id=learning_path_id,
			resource_id=payload.resource_id,
			order_index=payload.order_index,
			stage=payload.stage,
			purpose=payload.purpose,
			estimated_time=payload.estimated_time,
			is_optional=payload.is_optional,
		)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		# Ensure any failed transaction is rolled back before returning.
		try:
			db.rollback()
		except Exception:
			pass
		raise HTTPException(status_code=400, detail=f"添加失败: {e}")
	res = db.query(Resource).filter(Resource.id == item.resource_id).first()
	return PathItemInLearningPathResponse(
		id=item.id,
		learning_path_id=item.learning_path_id,
		resource_id=item.resource_id,
		resource_type=_to_resource_kind(res),
		title=(getattr(res, "title", None) or f"Resource {item.resource_id}"),
		order_index=item.order_index,
		stage=getattr(item, "stage", None),
		purpose=getattr(item, "purpose", None),
		estimated_time=getattr(item, "estimated_time", None),
		is_optional=bool(getattr(item, "is_optional", False)),
		resource_data=None,
	)


@router.delete("/{learning_path_id}/items/{resource_id}")
def remove_resource_from_learning_path(
	learning_path_id: int,
	resource_id: int,
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	_ensure_ownership(db, current_user.id, learning_path_id)
	ok = LearningPathCURD.remove_resource_from_learning_path(db, learning_path_id, resource_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Path item not found")
	return {"success": True}


@router.get("/{learning_path_id}/items", response_model=List[PathItemInLearningPathResponse])
def list_path_items(
	learning_path_id: int,
	skip: int = Query(0, ge=0),
	limit: int = Query(100, ge=1, le=200),
	db: Session = Depends(get_db_dep),
	current_user=Depends(get_current_user),
):
	_ensure_ownership(db, current_user.id, learning_path_id)
	items = PathItemCURD.list_by_learning_path(db, learning_path_id, skip=skip, limit=limit)
	return [
		PathItemInLearningPathResponse(
			id=it.id,
			learning_path_id=it.learning_path_id,
			resource_id=it.resource_id,
			resource_type=_to_resource_kind(getattr(it, "resource", None)),
			title=(getattr(getattr(it, "resource", None), "title", None) or f"Resource {it.resource_id}"),
			order_index=it.order_index,
			stage=getattr(it, "stage", None),
			purpose=getattr(it, "purpose", None),
			estimated_time=getattr(it, "estimated_time", None),
			is_optional=bool(getattr(it, "is_optional", False)),
			resource_data=None,
		)
		for it in items
	]



