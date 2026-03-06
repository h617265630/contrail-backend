import argparse
import sys
from pathlib import Path

# Ensure backend dir is on sys.path so we can import project modules
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import or_

from app.db.database import SessionLocal
from app.models.resource import Resource
from app.models.user_resource import UserResource
from app.models.path_item import PathItem
from app.models.resources.video import Video
from app.models.resources.doc import Doc
from app.models.resources.article import Article


def main() -> int:
    parser = argparse.ArgumentParser(description="Delete langchain-related resources from DB.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete rows. Without this flag, runs in dry-run mode.",
    )
    parser.add_argument(
        "--query",
        default="langchain",
        help="Case-insensitive substring to match against title/summary/source_url/platform.",
    )
    args = parser.parse_args()

    q = str(args.query or "").strip()
    if not q:
        print("Empty query is not allowed.")
        return 2

    db = SessionLocal()
    try:
        # Find candidate resources
        like = f"%{q}%"
        resources = (
            db.query(Resource)
            .filter(
                or_(
                    Resource.title.ilike(like),
                    Resource.summary.ilike(like),
                    Resource.source_url.ilike(like),
                    Resource.platform.ilike(like),
                )
            )
            .order_by(Resource.id.asc())
            .all()
        )

        if not resources:
            print(f"No resources matched query: {q!r}")
            return 0

        ids = [r.id for r in resources]
        print(f"Matched {len(ids)} resources for query {q!r}:")
        for r in resources:
            print(f" - id={r.id} platform={r.platform!r} title={r.title!r} url={r.source_url!r}")

        if not args.apply:
            print("\nDry-run only. Re-run with --apply to delete.")
            return 0

        # Delete dependent rows first to avoid FK issues.
        # (Some tables have ON DELETE CASCADE, but we keep explicit deletes to be safe.)
        db.query(UserResource).filter(UserResource.resource_id.in_(ids)).delete(synchronize_session=False)
        db.query(PathItem).filter(PathItem.resource_id.in_(ids)).delete(synchronize_session=False)

        db.query(Video).filter(Video.resource_id.in_(ids)).delete(synchronize_session=False)
        db.query(Doc).filter(Doc.resource_id.in_(ids)).delete(synchronize_session=False)
        db.query(Article).filter(Article.resource_id.in_(ids)).delete(synchronize_session=False)

        db.query(Resource).filter(Resource.id.in_(ids)).delete(synchronize_session=False)

        db.commit()
        print(f"\nDeleted {len(ids)} resources and related rows.")
        return 0
    except Exception as e:
        db.rollback()
        print(f"Error: {e!r}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
