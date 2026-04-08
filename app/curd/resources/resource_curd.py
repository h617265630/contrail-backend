from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional, Tuple
from urllib.parse import urlparse
from html import unescape
import re
import time

import httpx

from sqlalchemy.orm import Session

from pytube import YouTube

from app.models.resource import Resource
from app.models.category import Category
from app.models.resources.video import Video
from app.models.resources.doc import Doc
from app.models.resources.article import Article
from app.models.user_resource import UserResource


class ResourceCURD:
    # Best-effort in-process cache for extraction results.
    # This dramatically reduces latency for repeated opens of the same resource detail.
    _EXTRACT_CACHE_TTL_SECONDS = 10 * 60
    _extract_cache: dict[str, tuple[float, dict]] = {}
    _TITLE_MAX_LENGTH = 500

    @staticmethod
    def _normalize_title(value: str | None, fallback_url: str) -> str:
        raw = (value or "").strip()
        if not raw:
            raw = ResourceCURD._guess_title_from_url(fallback_url)
        if len(raw) <= ResourceCURD._TITLE_MAX_LENGTH:
            return raw
        return raw[: ResourceCURD._TITLE_MAX_LENGTH - 1].rstrip() + "…"

    @staticmethod
    def _youtube_video_id(url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
        except Exception:
            return None

        host = (parsed.hostname or "").lower()
        if host.endswith("youtu.be"):
            vid = (parsed.path or "").lstrip("/")
            return vid or None

        # youtube.com/watch?v=...
        if host.endswith("youtube.com"):
            qs = parsed.query or ""
            m = re.search(r"(?:^|&)v=([^&]+)", qs)
            if m:
                return m.group(1)
            # fallback: /embed/{id}
            parts = [p for p in (parsed.path or "").split("/") if p]
            if len(parts) >= 2 and parts[0] in {"embed", "shorts"}:
                return parts[1]
        return None

    @staticmethod
    def _youtube_thumbnail(video_id: str | None) -> str | None:
        if not video_id:
            return None
        vid = (video_id or "").strip()
        if not vid:
            return None
        return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

    @staticmethod
    def _parse_chapters_from_description(description: Optional[str]) -> list[dict]:
        if not description:
            return []

        # Common patterns:
        # 00:00 Intro
        # 0:00 - Intro
        # 1:02:03 Chapter name
        ts_re = re.compile(
            r"^(?P<ts>(?:\d{1,2}:)?\d{1,2}:\d{2})\s*(?:[-–—]|\)|\]|\s)\s*(?P<title>.+?)\s*$"
        )

        def to_seconds(ts: str) -> int:
            parts = [int(p) for p in ts.split(":")]
            if len(parts) == 2:
                mm, ss = parts
                return mm * 60 + ss
            if len(parts) == 3:
                hh, mm, ss = parts
                return hh * 3600 + mm * 60 + ss
            return 0

        chapters: list[dict] = []
        for raw_line in description.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            m = ts_re.match(line)
            if not m:
                continue
            ts = m.group("ts")
            title = m.group("title").strip()
            if not title:
                continue
            chapters.append(
                {
                    "start_seconds": to_seconds(ts),
                    "timestamp": ts,
                    "title": title,
                    "description": None,
                }
            )

        # De-dup & sort by time
        seen = set()
        uniq: list[dict] = []
        for ch in sorted(chapters, key=lambda x: x["start_seconds"]):
            key = (ch["start_seconds"], ch["title"].lower())
            if key in seen:
                continue
            seen.add(key)
            uniq.append(ch)
        return uniq

    @staticmethod
    def _is_youtube(url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return host.endswith("youtube.com") or host.endswith("youtu.be")

    @staticmethod
    def _normalize_platform(host: str | None, site_name: str | None = None) -> str | None:
        raw_host = (host or "").lower().removeprefix("www.")
        if not raw_host and site_name:
            raw_host = site_name.strip().lower().replace(" ", "")

        # X/Twitter
        if raw_host.endswith("x.com") or raw_host.endswith("twitter.com"):
            return "x"

        # Instagram
        if raw_host.endswith("instagram.com"):
            return "instagram"

        # Normalize common platforms
        if raw_host.endswith("bilibili.com"):
            return "bilibili"
        if raw_host.endswith("xiaohongshu.com") or raw_host.endswith("xhslink.com"):
            return "xiaohongshu"
        if raw_host.endswith("medium.com"):
            return "medium"
        if raw_host.endswith("reddit.com"):
            return "reddit"
        if raw_host.endswith("github.com"):
            return "github"
        if raw_host.endswith("substack.com"):
            return "substack"

        return raw_host or None

    @staticmethod
    def _is_x(url: str) -> bool:
        host = (urlparse(url).hostname or "").lower().removeprefix("www.")
        return host.endswith("x.com") or host.endswith("twitter.com")

    @staticmethod
    def _x_status_id(url: str) -> str | None:
        """Extract numeric status id from X/Twitter URLs.

        Supports:
        - https://x.com/{user}/status/{id}
        - https://twitter.com/{user}/status/{id}
        - https://x.com/i/web/status/{id}
        """
        raw = (url or "").strip()
        if not raw:
            return None
        path = (urlparse(raw).path or "").strip()
        if not path:
            return None

        m = re.search(r"/status/(?P<id>\d+)", path)
        if m:
            return m.group("id")
        m = re.search(r"/i/web/status/(?P<id>\d+)", path)
        if m:
            return m.group("id")
        return None

    @staticmethod
    def _parse_publish_date_to_iso(value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            try:
                return value.isoformat()
            except Exception:
                return None
        s = str(value).strip()
        if not s:
            return None
        # already iso-ish
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return dt.isoformat()
        except Exception:
            pass
        # RFC822-ish (common for tweet timestamps)
        try:
            dt = parsedate_to_datetime(s)
            return dt.isoformat()
        except Exception:
            return None

    @staticmethod
    def _is_instagram(url: str) -> bool:
        host = (urlparse(url).hostname or "").lower().removeprefix("www.")
        return host.endswith("instagram.com")

    @staticmethod
    def _ig_shortcode(url: str) -> str | None:
        """Extract shortcode from Instagram URLs.

        Supports:
        - https://www.instagram.com/p/{code}/
        - https://www.instagram.com/reel/{code}/
        - https://www.instagram.com/tv/{code}/
        """
        path = (urlparse(url).path or "").strip()
        m = re.search(r"/(?:p|reel|tv)/([A-Za-z0-9_-]+)", path)
        return m.group(1) if m else None

    @staticmethod
    def _extract_instagram(url: str) -> dict:
        """Best-effort extraction for Instagram posts/reels/tv.

        Uses i.instagram.com/api/v1/oembed/ which returns JSON with
        thumbnail_url, title (caption), author_name, etc. — no API key needed.
        """
        raw = (url or "").strip()
        shortcode = ResourceCURD._ig_shortcode(raw)

        # ---- 1) Instagram oEmbed (reliable, returns thumbnail) ----
        try:
            with httpx.Client(
                timeout=10.0,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            ) as client:
                resp = client.get(
                    "https://i.instagram.com/api/v1/oembed/",
                    params={"url": raw},
                )
                resp.raise_for_status()
                data = resp.json() or {}

            caption = (data.get("title") or "").strip() or None
            author = (data.get("author_name") or "").strip() or None
            thumbnail_url = (data.get("thumbnail_url") or "").strip() or None
            media_id = (data.get("media_id") or "").strip() or shortcode

            # Detect if it's a video (reel/tv) from URL path
            path_lower = (urlparse(raw).path or "").lower()
            has_video = "/reel/" in path_lower or "/tv/" in path_lower

            # Build title
            if caption:
                short = re.sub(r"\s+", " ", caption)
                short = (short[:120] + "…") if len(short) > 120 else short
            else:
                short = f"Instagram post {shortcode or ''}"
            if author:
                title = f"@{author}: {short}"
            else:
                title = short

            return {
                "title": title,
                "description": caption,
                "thumbnail_url": thumbnail_url,
                "author": f"@{author}" if author else None,
                "publish_date": None,
                "video_id": shortcode or media_id,
                "duration_seconds": None,
                "platform": "instagram",
                "og_type": "video.other" if has_video else "article",
                "og_video": None,
                "twitter_player": None,
                "has_video": has_video,
                "chapters": [],
            }
        except Exception:
            pass

        # ---- 2) Final fallback: generic HTML meta ----
        meta = ResourceCURD._extract_generic_url(raw)
        meta.setdefault("platform", "instagram")
        meta.setdefault("video_id", shortcode)
        return meta

    @staticmethod
    def _extract_x_tweet(url: str) -> dict:
        """Best-effort extraction for X/Twitter status URLs.

        Strategy (no API key required):
        1) fxtwitter.com — a public embed-proxy that returns full OG meta (including
           og:image / og:video) when requested with a bot-like User-Agent.
        2) Twitter oEmbed — provides tweet text & author (but no image).
        3) Merge: fxtwitter gives thumbnail; oEmbed gives richer text/date.
        4) Final fallback: generic HTML meta.
        """
        raw = (url or "").strip()
        status_id = ResourceCURD._x_status_id(raw)
        if not status_id:
            return ResourceCURD._extract_generic_url(raw)

        # ---- helpers ----
        def _find_meta(html: str, *, name: str | None = None, prop: str | None = None) -> str | None:
            for attr, val in [("property", prop), ("name", name)]:
                if not val:
                    continue
                # content after attr
                m = re.search(
                    rf"<meta[^>]+{attr}=['\"]?{re.escape(val)}['\"]?[^>]+content=['\"](?P<c>[^'\"]+)['\"]",
                    html, flags=re.IGNORECASE,
                )
                if not m:
                    # content before attr
                    m = re.search(
                        rf"<meta[^>]+content=['\"](?P<c>[^'\"]+)['\"][^>]+{attr}=['\"]?{re.escape(val)}['\"]?",
                        html, flags=re.IGNORECASE,
                    )
                if m:
                    return unescape((m.group("c") or "").strip()) or None
            return None

        def _strip_tags(s: str) -> str:
            s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)
            s = re.sub(r"</p\s*>", "\n", s, flags=re.IGNORECASE)
            s = re.sub(r"<[^>]+>", "", s)
            return unescape(re.sub(r"\s+", " ", s)).strip()

        # ---- 1) fxtwitter.com  ----
        fx_title = fx_desc = fx_image = fx_video = None
        try:
            # Reconstruct path from original URL so user/status structure is kept.
            parsed = urlparse(raw)
            fx_url = f"https://fxtwitter.com{parsed.path}"
            # fxtwitter serves OG tags to bot-like User-Agents.
            with httpx.Client(timeout=8.0, follow_redirects=True, headers={"User-Agent": "bot"}) as client:
                resp = client.get(fx_url)
                resp.raise_for_status()
                fxhtml = resp.text or ""

            fx_title = _find_meta(fxhtml, prop="og:title")
            fx_desc = _find_meta(fxhtml, prop="og:description")
            fx_image = _find_meta(fxhtml, prop="og:image")
            fx_video = _find_meta(fxhtml, prop="og:video")
        except Exception:
            pass

        # ---- 2) oEmbed (richer text body & date) ----
        oembed_author = oembed_desc = oembed_date = None
        try:
            with httpx.Client(
                timeout=8.0, follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            ) as client:
                resp = client.get(
                    "https://publish.twitter.com/oembed",
                    params={"url": raw, "omit_script": "1"},
                )
                resp.raise_for_status()
                data = resp.json() or {}

            oembed_author = (data.get("author_name") or "").strip() or None
            html_fragment = (data.get("html") or "").strip() or ""

            m = re.search(r"<p\b[^>]*>(?P<p>.*?)</p>", html_fragment, flags=re.IGNORECASE | re.DOTALL)
            if m:
                oembed_desc = _strip_tags(m.group("p") or "") or None

            m_date = re.search(
                r"<a\b[^>]*href=['\"][^'\"]*/status/\d+[^'\"]*['\"][^>]*>(?P<t>[^<]+)</a>\s*</blockquote>",
                html_fragment, flags=re.IGNORECASE | re.DOTALL,
            )
            if m_date:
                dt_text = unescape((m_date.group("t") or "").strip())
                try:
                    oembed_date = datetime.strptime(dt_text, "%B %d, %Y").date().isoformat()
                except Exception:
                    oembed_date = None
        except Exception:
            pass

        # ---- 3) Merge results ----
        author = oembed_author or None
        description = oembed_desc or fx_desc or None
        thumbnail_url = (fx_image or "").strip() or None
        publish_date = oembed_date
        has_video = bool(fx_video)

        # Build title
        base_text = description or fx_title or f"X post {status_id}"
        short = re.sub(r"\s+", " ", base_text)
        short = (short[:120] + "…") if len(short) > 120 else short
        if author:
            title = f"{author}: {short}"
        else:
            title = short

        # If we got at least a title or description, return merged result.
        if description or fx_title or thumbnail_url:
            return {
                "title": title,
                "description": description,
                "thumbnail_url": thumbnail_url,
                "author": author,
                "publish_date": publish_date,
                "video_id": status_id,
                "duration_seconds": None,
                "platform": "x",
                "og_type": "video.other" if has_video else "article",
                "og_video": fx_video,
                "twitter_player": None,
                "has_video": has_video,
                "chapters": [],
            }

        # ---- 4) Final fallback: generic HTML meta ----
        meta = ResourceCURD._extract_generic_url(raw)
        meta.setdefault("platform", "x")
        meta.setdefault("video_id", status_id)
        return meta

    @staticmethod
    def _infer_resource_type(url: str, meta: dict) -> str:
        raw = (url or "").strip()
        base = raw.lower().split("?", 1)[0]
        if base.endswith(".pdf"):
            return "document"

        host = (urlparse(raw).hostname or "").lower().removeprefix("www.")
        if host.endswith("github.com"):
            return "document"

        # Known video platforms
        if ResourceCURD._is_youtube(raw):
            return "video"
        if host.endswith("bilibili.com"):
            return "video"
        if host.endswith("instagram.com"):
            path_lower = (urlparse(raw).path or "").lower()
            if "/reel/" in path_lower or "/tv/" in path_lower:
                return "video"
            return "article"
        if host.endswith("xiaohongshu.com") or host.endswith("xhslink.com"):
            # xiaohongshu links can be video or图文; default video for better UX
            return "video"

        og_type = str(meta.get("og_type") or "").strip().lower()
        if og_type.startswith("video"):
            return "video"

        # If page provides an embeddable player, treat as video
        if meta.get("og_video") or meta.get("twitter_player"):
            return "video"

        # If HTML indicates an inline video player but missing OG tags, treat as video
        if meta.get("has_video"):
            return "video"

        # Default
        return "article"

    @staticmethod
    def _guess_title_from_url(url: str) -> str:
        try:
            parsed = urlparse(url)
            host = (parsed.hostname or "").strip() or ""
            path = (parsed.path or "").strip() or ""
            name = (path.rsplit("/", 1)[-1] or "").strip()
            if name:
                return unescape(name)
            return host or "Link"
        except Exception:
            return "Link"

    @staticmethod
    def _extract_generic_url(url: str) -> dict:
        """Best-effort metadata extraction for non-YouTube links."""
        raw = (url or "").strip()
        if not raw:
            raise ValueError("Invalid URL")

        # Try a lightweight fetch to infer title/description/thumbnail.
        try:
            with httpx.Client(
                timeout=8.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
                },
            ) as client:
                resp = client.get(raw)
                resp.raise_for_status()
                content_type = (resp.headers.get("content-type") or "").lower()

                # PDF or binary: no HTML parsing.
                if "application/pdf" in content_type or raw.lower().split("?", 1)[0].endswith(".pdf"):
                    return {
                        "title": ResourceCURD._guess_title_from_url(raw),
                        "description": None,
                        "thumbnail_url": None,
                        "author": None,
                        "publish_date": None,
                        "video_id": None,
                        "duration_seconds": None,
                        "platform": (urlparse(raw).hostname or "").lower().removeprefix("www.") or None,
                        "chapters": [],
                    }

                text = resp.text or ""

                def _find_title(html: str) -> str | None:
                    m = re.search(r"<title[^>]*>(?P<t>.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
                    if not m:
                        return None
                    t = re.sub(r"\s+", " ", m.group("t") or "").strip()
                    return unescape(t) if t else None

                def _find_meta(html: str, *, name: str | None = None, prop: str | None = None) -> str | None:
                    if name:
                        m = re.search(
                            rf"<meta[^>]+name=['\"]{re.escape(name)}['\"][^>]+content=['\"](?P<c>[^'\"]+)['\"][^>]*>",
                            html,
                            flags=re.IGNORECASE,
                        )
                        if m:
                            return unescape((m.group("c") or "").strip()) or None
                    if prop:
                        m = re.search(
                            rf"<meta[^>]+property=['\"]{re.escape(prop)}['\"][^>]+content=['\"](?P<c>[^'\"]+)['\"][^>]*>",
                            html,
                            flags=re.IGNORECASE,
                        )
                        if m:
                            return unescape((m.group("c") or "").strip()) or None
                    return None

                title = (
                    _find_title(text)
                    or _find_meta(text, prop="og:title")
                    or _find_meta(text, name="twitter:title")
                    or ResourceCURD._guess_title_from_url(raw)
                )
                description = (
                    _find_meta(text, name="description")
                    or _find_meta(text, prop="og:description")
                    or _find_meta(text, name="twitter:description")
                )
                thumbnail_url = (
                    _find_meta(text, prop="og:image")
                    or _find_meta(text, name="twitter:image")
                    or _find_meta(text, name="twitter:image:src")
                )
                platform = _find_meta(text, prop="og:site_name")

                og_type = _find_meta(text, prop="og:type")
                og_video = _find_meta(text, prop="og:video") or _find_meta(text, prop="og:video:url")
                twitter_player = _find_meta(text, name="twitter:player")

                # Some pages (including X) store author in twitter meta tags.
                twitter_creator = _find_meta(text, name="twitter:creator")
                twitter_site = _find_meta(text, name="twitter:site")
                author = (twitter_creator or twitter_site)
                if author:
                    author = author.strip()
                    if author and not author.startswith("@"): 
                        # many sites use @handle; don't force otherwise
                        pass

                # Some sites don't expose OG video tags; detect video elements/streams in HTML.
                has_video = False
                if re.search(r"<video\b", text, flags=re.IGNORECASE):
                    has_video = True
                elif re.search(r"\.(mp4|m3u8)(?:\?|\"|'|\s)", text, flags=re.IGNORECASE):
                    has_video = True
                elif re.search(r"<iframe[^>]+(?:player|embed)", text, flags=re.IGNORECASE):
                    has_video = True

                if platform:
                    platform = platform.strip() or None
                host = (urlparse(raw).hostname or "").lower().removeprefix("www.") or None
                platform = ResourceCURD._normalize_platform(host, platform)

                return {
                    "title": title,
                    "description": description,
                    "thumbnail_url": thumbnail_url,
                    "author": author,
                    "publish_date": None,
                    "video_id": None,
                    "duration_seconds": None,
                    "platform": platform,
                    "og_type": og_type,
                    "og_video": og_video,
                    "twitter_player": twitter_player,
                    "has_video": has_video,
                    "chapters": [],
                }
        except Exception:
            # Final fallback: deterministic meta so UX can proceed.
            return {
                "title": ResourceCURD._guess_title_from_url(raw),
                "description": None,
                "thumbnail_url": None,
                "author": None,
                "publish_date": None,
                "video_id": None,
                "duration_seconds": None,
                "platform": (urlparse(raw).hostname or "").lower().removeprefix("www.") or None,
                "chapters": [],
            }

    @staticmethod
    def _extract_youtube_oembed(url: str) -> dict:
        """Best-effort metadata via YouTube oEmbed (no API key).

        Returns a partial meta dict: title, author, thumbnail_url.
        Raises on failure.
        """
        params = {"url": url, "format": "json"}
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            resp = client.get("https://www.youtube.com/oembed", params=params)
            resp.raise_for_status()
            data = resp.json()

        title = (data.get("title") or "").strip()
        author = (data.get("author_name") or "").strip() or None
        thumbnail_url = (data.get("thumbnail_url") or "").strip() or None
        if not title:
            raise ValueError("Extraction failed: missing title")
        return {"title": title, "author": author, "thumbnail_url": thumbnail_url}

    @staticmethod
    def extract_from_url(url: str) -> dict:
        key = (url or "").strip()
        if key:
            cached = ResourceCURD._extract_cache.get(key)
            if cached:
                ts, meta = cached
                if (time.time() - ts) < ResourceCURD._EXTRACT_CACHE_TTL_SECONDS:
                    return meta

        if not ResourceCURD._is_youtube(url):
            if ResourceCURD._is_x(url):
                meta = ResourceCURD._extract_x_tweet(url)
            elif ResourceCURD._is_instagram(url):
                meta = ResourceCURD._extract_instagram(url)
            else:
                meta = ResourceCURD._extract_generic_url(url)
            if key:
                ResourceCURD._extract_cache[key] = (time.time(), meta)
            return meta

        video_id = ResourceCURD._youtube_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        canonical_url = f"https://www.youtube.com/watch?v={video_id}"

        # 1) Try pytube first (richer: description/publish_date/duration).
        try:
            yt = YouTube(canonical_url)
            title = (yt.title or "").strip()
            description = (yt.description or "").strip() or None
            thumbnail_url = (yt.thumbnail_url or "").strip() or None
            author = (getattr(yt, "author", "") or "").strip() or None
            publish_date = getattr(yt, "publish_date", None)
            duration_seconds = getattr(yt, "length", None)
            try:
                duration_seconds = int(duration_seconds) if duration_seconds is not None else None
            except Exception:
                duration_seconds = None
            if duration_seconds is not None and duration_seconds < 0:
                duration_seconds = None

            if not description:
                try:
                    generic = ResourceCURD._extract_generic_url(canonical_url)
                    description = (generic.get("description") or "").strip() or None
                except Exception:
                    pass

            chapters = ResourceCURD._parse_chapters_from_description(description)
            if not title:
                raise ValueError("Extraction failed: missing title")

            if not thumbnail_url:
                thumbnail_url = ResourceCURD._youtube_thumbnail(video_id)

            meta = {
                "title": title,
                "description": description,
                "thumbnail_url": thumbnail_url,
                "author": author,
                "publish_date": publish_date,
                "video_id": video_id,
                "duration_seconds": duration_seconds,
                "platform": "youtube",
                "chapters": chapters,
            }
            if key:
                ResourceCURD._extract_cache[key] = (time.time(), meta)
            return meta
        except Exception:
            pass

        # 2) Fallback to oEmbed (usually more stable than pytube).
        try:
            oembed = ResourceCURD._extract_youtube_oembed(canonical_url)
            thumbnail_url = (oembed.get("thumbnail_url") or "").strip() or None
            if not thumbnail_url:
                thumbnail_url = ResourceCURD._youtube_thumbnail(video_id)

            description = None
            try:
                generic = ResourceCURD._extract_generic_url(canonical_url)
                description = (generic.get("description") or "").strip() or None
            except Exception:
                pass

            meta = {
                "title": oembed["title"],
                "description": description,
                "thumbnail_url": thumbnail_url,
                "author": oembed.get("author"),
                "publish_date": None,
                "video_id": video_id,
                "duration_seconds": None,
                "platform": "youtube",
                "chapters": [],
            }
            if key:
                ResourceCURD._extract_cache[key] = (time.time(), meta)
            return meta
        except Exception:
            pass

        # 3) Final fallback: deterministic metadata from video_id so UX can proceed
        # even when outbound access is blocked.
        meta = {
            "title": f"YouTube Video {video_id}",
            "description": None,
            "thumbnail_url": ResourceCURD._youtube_thumbnail(video_id),
            "author": None,
            "publish_date": None,
            "video_id": video_id,
            "duration_seconds": None,
            "platform": "youtube",
            "chapters": [],
        }
        if key:
            ResourceCURD._extract_cache[key] = (time.time(), meta)
        return meta

    @staticmethod
    def attach_to_user(db: Session, *, user_id: int, resource_id: int, is_public: bool = False, source: str = "saved") -> None:
        ResourceCURD.attach_to_user_with_weight(
            db,
            user_id=user_id,
            resource_id=resource_id,
            is_public=is_public,
            manual_weight=None,
            source=source,
        )

    @staticmethod
    def attach_to_user_with_weight(
        db: Session,
        *,
        user_id: int,
        resource_id: int,
        is_public: bool = False,
        manual_weight: Optional[int] = None,
        source: str = "saved",
    ) -> None:
        hit = (
            db.query(UserResource)
            .filter(UserResource.user_id == user_id, UserResource.resource_id == resource_id)
            .first()
        )

        # Policy:
        # - default manual_weight=1 when user doesn't set explicitly
        # - if already exists and request includes manual_weight, overwrite it
        if hit:
            if manual_weight is not None:
                hit.manual_weight = int(manual_weight)
                hit.effective_weight = int(manual_weight)
            return

        default_weight = 1 if manual_weight is None else int(manual_weight)
        db.add(
            UserResource(
                user_id=user_id,
                resource_id=resource_id,
                is_public=is_public,
                source=source,
                manual_weight=default_weight,
                effective_weight=default_weight,
                added_at=datetime.utcnow(),
                open_count=0,
                completion_status=False,
            )
        )

        # Community metric: increment save_count on first attach.
        obj = db.query(Resource).filter(Resource.id == resource_id).first()
        if obj is not None:
            try:
                obj.save_count = int(getattr(obj, "save_count", 0) or 0) + 1
            except Exception:
                obj.save_count = 1

        db.flush()

    @staticmethod
    def list_for_user(db: Session, *, user_id: int) -> list[Resource]:
        return (
            db.query(Resource)
            .join(UserResource, UserResource.resource_id == Resource.id)
            .filter(UserResource.user_id == user_id)
            .order_by(Resource.id.desc())
            .all()
        )

    @staticmethod
    def list_all(db: Session) -> list[Resource]:
        return db.query(Resource).order_by(Resource.id.desc()).all()

    @staticmethod
    def create_from_url(
        db: Session,
        *,
        user_id: int,
        url: str,
        category_id: int,
        is_system_public: bool = False,
        is_public: bool = False,
        visibility: str = "private",
        manual_weight: Optional[int] = None,
    ) -> Resource:
        meta = ResourceCURD.extract_from_url(url)
        normalized = (url or "").strip()
        if not normalized:
            raise ValueError("Invalid URL")

        if category_id is None:
            raise ValueError("category_id is required")
        cat = db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            raise ValueError("Category not found")

        resource_type = ResourceCURD._infer_resource_type(normalized, meta)

        platform = meta.get("platform")
        if not platform:
            host = (urlparse(normalized).hostname or "").lower().removeprefix("www.")
            platform = ResourceCURD._normalize_platform(host, None)

        # source_url is NOT unique per requirements.
        normalized_title = ResourceCURD._normalize_title(
            meta.get("title") or ResourceCURD._guess_title_from_url(normalized),
            normalized,
        )
        obj = Resource(
            resource_type=resource_type,
            platform=platform,
            title=normalized_title,
            summary=meta.get("description"),
            source_url=normalized,
            thumbnail=meta.get("thumbnail_url"),
            category_id=category_id,
            difficulty=None,
            tags={},
            raw_meta={
                "author": meta.get("author"),
                "publish_date": meta.get("publish_date"),
                "video_id": meta.get("video_id"),
                "duration_seconds": meta.get("duration_seconds"),
                "chapters": meta.get("chapters") or [],
                "og_type": meta.get("og_type"),
                "og_video": meta.get("og_video"),
                "twitter_player": meta.get("twitter_player"),
            },
            is_system_public=is_system_public,
            visibility=visibility,
            creator_id=user_id,
        )
        db.add(obj)
        db.flush()

        if resource_type == "video":
            v = Video(
                resource_id=obj.id,
                duration=meta.get("duration_seconds"),
                channel=meta.get("author"),
                video_id=meta.get("video_id"),
            )
            db.add(v)
            db.flush()
        elif resource_type == "document":
            d = Doc(resource_id=obj.id)
            db.add(d)
            db.flush()
        else:
            a = Article(resource_id=obj.id)
            db.add(a)
            db.flush()

        ResourceCURD.attach_to_user_with_weight(
            db,
            user_id=user_id,
            resource_id=obj.id,
            is_public=is_public,
            manual_weight=manual_weight,
            source="created",
        )
        return obj

    @staticmethod
    def detach_from_user(db: Session, *, user_id: int, resource_id: int) -> None:
        assoc = (
            db.query(UserResource)
            .filter(UserResource.user_id == user_id, UserResource.resource_id == resource_id)
            .first()
        )
        if not assoc:
            raise ValueError("resource not found")

        db.delete(assoc)
        db.flush()

    @staticmethod
    def update_for_user(
        db: Session,
        *,
        user_id: int,
        resource_id: int,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        platform: Optional[str] = None,
        thumbnail: Optional[str] = None,
        category_id: Optional[int] = None,
        difficulty: Optional[int] = None,
        tags: Optional[dict] = None,
        raw_meta: Optional[dict] = None,
    ) -> Tuple[Resource, UserResource]:
        """更新用户收藏资源。

        逻辑：
        - 如果用户是资源的创建者（creator_id == user_id），直接修改 Resource 表（私有资源）
        - 如果是收藏的公共资源，写入 UserResource.custom_* 覆盖字段，不影响原始资源
        """
        obj = db.query(Resource).filter(Resource.id == resource_id).first()
        if not obj:
            raise ValueError("resource not found")

        assoc = (
            db.query(UserResource)
            .filter(
                UserResource.user_id == user_id,
                UserResource.resource_id == resource_id,
            )
            .first()
        )
        if not assoc:
            raise ValueError("user_resource association not found")

        is_creator = getattr(obj, "creator_id", None) == user_id

        if is_creator:
            # 用户自己创建的资源 → 直接修改 Resource
            if title is not None:
                t = title.strip()
                if not t:
                    raise ValueError("title cannot be empty")
                obj.title = ResourceCURD._normalize_title(t, obj.source_url or "")

            if summary is not None:
                obj.summary = summary.strip() or None

            if platform is not None:
                obj.platform = platform.strip() or None

            if thumbnail is not None:
                obj.thumbnail = thumbnail.strip() or None

            if category_id is not None:
                cat = db.query(Category).filter(Category.id == int(category_id)).first()
                if not cat:
                    raise ValueError("Category not found")
                obj.category_id = int(category_id)

            if difficulty is not None:
                obj.difficulty = int(difficulty)

            if tags is not None:
                obj.tags = tags

            if raw_meta is not None:
                obj.raw_meta = raw_meta

            db.add(obj)
        else:
            # 收藏的公共资源 → 写入 custom_* 覆盖字段
            if title is not None:
                t = title.strip()
                if not t:
                    assoc.custom_title = None
                else:
                    assoc.custom_title = t

            if summary is not None:
                assoc.custom_summary = summary.strip() or None

            if thumbnail is not None:
                assoc.custom_thumbnail = thumbnail.strip() or None

            db.add(assoc)

        db.flush()
        return obj, assoc

