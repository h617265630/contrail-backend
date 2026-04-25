"""
GitHub search tool for repositories and resources.
Uses Tavily API and GitHub Search API.
"""

import asyncio
import httpx
import os
import re
from html import unescape as _unescape


# ── Banner / social image map ──────────────────────────────────────────────────
# 精确匹配表（host → banner）
_PLATFORM_EXACT: dict[str, str] = {
    # General dev
    "medium.com":               "https://miro.medium.com/v2/resize:fit:1200/1*jfdwtvU6V6g99q3G7gq7dQ.png",
    "towardsdatascience.com":     "https://miro.medium.com/v2/resize:fit:1200/1*jfdwtvU6V6g99q3G7gq7dQ.png",
    "dev.to":                    "https://dev-to.s3.us-west-2.amazonaws.com/original_images/Oxw38XZ7kq7hwD5msz7o9ZkJ.jpeg",
    "hashnode.com":              "https://cdn.hashnode.com/res/hashnode/image/upload/v1611902473383/CDyAuTy75.png",
    "stackoverflow.com":          "https://cdn.sstatic.net/Sites/stackoverflow/Img/apple-touch-icon@2.png",
    "css-tricks.com":            "https://css-tricks.com/wp-content/uploads/2019/06/akashic-knowledge.png",
    "smashingmagazine.com":       "https://www.smashingmagazine.com/images/logo/logo--red.png",
    "freecodecamp.org":           "https://cdn.freecodecamp.org/platform/universal/fcc_meta_1920X1080-indigo.png",
    "w3schools.com":              "https://www.w3schools.com/images/w3schools_logo_436_2.png",
    "geeksforgeeks.org":           "https://media.geeksforgeeks.org/wp-content/uploads/2021/11/GFG-OG-Image.png",
    "digitalocean.com":           "https://www.digitalocean.com/_next/static/media/social-share.png",
    "baeldung.com":               "https://www.baeldung.com/wp-content/uploads/2016/05/baeldung-logo.jpg",
    "tutorialspoint.com":          "https://static.tutorialspoint.com/images/tp-logo.png",
    # Frontend frameworks
    "reactjs.org":               "https://reactjs.org/logo-og.png",
    "react.dev":                 "https://react.dev/images/og-home.png",
    "vuejs.org":                 "https://vuejs.org/images/logo.png",
    "angular.io":               "https://angular.io/assets/images/logos/angular/angular.svg",
    "svelte.dev":               "https://svelte.dev/svelte-logotype.svg",
    "nextjs.org":               "https://nextjs.org/static/twitter-cards/home.jpg",
    "nuxt.com":                  "https://nuxt.com/assets/design-kit/og-image.jpg",
    "solidjs.com":              "https://www.solidjs.com/img/og.png",
    # CSS / styling
    "tailwindcss.com":           "https://tailwindcss.com/_next/static/media/social-card-large.a6e71726.jpg",
    "getbootstrap.com":          "https://getbootstrap.com/docs/5.3/assets/brand/bootstrap-social.png",
    # Languages
    "typescriptlang.org":         "https://www.typescriptlang.org/images/og-image.png",
    "developer.mozilla.org":     "https://developer.mozilla.org/mdn-social-share.cd6c4a5a.png",
    "docs.python.org":          "https://www.python.org/static/opengraph-icon-200x200.png",
    "python.org":              "https://www.python.org/static/opengraph-icon-200x200.png",
    "rust-lang.org":            "https://www.rust-lang.org/static/images/rust-social-wide.jpg",
    "go.dev":                    "https://go.dev/blog/go-brand/Go-Logo/PNG/Go-Logo_Blue.png",
    "kotlinlang.org":           "https://kotlinlang.org/assets/images/twitter-ogimage.png",
    "swift.org":                "https://swift.org/assets/images/swift~dark.svg",
    "nodejs.org":              "https://nodejs.org/static/images/logo.svg",
    "deno.com":                 "https://deno.com/og_image.png",
    "bun.sh":                   "https://bun.sh/og-image.png",
    # Cloud / DevOps
    "docs.aws.amazon.com":       "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
    "aws.amazon.com":            "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
    "cloud.google.com":          "https://cloud.google.com/_static/cloud/images/social-icon-google-cloud-1200-630.png",
    "learn.microsoft.com":       "https://learn.microsoft.com/en-us/media/open-graph-image.png",
    "docs.docker.com":           "https://www.docker.com/wp-content/uploads/2022/03/Moby-logo.png",
    "kubernetes.io":            "https://kubernetes.io/images/kubernetes-horizontal-color.png",
    # AI / ML
    "pytorch.org":              "https://pytorch.org/assets/images/pytorch-logo.png",
    "tensorflow.org":           "https://www.tensorflow.org/images/tf_logo_social.png",
    "huggingface.co":           "https://huggingface.co/front/assets/huggingface_logo-noborder.svg",
    "kaggle.com":               "https://www.kaggle.com/static/images/site-logo.svg",
    "openai.com":               "https://openai.com/content/images/2022/05/openai-avatar.png",
    "docs.anthropic.com":       "https://www.anthropic.com/images/icons/apple-touch-icon.png",
    # Learning platforms
    "coursera.org":             "https://d3njjcbhbojbot.cloudfront.net/web/images/favicons/v2/apple-touch-icon-precomposed.png",
    "udemy.com":                "https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg",
    "pluralsight.com":          "https://www.pluralsight.com/content/dam/pluralsight2/general/brand/og_image.png",
    "realpython.com":           "https://realpython.com/static/real-python-logo-wide.fbab4d2c6f34.png",
    "frontendmasters.com":       "https://frontendmasters.com/static-assets/core/social-thumb.png",
    "leetcode.com":             "https://leetcode.com/static/images/LeetCode_Sharing.png",
}

