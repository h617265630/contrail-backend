from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.resource_summary_cache import ResourceSummaryCache


class ResourceSummaryCacheCURD:
    @staticmethod
    def _make_key(url: str, topic: str) -> str:
        """Stable hash key for a (url, topic) pair."""
        raw = f"{url.strip().lower()}::{topic.strip().lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:64]

    @staticmethod
    def get(db: Session, *, url: str, topic: str) -> ResourceSummaryCache | None:
        key = ResourceSummaryCacheCURD._make_key(url, topic)
        return db.query(ResourceSummaryCache).filter(
            ResourceSummaryCache.cache_key == key
        ).first()

    @staticmethod
    def upsert(
        db: Session,
        *,
        url: str,
        topic: str,
        title: str | None,
        summary: str,
        key_points: list[str],
        difficulty: str | None,
        resource_type: str | None,
        learning_stage: str | None,
        estimated_minutes: int | None,
        image: str | None,
    ) -> ResourceSummaryCache:
        key = ResourceSummaryCacheCURD._make_key(url, topic)
        existing = db.query(ResourceSummaryCache).filter(
            ResourceSummaryCache.cache_key == key
        ).first()

        now = datetime.utcnow()
        if existing:
            existing.title = title
            existing.summary = summary
            existing.key_points = json.dumps(key_points)
            existing.difficulty = difficulty
            existing.resource_type = resource_type
            existing.learning_stage = learning_stage
            existing.estimated_minutes = estimated_minutes
            existing.image = image
            existing.fetched_at = now
            db.add(existing)
            return existing

        obj = ResourceSummaryCache(
            cache_key=key,
            url=url,
            topic=topic,
            title=title,
            summary=summary,
            key_points=json.dumps(key_points),
            difficulty=difficulty,
            resource_type=resource_type,
            learning_stage=learning_stage,
            estimated_minutes=estimated_minutes,
            image=image,
            fetched_at=now,
        )
        db.add(obj)
        return obj

    @staticmethod
    def get_multi_by_topic(db: Session, *, topic: str, limit: int = 100) -> list[ResourceSummaryCache]:
        return (
            db.query(ResourceSummaryCache)
            .filter(ResourceSummaryCache.topic == topic.strip().lower())
            .order_by(ResourceSummaryCache.fetched_at.desc())
            .limit(limit)
            .all()
        )
