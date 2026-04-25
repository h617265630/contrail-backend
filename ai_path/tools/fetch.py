"""
HTTP page fetcher with BeautifulSoup text extraction.
Falls back to the search snippet if the page can't be fetched.
"""

from __future__ import annotations
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from ai_path.models.schemas import FetchedPage

# ── Config ─────────────────────────────────────────────────────────────────────
MAX_CONTENT_CHARS = 4000
REQUEST_TIMEOUT = 8

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; aifetchpathly/1.0; "
        "+https://github.com/aifetchpathly)"
    ),
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
}

# Domains / URL patterns that can't or shouldn't be fetched
_SKIP_PATTERNS = [
    r"youtube\.com",
    r"youtu\.be",
    r"twitter\.com",
    r"x\.com",
    r"linkedin\.com",
    r"facebook\.com",
    r"instagram\.com",
    r"reddit\.com",
    r"\.pdf$",
    r"\.pptx?$",
    r"\.docx?$",
]
_SKIP_RE = re.compile("|".join(_SKIP_PATTERNS), re.IGNORECASE)


def _should_skip(url: str) -> bool:
    return bool(_SKIP_RE.search(url))


_GH_AVATAR_RE = re.compile(r"https://avatars\.githubusercontent\.com/[^)\s\"']+")
_SKIP_PATTERNS_IMG = [
    r"youtube\.com",
    r"youtu\.be",
    r"twitter\.com",
    r"x\.com",
    r"linkedin\.com",
    r"facebook\.com",
    r"instagram\.com",
    r"reddit\.com",
    r"\.pdf$",
    r"\.pptx?$",
    r"\.docx?$",
]


def _extract_text_and_image(html: str, url: str) -> tuple[str, str, str | None]:
    """Return (title, main_text, image_url) extracted from raw HTML."""
    soup = BeautifulSoup(html, "lxml")

    # Title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Remove boilerplate tags
    for tag in soup(["script", "style", "nav", "footer", "header",
                      "aside", "form", "noscript", "svg"]):
        tag.decompose()

    # Try to find main content container
    main = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_=re.compile(r"(content|post|article|entry|body)", re.I))
        or soup.body
    )

    if main is None:
        return title, "", None

    text = main.get_text(separator="\n", strip=True)
    # Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Extract image
    image_url: str | None = None

    # 1. og:image
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        image_url = og["content"]

    # 2. twitter:image
    if not image_url:
        tw = soup.find("meta", attrs={"name": "twitter:image"})
        if tw and tw.get("content"):
            image_url = tw["content"]

    # 3. GitHub repo → use owner avatar from static GitHub img or API redirect
    if not image_url and "github.com" in url:
        # Try to find GitHub avatar in the HTML (often in avatars.githubusercontent.com)
        img_tags = soup.find_all("img", src=re.compile(r"avatars\.githubusercontent\.com"))
        for img in img_tags:
            src = img.get("src", "")
            if src and not src.startswith("data:"):
                image_url = src
                break

    return title, text[:MAX_CONTENT_CHARS], image_url


def fetch_page(url: str, fallback_title: str = "", fallback_snippet: str = "") -> FetchedPage:
    """
    Fetch a URL and extract readable text + og:image.
    Returns FetchedPage(fetch_ok=False) with snippet as content on any failure.
    """
    if _should_skip(url):
        return FetchedPage(
            url=url,
            title=fallback_title or url,
            content=fallback_snippet,
            fetch_ok=False,
            image=None,
        )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            raise ValueError(f"Non-HTML content type: {content_type}")

        title, text, image = _extract_text_and_image(resp.text, url)
        if len(text) < 100:
            # Too little content — fall back to snippet
            return FetchedPage(
                url=url,
                title=title or fallback_title,
                content=fallback_snippet,
                fetch_ok=False,
                image=image,
            )

        return FetchedPage(
            url=url,
            title=title or fallback_title,
            content=text,
            fetch_ok=True,
            image=image,
        )

    except Exception:
        return FetchedPage(
            url=url,
            title=fallback_title or url,
            content=fallback_snippet,
            fetch_ok=False,
            image=None,
        )