# 子域名匹配表（后缀域名 → banner），O(1) 查找
_PLATFORM_WILDCARD: dict[str, str] = {
    "medium.com": "https://miro.medium.com/v2/resize:fit:1200/1*jfdwtvU6V6g99q3G7gq7dQ.png",
    "github.com": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
}

_HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}


# ── 通用 meta 解析（与 ResourceCURD._extract_generic_url 完全一致）─────────────────

def _find_meta(html: str, *, prop: str | None = None, name: str | None = None) -> str | None:
    """与 ResourceCURD._extract_generic_url 中的 _find_meta 完全一致。"""
    if prop:
        m = re.search(
            rf"<meta[^>]+property=['\"]{re.escape(prop)}['\"][^>]+content=['\"](?P<c>[^'\"]+)['\"][^>]*>",
            html, flags=re.IGNORECASE,
        )
        if m:
            return _unescape((m.group("c") or "").strip()) or None
    if name:
        m = re.search(
            rf"<meta[^>]+name=['\"]{re.escape(name)}['\"][^>]+content=['\"](?P<c>[^'\"]+)['\"][^>]*>",
            html, flags=re.IGNORECASE,
        )
        if m:
            return _unescape((m.group("c") or "").strip()) or None
    return None


def _fetch_og_image(url: str) -> str:
    """同步 fetch og:image — 与 add resource 逻辑完全一致。"""
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True, headers=_HTTP_HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text or ""
    except Exception:
        return ""

    return (
        _find_meta(html, prop="og:image")
        or _find_meta(html, name="twitter:image")
        or _find_meta(html, name="twitter:image:src")
        or ""
    )


async def _fetch_og_image_async(url: str) -> str:
    """异步 fetch og:image — 与 _fetch_og_image 逻辑完全一致。"""
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers=_HTTP_HEADERS) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text or ""
    except Exception:
        return ""

    return (
        _find_meta(html, prop="og:image")
        or _find_meta(html, name="twitter:image")
        or _find_meta(html, name="twitter:image:src")
        or ""
    )


# ── 静态 thumbnail（零延迟，无网络请求）────────────────────────────────────────

