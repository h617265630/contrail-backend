from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.learning_path import LearningPath
from app.models.category import Category
from app.models.user_learning_path import UserLearningPath
from app.models.path_item import PathItem
from app.models.resource import Resource
from app.models.progress import Progress


class LearningPathCURD:
    @staticmethod
    def create_learning_path(
        db: Session,
        user_id: int,
        title: str,
        description: str = None,
        *,
        is_public: bool = False,
        cover_image_url: str | None = None,
        type: str | None = None,
        category_id: int,
    ) -> LearningPath:
        if category_id is None:
            raise ValueError("category_id is required")

        hit = db.query(Category).filter(Category.id == category_id).first()
        if not hit:
            raise ValueError("Category not found")

        learning_path = LearningPath(
            title=title,
            type=type,
            description=description,
            is_public=bool(is_public),
            cover_image_url=cover_image_url,
            category_id=category_id,
            creator_id=user_id,
            status="published",
        )
        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)

        # 创建关联记录
        user_learning_path = UserLearningPath(
            user_id=user_id, learning_path_id=learning_path.id
        )
        try:
            db.add(user_learning_path)
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("This learning path is already associated with the user.")

        return learning_path

    @staticmethod
    def list_public_learning_paths(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[LearningPath]:
        return (
            db.query(LearningPath)
            .options(joinedload(LearningPath.category))
            .filter(LearningPath.is_public.is_(True))
            .filter(LearningPath.is_active.is_(True))
            .filter(LearningPath.status == "published")
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_learning_paths_by_user(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[LearningPath]:
        learning_paths = (
            db.query(LearningPath)
            .options(joinedload(LearningPath.category))
            .join(
                UserLearningPath, UserLearningPath.learning_path_id == LearningPath.id
            )
            .filter(UserLearningPath.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return learning_paths

    @staticmethod
    def get_learning_path(db: Session, learning_path_id: int) -> Optional[LearningPath]:
        return (
            db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
        )

    @staticmethod
    def delete_learning_path(db: Session, learning_path: LearningPath) -> None:
        try:
            lp_id = int(getattr(learning_path, "id"))

            # 1) Delete Progress records that reference path items in this learning path.
            path_item_ids = [
                int(x)
                for (x,) in (
                    db.query(PathItem.id)
                    .filter(PathItem.learning_path_id == lp_id)
                    .all()
                )
                if x is not None
            ]
            if path_item_ids:
                db.query(Progress).filter(
                    Progress.path_item_id.in_(path_item_ids)
                ).delete(synchronize_session=False)

            # 2) Delete join table associations.
            db.query(UserLearningPath).filter(
                UserLearningPath.learning_path_id == lp_id
            ).delete(synchronize_session=False)

            # 3) Delete path items.
            db.query(PathItem).filter(PathItem.learning_path_id == lp_id).delete(
                synchronize_session=False
            )

            # 4) Finally delete the learning path.
            db.delete(learning_path)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise ValueError(
                f"Failed to delete learning path due to integrity constraints: {e}"
            )
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to delete learning path: {e}")

    # ---------- PathItem 相关 CRUD ----------  还要修改
    @staticmethod
    def add_resource_to_learning_path(
        db: Session,
        learning_path_id: int,
        resource_id: int,
        *,
        order_index: Optional[int] = None,
        stage: Optional[str] = None,
        purpose: Optional[str] = None,
        estimated_time: Optional[int] = None,
        is_optional: Optional[bool] = None,
        manual_weight: Optional[int] = None,
    ) -> PathItem:
        # 校验学习路径存在
        lp = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
        if not lp:
            raise ValueError("LearningPath not found")

        # 校验资源存在
        res = db.query(Resource).filter(Resource.id == resource_id).first()
        if not res:
            raise ValueError("Resource not found")

        # 计算 order_index（若未提供，则取该路径现有最大 order_index + 1）
        if order_index is None:
            max_pos = (
                db.query(PathItem.order_index)
                .filter(PathItem.learning_path_id == learning_path_id)
                .order_by(PathItem.order_index.desc())
                .first()
            )
            order_index = (max_pos[0] + 1) if max_pos else 1

        item = PathItem(
            learning_path_id=learning_path_id,
            resource_id=resource_id,
            order_index=order_index,
            stage=stage,
            purpose=purpose,
            estimated_time=estimated_time,
            is_optional=bool(is_optional) if is_optional is not None else False,
            manual_weight=manual_weight,
        )

        db.add(item)
        try:
            db.commit()
            db.refresh(item)
        except IntegrityError:
            db.rollback()
            raise ValueError(
                "Duplicate path item: order_index or resource already exists in this learning path"
            )

        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to add resource to learning path: {e}")
        return item

    @staticmethod
    def remove_resource_from_learning_path(
        db: Session,
        learning_path_id: int,
        resource_id: int,
    ) -> bool:
        item = (
            db.query(PathItem)
            .filter(
                PathItem.learning_path_id == learning_path_id,
                PathItem.resource_id == resource_id,
            )
            .first()
        )
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    @staticmethod
    def get_learning_path_with_items(
        db: Session, learning_path_id: int
    ) -> Optional[LearningPath]:
        # 预加载 path_items、资源对象、以及 category，按照 order_index 排序
        lp = (
            db.query(LearningPath)
            .options(
                joinedload(LearningPath.category),
                joinedload(LearningPath.path_items).joinedload(PathItem.resource)
            )
            .filter(LearningPath.id == learning_path_id)
            .first()
        )
        return lp

    @staticmethod
    def fork_learning_path(
        db: Session,
        source_learning_path_id: int,
        user_id: int,
    ) -> LearningPath:
        """Fork a learning path: create a copy owned by the current user."""
        # Get source path with items
        source = (
            db.query(LearningPath)
            .options(joinedload(LearningPath.path_items))
            .filter(LearningPath.id == source_learning_path_id)
            .first()
        )
        if not source:
            raise ValueError("LearningPath not found")

        # Determine root_id (the original source of the fork lineage)
        source_root_id = getattr(source, "root_id", None) or source.id

        # Create new forked path
        forked_path = LearningPath(
            title=source.title,
            type=getattr(source, "type", None),
            description=source.description,
            is_public=False,  # Forked paths are private by default
            cover_image_url=getattr(source, "cover_image_url", None),
            category_id=source.category_id,
            creator_id=user_id,
            parent_id=source_learning_path_id,
            root_id=source_root_id,
            status="draft",
        )
        db.add(forked_path)

        # Increment fork_count on source path
        source.fork_count = (getattr(source, "fork_count", 0) or 0) + 1

        db.commit()
        db.refresh(forked_path)

        # Copy all path items to the new path
        for item in source.path_items:
            new_item = PathItem(
                learning_path_id=forked_path.id,
                resource_id=item.resource_id,
                order_index=item.order_index,
                stage=getattr(item, "stage", None),
                purpose=getattr(item, "purpose", None),
                estimated_time=getattr(item, "estimated_time", None),
                is_optional=bool(getattr(item, "is_optional", False)),
                manual_weight=getattr(item, "manual_weight", None),
            )
            db.add(new_item)

        # Add user association
        user_learning_path = UserLearningPath(
            user_id=user_id, learning_path_id=forked_path.id
        )
        db.add(user_learning_path)

        db.commit()
        db.refresh(forked_path)

        return forked_path

    @staticmethod
    def get_user_path_status(
        db: Session,
        learning_path_id: int,
        user_id: int,
    ) -> dict:
        """Check if path is saved (attached) or forked by user."""
        # Check if user has attached this path (saved)
        is_saved = (
            db.query(UserLearningPath)
            .filter(
                UserLearningPath.user_id == user_id,
                UserLearningPath.learning_path_id == learning_path_id,
            )
            .first()
            is not None
        )

        # Check if user has already forked this path
        has_forked = (
            db.query(LearningPath)
            .filter(
                LearningPath.parent_id == learning_path_id,
                LearningPath.creator_id == user_id,
            )
            .first()
            is not None
        )

        return {"is_saved": is_saved, "has_forked": has_forked}
