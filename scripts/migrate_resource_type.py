import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.resource import Resource
from app.models.resources.video import Video
from app.models.resources.article import Article


def _resource_type_value(obj: Resource) -> str:
    rt = getattr(obj, "resource_type", None)
    return (rt.value if hasattr(rt, "value") else str(rt or "")).strip().lower()


def migrate_resource_to_video(db: Session, *, resource_id: int, apply: bool) -> None:
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise ValueError(f"Resource {resource_id} not found")

    current = _resource_type_value(res)
    raw_meta = getattr(res, "raw_meta", None) or {}

    existing_video = db.query(Video).filter(Video.resource_id == resource_id).first()
    existing_article = db.query(Article).filter(Article.resource_id == resource_id).first()

    duration = raw_meta.get("duration_seconds")
    channel = raw_meta.get("author")
    video_id = raw_meta.get("video_id")

    try:
        duration = int(duration) if duration is not None else None
    except Exception:
        duration = None

    print("-- migrate_resource_to_video")
    print("resource_id:", resource_id)
    print("current resource_type:", current)
    print("has Article row:", bool(existing_article))
    print("has Video row:", bool(existing_video))
    print("raw_meta.duration_seconds:", raw_meta.get("duration_seconds"))
    print("raw_meta.author:", raw_meta.get("author"))
    print("raw_meta.video_id:", raw_meta.get("video_id"))
    print("will set duration/channel/video_id:", duration, channel, video_id)
    print("apply:", apply)

    if not apply:
        print("DRY RUN: no changes made")
        return

    # 1) Set resource_type
    res.resource_type = "video"

    # 2) Remove incompatible typed rows
    if existing_article:
        db.delete(existing_article)

    # 3) Ensure Video row exists
    if not existing_video:
        existing_video = Video(resource_id=resource_id)
        db.add(existing_video)

    existing_video.duration = duration
    existing_video.channel = channel
    existing_video.video_id = video_id

    db.commit()

    # Print final state
    db.refresh(res)
    final_type = _resource_type_value(res)
    print("DONE. final resource_type:", final_type)


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate an existing resource to type=video safely")
    parser.add_argument("--resource-id", type=int, required=True)
    parser.add_argument("--apply", action="store_true", help="Actually apply DB changes")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        migrate_resource_to_video(db, resource_id=args.resource_id, apply=bool(args.apply))
    finally:
        db.close()


if __name__ == "__main__":
    main()
