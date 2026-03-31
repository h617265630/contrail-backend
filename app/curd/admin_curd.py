from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from app.models.rbac.user import User
from app.models.learning_path import LearningPath
from app.models.resource import Resource
from app.models.category import Category
from app.models.user_learning_path import UserLearningPath
from app.schemas.admin import (
    AdminStatsResponse,
    AdminUserItem,
    AdminLearningPathItem,
    AdminResourceItem,
    AdminAnalyticsResponse,
    DailyCountItem,
    CategoryCountItem,
    TopResourceItem,
)


class AdminCURD:
    @staticmethod
    def get_stats(db: Session) -> AdminStatsResponse:
        now = datetime.now()
        week_ago = now - timedelta(days=7)

        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        users_last_7_days = (
            db.query(func.count(User.id)).filter(User.created_at >= week_ago).scalar() or 0
        )

        total_learning_paths = db.query(func.count(LearningPath.id)).scalar() or 0
        public_learning_paths = (
            db.query(func.count(LearningPath.id)).filter(LearningPath.is_public == True).scalar() or 0
        )
        paths_last_7_days = 0  # TODO: needs created_at column in learning_paths table

        total_resources = db.query(func.count(Resource.id)).scalar() or 0
        resources_last_7_days = (
            db.query(func.count(Resource.id)).filter(Resource.created_at >= week_ago).scalar() or 0
        )

        total_categories = db.query(func.count(Category.id)).scalar() or 0

        return AdminStatsResponse(
            total_users=total_users,
            active_users=active_users,
            total_learning_paths=total_learning_paths,
            public_learning_paths=public_learning_paths,
            total_resources=total_resources,
            total_categories=total_categories,
            users_last_7_days=users_last_7_days,
            paths_last_7_days=paths_last_7_days,
            resources_last_7_days=resources_last_7_days,
        )

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> Tuple[List[AdminUserItem], int]:
        query = db.query(User)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_pattern))
                | (User.email.ilike(search_pattern))
                | (User.display_name.ilike(search_pattern))
            )

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if is_superuser is not None:
            query = query.filter(User.is_superuser == is_superuser)

        total = query.count()
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

        user_items = []
        for user in users:
            roles = [role.name for role in user.roles] if user.roles else []
            user_items.append(
                AdminUserItem(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    display_name=user.display_name,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser,
                    created_at=user.created_at,
                    roles=roles,
                )
            )

        return user_items, total

    @staticmethod
    def toggle_user_status(db: Session, user_id: int) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = not user.is_active
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def toggle_superuser_status(db: Session, user_id: int) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_superuser = not user.is_superuser
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def get_learning_paths(
        db: Session, skip: int = 0, limit: int = 20
    ) -> Tuple[List[AdminLearningPathItem], int]:
        query = db.query(LearningPath)
        total = query.count()
        paths = query.order_by(LearningPath.created_at.desc()).offset(skip).limit(limit).all()

        path_items = []
        for path in paths:
            user_count = (
                db.query(func.count(UserLearningPath.user_id))
                .filter(UserLearningPath.learning_path_id == path.id)
                .scalar()
                or 0
            )
            path_items.append(
                AdminLearningPathItem(
                    id=path.id,
                    title=path.title,
                    is_public=path.is_public,
                    is_active=path.is_active,
                    category_name=path.category_name,
                    created_at=path.created_at,
                    user_count=user_count,
                )
            )

        return path_items, total

    @staticmethod
    def delete_learning_path(db: Session, path_id: int) -> bool:
        path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
        if path:
            db.delete(path)
            db.commit()
            return True
        return False

    @staticmethod
    def get_resources(
        db: Session, skip: int = 0, limit: int = 20
    ) -> Tuple[List[AdminResourceItem], int]:
        query = db.query(Resource)
        total = query.count()
        resources = query.order_by(Resource.created_at.desc()).offset(skip).limit(limit).all()

        resource_items = []
        for resource in resources:
            resource_items.append(
                AdminResourceItem(
                    id=resource.id,
                    title=resource.title,
                    resource_type=resource.resource_type,
                    platform=resource.platform,
                    category_name=resource.category_name,
                    save_count=resource.save_count,
                    trending_score=resource.trending_score,
                    created_at=resource.created_at,
                )
            )

        return resource_items, total

    @staticmethod
    def delete_resource(db: Session, resource_id: int) -> bool:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if resource:
            db.delete(resource)
            db.commit()
            return True
        return False

    @staticmethod
    def get_analytics(db: Session, days: int = 30) -> AdminAnalyticsResponse:
        now = datetime.now()
        start_date = now - timedelta(days=days)

        # Daily users
        daily_users_data = (
            db.query(
                    func.date(User.created_at).label("date"),
                    func.count(User.id).label("count"),
                )
                .filter(User.created_at >= start_date)
                .group_by(func.date(User.created_at))
                .order_by(func.date(User.created_at))
                .all()
        )
        daily_users = [
            DailyCountItem(date=str(row.date), count=row.count) for row in daily_users_data
        ]

        # Daily learning paths
        daily_paths_data = (
            db.query(
                    func.date(LearningPath.created_at).label("date"),
                    func.count(LearningPath.id).label("count"),
                )
                .filter(LearningPath.created_at >= start_date)
                .group_by(func.date(LearningPath.created_at))
                .order_by(func.date(LearningPath.created_at))
                .all()
        )
        daily_paths = [
            DailyCountItem(date=str(row.date), count=row.count) for row in daily_paths_data
        ]

        # Daily resources
        daily_resources_data = (
            db.query(
                    func.date(Resource.created_at).label("date"),
                    func.count(Resource.id).label("count"),
                )
                .filter(Resource.created_at >= start_date)
                .group_by(func.date(Resource.created_at))
                .order_by(func.date(Resource.created_at))
                .all()
        )
        daily_resources = [
            DailyCountItem(date=str(row.date), count=row.count) for row in daily_resources_data
        ]

        # Top categories by resource count
        top_categories_data = (
            db.query(Category.name, func.count(Resource.id).label("count"))
            .join(Resource, Resource.category_id == Category.id)
            .group_by(Category.name)
            .order_by(func.count(Resource.id).desc())
            .limit(10)
            .all()
        )
        top_categories = [
            CategoryCountItem(name=row.name, count=row.count) for row in top_categories_data
        ]

        # Top resources by save_count
        top_resources_data = (
            db.query(Resource.title, Resource.save_count)
            .order_by(Resource.save_count.desc())
            .limit(10)
            .all()
        )
        top_resources = [
            TopResourceItem(title=row.title, save_count=row.save_count)
            for row in top_resources_data
        ]

        return AdminAnalyticsResponse(
            daily_users=daily_users,
            daily_paths=daily_paths,
            daily_resources=daily_resources,
            top_categories=top_categories,
            top_resources=top_resources,
        )
