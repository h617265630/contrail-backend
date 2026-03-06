from __future__ import annotations

import ipaddress
import re
import socket
import time
import concurrent.futures
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlparse

import bleach
import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.reader import ReaderExtractRequest, ReaderExtractResponse

router = APIRouter(prefix="/reader", tags=["Reader"])


_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_CACHE_TTL_SECONDS = 24 * 60 * 60
_MAX_BYTES = 2_500_000


def _is_private_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
        )
    except ValueError:
        return True


def _assert_url_safe(raw_url: str) -> None:
    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed")

    host = (parsed.hostname or "").strip()
    if not host:
        raise HTTPException(status_code=400, detail="Invalid URL host")

    if host in {"localhost"}:
        raise HTTPException(status_code=400, detail="Blocked host")

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(socket.getaddrinfo, host, None)
            infos = fut.result(timeout=3.0)
    except concurrent.futures.TimeoutError:
        raise HTTPException(status_code=400, detail="DNS resolve timeout")
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="DNS resolve failed")

    for info in infos:
        ip = info[4][0]
        if _is_private_ip(ip):
            raise HTTPException(status_code=400, detail="Blocked private network host")


def _cache_get(url: str) -> dict[str, Any] | None:
    hit = _CACHE.get(url)
    if not hit:
        return None
    ts, payload = hit
    if (time.time() - ts) > _CACHE_TTL_SECONDS:
        _CACHE.pop(url, None)
        return None
    return payload


def _cache_set(url: str, payload: dict[str, Any]) -> None:
    _CACHE[url] = (time.time(), payload)


_ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p",
    "pre",
    "code",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "figure",
    "figcaption",
    "blockquote",
    "hr",
    "br",
    "span",
    "div",
    "section",
    "article",
    "header",
    "footer",
]

_ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "pre": ["class"],
    "span": ["class"],
    "div": ["class"],
}


def _count_words(text: str) -> int:
    raw = re.sub(r"\s+", " ", (text or "").strip())
    if not raw:
        return 0
    return len(raw.split(" "))


def _absolutize_img_src(html: str, base_url: str) -> str:
    if not html:
        return html

    # Rewrite <img src="..."> to absolute URLs for better rendering.
    # Many readability outputs (esp. GitHub README) contain relative URLs.
    # Note: this is best-effort and intentionally avoids adding heavy HTML parser deps.
    def _rewrite(match: re.Match[str]) -> str:
        prefix = match.group("prefix")
        src = (match.group("src") or "").strip()
        suffix = match.group("suffix")

        if not src:
            return match.group(0)

        lowered = src.lower()
        if lowered.startswith(("data:", "mailto:", "javascript:")):
            return match.group(0)

        # Handle scheme-relative URLs: //cdn.example.com/img.png
        if lowered.startswith("//"):
            scheme = urlparse(base_url).scheme or "https"
            abs_src = f"{scheme}:{src}"
        else:
            abs_src = urljoin(base_url, src)

        return f"{prefix}{abs_src}{suffix}"

    # Match src attribute with single or double quotes.
    img_src_re = re.compile(
        r"(?P<prefix><img\b[^>]*?\bsrc\s*=\s*['\"])(?P<src>[^'\"]+)(?P<suffix>['\"][^>]*?>)",
        flags=re.IGNORECASE,
    )

    try:
        return img_src_re.sub(_rewrite, html)
    except Exception:
        return html


@router.post("/extract", response_model=ReaderExtractResponse)
def reader_extract(payload: ReaderExtractRequest):
    try:
        from readability import Document  # type: ignore
    except Exception:
        try:
            from readability.readability import Document  # type: ignore
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Reader dependency missing or incompatible. Install 'readability-lxml' and remove the wrong 'readability' package. "
                    f"Import error: {e}"
                ),
            )

    url = str(payload.url)

    cached = _cache_get(url)
    if cached is not None:
        return ReaderExtractResponse(**cached)

    _assert_url_safe(url)

    try:
        with httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; ContrailReader/1.0; +https://example.com)",
                "Accept": "text/html,application/xhtml+xml",
            },
        ) as client:
            resp = client.get(url)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Fetch failed: {e}")

    ctype = (resp.headers.get("content-type") or "").lower()
    if "text/html" not in ctype and "application/xhtml+xml" not in ctype:
        raise HTTPException(status_code=400, detail=f"Unsupported content-type: {ctype or 'unknown'}")

    content = resp.content
    if len(content) > _MAX_BYTES:
        raise HTTPException(status_code=400, detail="Content too large")

    html = content.decode(resp.encoding or "utf-8", errors="replace")

    try:
        def _run_readability(raw_html: str) -> tuple[str, str]:
            doc = Document(raw_html)
            title = (doc.short_title() or "").strip() or "Untitled"
            summary_html = (doc.summary(html_partial=True) or "").strip()
            return title, summary_html

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(_run_readability, html)
            title, summary_html = fut.result(timeout=5.0)
    except concurrent.futures.TimeoutError:
        raise HTTPException(status_code=400, detail="Extract timeout")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Extract failed: {e}")

    cleaned = bleach.clean(
        summary_html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        strip=True,
    )

    cleaned = _absolutize_img_src(cleaned, url)

    text = bleach.clean(cleaned, tags=[], strip=True)
    wc = _count_words(text)

    out = {
        "url": url,
        "title": title,
        "site_name": None,
        "byline": None,
        "excerpt": None,
        "content_html": cleaned,
        "word_count": wc,
        "extracted_at": datetime.utcnow(),
    }

    _cache_set(url, out)
    return ReaderExtractResponse(**out)
