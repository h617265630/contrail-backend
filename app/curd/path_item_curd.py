from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.models.path_item import PathItem
from app.models.learning_path import LearningPath
from app.models.resource import Resource


class PathItemCURD:
    """
    PathItem 的基础增删改查，以及基于资源(Video/Clip)的注册封装。
    采用方案B：PathItem 通过 resource_id 引用资源父表(Resource)，并记录 resource_type。
    约束：
      - (learning_path_id, resource_id) 唯一
      - (learning_path_id, position) 唯一
    """

    # ---------- Read ----------
    @staticmethod
    def get(db: Session, path_item_id: int) -> Optional[PathItem]:
        return db.query(PathItem).filter(PathItem.id == path_item_id).first()

    @staticmethod
    def list_by_learning_path(
        db: Session, learning_path_id: int, skip: int = 0, limit: int = 100
    ) -> List[PathItem]:
        return (
            db.query(PathItem)
            .filter(PathItem.learning_path_id == learning_path_id)
            .order_by(PathItem.order_index.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ---------- Create ----------
    @staticmethod
    def _ensure_learning_path_and_resource(
        db: Session, learning_path_id: int, resource_id: int
    ) -> Tuple[LearningPath, Resource]:
        lp = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
        if not lp:
            raise ValueError("LearningPath not found")

        res = db.query(Resource).filter(Resource.id == resource_id).first()
        if not res:
            raise ValueError("Resource not found")

        return lp, res

    @staticmethod
    def create(
        db: Session,
        learning_path_id: int,
        resource_id: int,
        *,
        order_index: Optional[int] = None,
        stage: Optional[str] = None,
        purpose: Optional[str] = None,
        estimated_time: Optional[int] = None,
        is_optional: Optional[bool] = None,
    ) -> PathItem:
        PathItemCURD._ensure_learning_path_and_resource(db, learning_path_id, resource_id)

        # 如果没有给 order_index，使用当前路径的最大 order_index + 1
        if order_index is None:
            max_pos = db.query(func.max(PathItem.order_index)).filter(
                PathItem.learning_path_id == learning_path_id
            ).scalar()
            order_index = (max_pos or 0) + 1

        item = PathItem(
            learning_path_id=learning_path_id,
            resource_id=resource_id,
            order_index=order_index,
            stage=stage,
            purpose=purpose,
            estimated_time=estimated_time,
            is_optional=bool(is_optional) if is_optional is not None else False,
        )
        db.add(item)
        try:
            db.commit()
            db.refresh(item)
        except IntegrityError:
            db.rollback()
            # 可能是位置冲突或资源重复添加
            raise ValueError("Duplicate path item: order_index or resource already exists in this learning path")
        return item

    # ---------- Update ----------
    @staticmethod
    def update(
        db: Session,
        path_item_id: int,
        *,
        order_index: Optional[int] = None,
        stage: Optional[str] = None,
        purpose: Optional[str] = None,
        estimated_time: Optional[int] = None,
        is_optional: Optional[bool] = None,
    ) -> Optional[PathItem]:
        item = PathItemCURD.get(db, path_item_id)
        if not item:
            return None

        if order_index is not None:
            item.order_index = order_index
        if stage is not None:
            item.stage = stage
        if purpose is not None:
            item.purpose = purpose
        if estimated_time is not None:
            item.estimated_time = estimated_time
        if is_optional is not None:
            item.is_optional = bool(is_optional)

        try:
            db.commit()
            db.refresh(item)
        except IntegrityError:
            db.rollback()
            raise ValueError("Duplicate order_index in this learning path")
        return item

    # ---------- Delete ----------
    @staticmethod
    def delete(db: Session, path_item_id: int) -> bool:
        item = PathItemCURD.get(db, path_item_id)
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True
