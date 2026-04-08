from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Tuple
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
            creator_id=user_id,  # 标记创建者
        )
        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)

        # 创建关联记录
        user_learning_path = UserLearningPath(user_id=user_id, learning_path_id=learning_path.id)
        try:
            db.add(user_learning_path)
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("This learning path is already associated with the user.")

        return learning_path

    @staticmethod
    def list_public_learning_paths(db: Session, skip: int = 0, limit: int = 100) -> List[LearningPath]:
        return (
            db.query(LearningPath)
            .filter(LearningPath.is_public.is_(True))
            .filter(LearningPath.is_active.is_(True))
            .filter(LearningPath.status == "published")
            .options(joinedload(LearningPath.path_items))
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
            .join(UserLearningPath, UserLearningPath.learning_path_id == LearningPath.id)
            .filter(UserLearningPath.user_id == user_id)
            .options(joinedload(LearningPath.path_items))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return learning_paths

    @staticmethod
    def get_learning_paths_by_user_with_assoc(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Tuple[LearningPath, UserLearningPath]]:
        """返回 (LearningPath, UserLearningPath) 对，用于合并 custom_* 覆盖字段"""
        rows = (
            db.query(LearningPath, UserLearningPath)
            .join(UserLearningPath, UserLearningPath.learning_path_id == LearningPath.id)
            .filter(UserLearningPath.user_id == user_id)
            .options(joinedload(LearningPath.path_items))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return rows


    @staticmethod
    def get_learning_path(db: Session, learning_path_id: int) -> Optional[LearningPath]:
        return db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
    


    
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
                db.query(Progress).filter(Progress.path_item_id.in_(path_item_ids)).delete(synchronize_session=False)

            # 2) Delete join table associations.
            db.query(UserLearningPath).filter(UserLearningPath.learning_path_id == lp_id).delete(synchronize_session=False)

            # 3) Delete path items.
            db.query(PathItem).filter(PathItem.learning_path_id == lp_id).delete(synchronize_session=False)

            # 4) Finally delete the learning path.
            db.delete(learning_path)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Failed to delete learning path due to integrity constraints: {e}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to delete learning path: {e}")

    @staticmethod
    def update_user_learning_path(
        db: Session,
        user_id: int,
        learning_path_id: int,
        custom_title: Optional[str] = None,
        custom_description: Optional[str] = None,
        custom_cover_image_url: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Tuple[LearningPath, UserLearningPath]:
        """更新用户收藏路径。

        逻辑：
        - 用户是创建者（creator_id == user_id）：直接修改 LearningPath 原始字段
        - 用户是收藏者：写入 UserLearningPath.custom_* 覆盖字段，不影响原始路径
        """
        lp = db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()
        if not lp:
            raise ValueError("Learning path not found")

        assoc = (
            db.query(UserLearningPath)
            .filter(
                UserLearningPath.user_id == user_id,
                UserLearningPath.learning_path_id == learning_path_id,
            )
            .first()
        )
        if not assoc:
            raise ValueError("UserLearningPath association not found")

        is_creator = getattr(lp, "creator_id", None) == user_id

        if is_creator:
            # 创建者 → 直接修改 LearningPath
            if custom_title is not None:
                lp.title = custom_title.strip()
            if custom_description is not None:
                lp.description = custom_description.strip() or None
            if custom_cover_image_url is not None:
                lp.cover_image_url = custom_cover_image_url.strip() or None
            db.add(lp)
        else:
            # 收藏者 → 写入 custom_* 覆盖字段
            if custom_title is not None:
                assoc.custom_title = custom_title.strip() or None
            if custom_description is not None:
                assoc.custom_description = custom_description.strip() or None
            if custom_cover_image_url is not None:
                assoc.custom_cover_image_url = custom_cover_image_url.strip() or None
            if notes is not None:
                assoc.notes = notes.strip() or None
            db.add(assoc)

        db.flush()
        return lp, assoc

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
        )

        db.add(item)
        try:
            db.commit()
            db.refresh(item)
        except IntegrityError:
            db.rollback()
            raise ValueError("Duplicate path item: order_index or resource already exists in this learning path")

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
        # 预加载 path_items 以及资源对象，按照 order_index 排序
        lp = (
            db.query(LearningPath)
            .options(
                joinedload(LearningPath.path_items).joinedload(PathItem.resource)
            )
            .filter(LearningPath.id == learning_path_id)
            .first()
        )
        return lp

    @staticmethod
    def fork_learning_path(
        db: Session,
        source_path_id: int,
        user_id: int,
    ) -> LearningPath:
        """Fork 一条 learning path，返回新 path"""
        source = db.query(LearningPath).filter(LearningPath.id == source_path_id).first()
        if not source:
            raise ValueError("Learning path not found")

        # root_id：如果 source 本身是 fork 来的，沿用它的 root；否则 source 就是 root
        root_id = source.root_id if source.root_id else source.id

        # 1. 创建新 path
        new_path = LearningPath(
            title=source.title,
            type=source.type,
            description=source.description,
            is_public=False,
            is_active=True,
            cover_image_url=source.cover_image_url,
            category_id=source.category_id,
            creator_id=user_id,
            parent_id=source.id,
            root_id=root_id,
            status="draft",
        )
        db.add(new_path)
        db.flush()  # 获取 new_path.id

        # 2. 深拷贝 path_items
        for item in source.path_items:
            new_item = PathItem(
                learning_path_id=new_path.id,
                resource_id=item.resource_id,
                order_index=item.order_index,
                stage=item.stage,
                purpose=item.purpose,
                estimated_time=item.estimated_time,
                is_optional=item.is_optional,
            )
            db.add(new_item)

        # 3. 创建用户关联
        user_lp = UserLearningPath(user_id=user_id, learning_path_id=new_path.id)
        db.add(user_lp)

        # 4. 记录 fork 关系 + 更新计数
        from app.models.learning_path_fork import LearningPathFork
        fork_record = LearningPathFork(
            source_path_id=source.id,
            forked_path_id=new_path.id,
            user_id=user_id,
        )
        db.add(fork_record)

        source.fork_count = (source.fork_count or 0) + 1

        db.commit()
        db.refresh(new_path)
        return new_path