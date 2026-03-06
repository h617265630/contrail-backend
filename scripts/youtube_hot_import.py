"""按分类抓取 YouTube 热门视频 URL，并批量写入 resources(link_resources) 表。

使用官方 YouTube Data API v3（需要 API Key），不做页面爬取。

用法示例：
  cd backend
  export YOUTUBE_API_KEY="..."
  python scripts/youtube_hot_import.py --region CN --max-results 20 --category-id 27 --category-id 28

可选：绑定到某个用户的 /my-resources（写 user_resource 关联）
  python scripts/youtube_hot_import.py --user-id 1 --region US --max-results 10 --category-id 28

注意：
- 已存在的 url 会跳过（或补全缺失字段）。
- 默认写入 is_public=True。
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Any, Iterable

import httpx

# Ensure "app" package import works when running from repo root.
HERE = os.path.abspath(os.path.dirname(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(HERE, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.db.database import SessionLocal  # noqa: E402
from app.models.resource import ResourceType  # noqa: E402
from app.models.resources.link import LinkResource  # noqa: E402
from app.models.user_resource import UserResource  # noqa: E402


@dataclass(frozen=True)
class YouTubeVideo:
    video_id: str
    title: str
    description: str | None
    thumbnail_url: str | None

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


def _yt_api_key(cli_key: str | None) -> str:
    key = (cli_key or os.getenv("YOUTUBE_API_KEY") or "").strip()
    if not key:
        raise SystemExit(
            "缺少 YouTube API Key：请设置环境变量 YOUTUBE_API_KEY 或传入 --api-key"
        )
    return key


def fetch_most_popular(
    *,
    api_key: str,
    region: str,
    category_id: str,
    max_results: int,
) -> list[YouTubeVideo]:
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": api_key,
        "part": "snippet",
        "chart": "mostPopular",
        "regionCode": region,
        "videoCategoryId": category_id,
        "maxResults": str(max_results),
    }

    with httpx.Client(timeout=20.0) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    out: list[YouTubeVideo] = []
    for item in data.get("items", []) or []:
        vid = (item.get("id") or "").strip()
        if not vid:
            continue
        snip = item.get("snippet") or {}
        title = (snip.get("title") or "").strip() or f"YouTube Video {vid}"
        description = (snip.get("description") or "").strip() or None
        thumbs = snip.get("thumbnails") or {}
        thumb_url = (
            (thumbs.get("maxres") or {}).get("url")
            or (thumbs.get("standard") or {}).get("url")
            or (thumbs.get("high") or {}).get("url")
            or (thumbs.get("medium") or {}).get("url")
            or (thumbs.get("default") or {}).get("url")
        )
        out.append(
            YouTubeVideo(
                video_id=vid,
                title=title,
                description=description,
                thumbnail_url=(thumb_url.strip() if isinstance(thumb_url, str) else None),
            )
        )
    return out


def fetch_category_title(*, api_key: str, region: str, category_id: str) -> str | None:
    url = "https://www.googleapis.com/youtube/v3/videoCategories"
    params = {
        "key": api_key,
        "part": "snippet",
        "id": category_id,
        "regionCode": region,
    }
    with httpx.Client(timeout=20.0) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    items = data.get("items") or []
    if not items:
        return None
    snip = (items[0].get("snippet") or {})
    title = (snip.get("title") or "").strip()
    return title or None


def upsert_link_resource(
    *,
    db,
    video: YouTubeVideo,
    category_label: str,
    is_public: bool,
) -> tuple[LinkResource, bool]:
    existing = db.query(LinkResource).filter(LinkResource.url == video.url).first()
    if existing:
        changed = False
        if video.title and (not existing.title or existing.title.startswith("YouTube Video ")):
            existing.title = video.title
            changed = True
        if video.description and not existing.description:
            existing.description = video.description
            changed = True
        if video.thumbnail_url and not existing.thumbnail_url:
            existing.thumbnail_url = video.thumbnail_url
            changed = True
        if category_label and not existing.category:
            existing.category = category_label
            changed = True
        if existing.is_public is None or existing.is_public != bool(is_public):
            existing.is_public = bool(is_public)
            changed = True
        db.add(existing)
        db.flush()
        return existing, False

    obj = LinkResource(
        title=video.title,
        description=video.description,
        resource_type=LinkResource.__mapper_args__["polymorphic_identity"],
        url=video.url,
        source="youtube.com",
        category=category_label,
        thumbnail_url=video.thumbnail_url,
        is_public=bool(is_public),
        is_active=True,
    )
    # Make sure polymorphic type is correct even if caller changes defaults.
    obj.resource_type = ResourceType.LINK

    db.add(obj)
    db.flush()
    return obj, True


def attach_to_user_if_needed(*, db, user_id: int | None, resource_id: int) -> None:
    if not user_id:
        return
    hit = (
        db.query(UserResource)
        .filter(UserResource.user_id == user_id, UserResource.resource_id == resource_id)
        .first()
    )
    if hit:
        return
    db.add(UserResource(user_id=user_id, resource_id=resource_id))
    db.flush()


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--api-key", default=None, help="YouTube Data API key（也可用环境变量 YOUTUBE_API_KEY）")
    p.add_argument("--region", default="US", help="地区代码，如 US/CN/JP")
    p.add_argument("--max-results", type=int, default=20, help="每个分类抓取数量（1-50）")
    p.add_argument(
        "--category-id",
        action="append",
        default=[],
        help="YouTube videoCategoryId（可重复传入）",
    )
    p.add_argument(
        "--store-category",
        default="youtube",
        choices=["youtube", "id"],
        help="写入 resources.category 的内容：youtube=分类标题；id=分类ID",
    )
    p.add_argument(
        "--category-prefix",
        default="",
        help="写入 resources.category 的前缀（例如 'YouTube/'）",
    )
    p.add_argument(
        "--user-id",
        type=int,
        default=None,
        help="可选：把资源同时挂到某个用户的 my-resources（写 user_resource 关联）",
    )
    p.add_argument(
        "--public",
        dest="is_public",
        action="store_true",
        default=True,
        help="写入 is_public=true（默认）",
    )
    p.add_argument(
        "--private",
        dest="is_public",
        action="store_false",
        help="写入 is_public=false",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="只抓取不入库",
    )
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    api_key = _yt_api_key(args.api_key)

    if not args.category_id:
        raise SystemExit("请至少传入一个 --category-id（例如 27=Education, 28=Science & Technology）")

    if args.max_results < 1 or args.max_results > 50:
        raise SystemExit("--max-results 需要在 1-50 之间")

    totals_created = 0
    totals_seen = 0

    with SessionLocal() as db:
        for cid in args.category_id:
            cid = str(cid).strip()
            if not cid:
                continue

            yt_title = None
            if args.store_category == "youtube":
                try:
                    yt_title = fetch_category_title(api_key=api_key, region=args.region, category_id=cid)
                except Exception:
                    yt_title = None

            if args.store_category == "youtube":
                label = yt_title or f"YouTube/{cid}"
            else:
                label = str(cid)

            if args.category_prefix:
                label = f"{args.category_prefix}{label}"

            videos = fetch_most_popular(
                api_key=api_key,
                region=args.region,
                category_id=cid,
                max_results=args.max_results,
            )

            if args.dry_run:
                print(f"[dry-run] category {cid}: {len(videos)} urls")
                totals_seen += len(videos)
                continue

            created = 0
            for v in videos:
                totals_seen += 1
                obj, is_new = upsert_link_resource(
                    db=db,
                    video=v,
                    category_label=label,
                    is_public=args.is_public,
                )
                attach_to_user_if_needed(db=db, user_id=args.user_id, resource_id=obj.id)
                if is_new:
                    created += 1

            db.commit()
            totals_created += created
            print(f"category {cid}: fetched={len(videos)} created={created} stored_category='{label}'")

    print(f"done: fetched_total={totals_seen} created_total={totals_created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