def _get_thumbnail_for_url(url: str) -> str:
    """
    返回最佳 banner/social 图片 URL。
    优先级：
    1. YouTube → 视频缩略图
    2. GitHub → opengraph.githubassets.com
    3. 已知平台 → O(1) 字典查找
    4. 未知域名 → ""（由调用方并发 fetch og:image）
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.netloc.lower().replace("www.", "")
        path = parsed.path

        # ── YouTube ──────────────────────────────────────────────────────────
        if "youtube.com" in host or "youtu.be" in host:
            vid_id = None
            if "youtu.be" in host:
                vid_id = path.strip("/").split("/")[0]
            elif "/watch" in path:
                from urllib.parse import parse_qs
                vid_id = (parse_qs(parsed.query).get("v") or [""])[0]
            elif "/shorts/" in path or "/embed/" in path:
                vid_id = path.strip("/").split("/")[-1]
            if vid_id:
                return f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"

        # ── 精确匹配 O(1) ────────────────────────────────────────────────────
        if host in _PLATFORM_EXACT:
            return _PLATFORM_EXACT[host]

        # ── 子域名匹配 O(1) ──────────────────────────────────────────────────
        dot = host.find(".")
        while dot > 0:
            suffix = host[dot + 1:]
            if suffix in _PLATFORM_WILDCARD:
                if suffix == "github.com":
                    parts = [p for p in path.strip("/").split("/") if p]
                    if len(parts) >= 2:
                        return f"https://opengraph.githubassets.com/1/{parts[0]}/{parts[1]}"
                return _PLATFORM_WILDCARD[suffix]
            dot = suffix.find(".")

        # ── 未知域名：返回空，由调用方并发 fetch og:image ────────────────────
        return ""

    except Exception:
        return ""


# ── 并发 fetch ────────────────────────────────────────────────────────────────

def _fetch_og_images_concurrent(urls: list[str]) -> list[str]:
    """并发 fetch 多个 URL 的 og:image，返回顺序与输入一致。"""
    if not urls:
        return []

    async def _gather() -> list[str]:
        return await asyncio.gather(*[_fetch_og_image_async(u) for u in urls])

    try:
        loop = asyncio.get_running_loop()
        # 在已有事件循环中：用 run_in_executor 避免 asyncio.run() 开销
        def _sync() -> list[str]:
            return asyncio.run(_gather())
        future = loop.run_in_executor(None, _sync)
        return future.result()
    except RuntimeError:
        # 无运行中循环（同步环境）
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(_gather())


# ── 主搜索函数 ────────────────────────────────────────────────────────────────

def search_github(query: str, limit: int = 6) -> list[dict]:
    """搜索 GitHub 仓库。优先 GitHub API，失败走 fallback。"""
    github_token = os.getenv("GITHUB_TOKEN", "")
    if github_token:
        results = _search_github_api(query, limit, github_token)
        if results:
            return results
    return _fallback_github(query)[:limit]


def search_tavily_resources(query: str, limit: int = 6) -> list[dict]:
    """通过 Tavily API 搜索网页资源（非 GitHub）。"""
    return _search_tavily(query, limit)


# 跳过视频类域名（这些无法提取文本内容）
_SKIP_DOMAINS_VIDEO = {
    "youtube.com", "youtu.be", "bilibili.com", "vimeo.com",
    "twitch.tv", "dailymotion.com", "coursera.org", "udemy.com",
}


def _is_video_url(url: str) -> bool:
    """检查 URL 是否为视频类资源（无法提取文本）。"""
    try:
        host = httpx.URL(url).host or ""
        # 跳过 www. 前缀
        host = host.lstrip("www.")
        return any(vd in host.lower() for vd in _SKIP_DOMAINS_VIDEO)
    except Exception:
        return False


def _search_tavily(query: str, limit: int = 6) -> list[dict]:
    """Tavily 搜索 + 并发获取未知域名 og:image。"""
    tavily_api_key = os.getenv("TAVILY_API_KEY", "")
    if not tavily_api_key:
        return []

    payload = {
        "api_key": tavily_api_key,
        "query": f"{query} tutorial learning resource",
        "search_depth": "basic",
        "max_results": limit,
    }

    try:
        timeout = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
        with httpx.Client(timeout=timeout) as client:
            response = client.post("https://api.tavily.com/search", json=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            result = response.json()
    except Exception:
        return []

    resources: list[dict] = []
    unknown_indices: list[int] = []

    for idx, item in enumerate(result.get("results", [])[:limit]):
        url = item.get("url")
        if not url:
            continue
        # 跳过视频类 URL（无法提取文本内容）
        if _is_video_url(url):
            continue
        title = item.get("title") or f"Resource: {query}"
        description = item.get("content") or item.get("snippet") or f"与 {query} 相关的资源。"
        score = item.get("score")
        normalized_score = float(score) if isinstance(score, (int, float)) else max(0.5, 0.9 - idx * 0.08)

        thumbnail = _get_thumbnail_for_url(url)
        needs_fetch = thumbnail == ""

        resources.append({
            "type": "article",
            "title": title,
            "url": url,
            "description": description[:300],
            "source_score": normalized_score,
            "thumbnail": thumbnail,
            "why_recommended": "覆盖文档与教程场景，适合补全知识细节与最佳实践。",
        })
        if needs_fetch:
            unknown_indices.append(len(resources) - 1)

    if unknown_indices:
        urls_to_fetch = [resources[i]["url"] for i in unknown_indices]
        thumbnails = _fetch_og_images_concurrent(urls_to_fetch)
        for i, thumb in zip(unknown_indices, thumbnails):
            if thumb:
                resources[i]["thumbnail"] = thumb

    return resources


def _search_github_api(query: str, limit: int, token: str) -> list[dict]:
    """GitHub API 搜索 + 并发获取所有 repo 的 og:image。"""
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        timeout = float(os.getenv("HTTP_TIMEOUT_SECONDS", "10"))
        with httpx.Client(timeout=timeout) as client:
            response = client.get("https://api.github.com/search/repositories", params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
    except Exception:
        return []

    # 收集元数据，不立即 fetch 图
    repos_data: list[tuple[str, str, str, float]] = []
    for idx, repo in enumerate(payload.get("items", [])[:limit]):
        full_name = repo.get("full_name", "GitHub Repo")
        html_url = repo.get("html_url")
        if not html_url:
            continue
        description = repo.get("description") or f"与 {query} 相关的开源仓库。"
        score = max(0.58, 0.94 - idx * 0.07)
        repos_data.append((full_name, html_url, description, score))

    # 并发 fetch 所有 repo 的 og:image
    urls = [r[1] for r in repos_data]
    thumbnails = _fetch_og_images_concurrent(urls)

    resources: list[dict] = []
    for (full_name, html_url, description, score), thumb in zip(repos_data, thumbnails):
        final_thumb = thumb or (
            f"https://opengraph.githubassets.com/1/{full_name}"
            if full_name else
            "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        )
        resources.append({
            "type": "github",
            "title": full_name,
            "url": html_url,
            "description": description,
            "source_score": score,
            "thumbnail": final_thumb,
            "why_recommended": "高质量开源项目可直接用于阅读源码与实战参考。",
        })
    return resources


def _fallback_github(query: str) -> list[dict]:
    """GitHub API 失败时返回热门仓库，未匹配时也返回全部 fallback repos。"""
    from .utils import mock_resource

    q = query.replace(" ", "+").lower()
    repos = [
        {"title": "vercel/next.js",                "url": "https://github.com/vercel/next.js",               "description": "The React Framework for Web."},
        {"title": "facebook/react",                  "url": "https://github.com/facebook/react",                "description": "A declarative, efficient JavaScript library for building UIs."},
        {"title": "microsoft/typescript",             "url": "https://github.com/microsoft/typescript",          "description": "TypeScript is a superset of JavaScript that compiles to clean JS."},
        {"title": "tailwindlabs/tailwindcss",        "url": "https://github.com/tailwindlabs/tailwindcss",     "description": "A utility-first CSS framework for rapid UI development."},
        {"title": "vitejs/vite",                     "url": "https://github.com/vitejs/vite",                   "description": "Next generation frontend tooling — lightning fast HMR."},
        {"title": "shadcn-ui/ui",                    "url": "https://github.com/shadcn-ui/ui",                  "description": "Beautifully designed components built with Radix UI and Tailwind CSS."},
        {"title": "anthropics/anthropic-sdk-typescript", "url": "https://github.com/anthropics/anthropic-sdk-typescript", "description": "Anthropic TypeScript SDK for Claude AI."},
        {"title": "langchain-ai/langchain",          "url": "https://github.com/langchain-ai/langchain",       "description": "Building applications with LLMs through composability."},
    ]
    # 优先返回匹配的，未匹配时也返回全部 8 个 fallback repos
    matched = [r for r in repos if q in r["title"].lower()]
    candidates = matched if matched else repos
    return [
        mock_resource(
            rtype="github",
            title=r["title"],
            url=r["url"],
            description=r["description"],
            score=0.85 - i * 0.05,
        )
        for i, r in enumerate(candidates)
    ]
