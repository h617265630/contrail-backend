from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import httpx
from datetime import datetime, timedelta

router = APIRouter(prefix="/trending", tags=["Trending"])


# GitHub Trending
@router.get("/github")
async def get_github_trending(
    language: Optional[str] = Query(None, description="Programming language filter"),
    since: Optional[str] = Query(
        "weekly", description="Time range: daily, weekly, monthly"
    ),
    per_page: int = Query(30, ge=1, le=100),
):
    """
    Get trending GitHub repositories
    Uses GitHub Search API to find popular repositories
    """
    try:
        # Calculate date range based on 'since' parameter
        now = datetime.utcnow()
        if since == "daily":
            date_from = now - timedelta(days=1)
        elif since == "monthly":
            date_from = now - timedelta(days=30)
        else:  # weekly
            date_from = now - timedelta(days=7)

        date_str = date_from.strftime("%Y-%m-%d")

        # Build query
        query_parts = [f"stars:>100", f"created:>{date_str}"]
        if language:
            query_parts.append(f"language:{language}")

        query = " ".join(query_parts)

        # Call GitHub API
        url = "https://api.github.com/search/repositories"
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": per_page}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        # Transform to our format
        items = []
        for repo in data.get("items", []):
            items.append(
                {
                    "id": repo["id"],
                    "title": repo["full_name"],
                    "summary": repo.get("description", ""),
                    "source_url": repo["html_url"],
                    "thumbnail": repo["owner"].get("avatar_url", ""),
                    "platform": "GitHub",
                    "resource_type": "article",
                    "category_name": "Development",
                    "stats": {
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "watchers": repo.get("watchers_count", 0),
                        "language": repo.get("language", ""),
                        "topics": repo.get("topics", []),
                    },
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                }
            )

        return {"total_count": data.get("total_count", 0), "items": items}

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail=f"GitHub API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch GitHub trending: {str(e)}"
        )


# YouTube Trending
@router.get("/youtube")
async def get_youtube_trending(
    api_key: str = Query(..., description="YouTube Data API v3 key"),
    region_code: str = Query("US", description="Region code (US, CN, JP, etc.)"),
    category_id: Optional[str] = Query(
        None, description="Video category ID (28=Tech, 27=Education)"
    ),
    max_results: int = Query(50, ge=1, le=50),
):
    """
    Get trending YouTube videos
    Requires YouTube Data API v3 key
    """
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": max_results,
            "key": api_key,
        }

        if category_id:
            params["videoCategoryId"] = category_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        # Transform to our format
        items = []
        for video in data.get("items", []):
            snippet = video.get("snippet", {})
            statistics = video.get("statistics", {})
            content_details = video.get("contentDetails", {})

            items.append(
                {
                    "id": video["id"],
                    "title": snippet.get("title", ""),
                    "summary": snippet.get("description", "")[
                        :500
                    ],  # Truncate long descriptions
                    "source_url": f"https://www.youtube.com/watch?v={video['id']}",
                    "thumbnail": snippet.get("thumbnails", {})
                    .get("high", {})
                    .get("url", ""),
                    "platform": "YouTube",
                    "resource_type": "video",
                    "category_name": "Video",
                    "stats": {
                        "views": int(statistics.get("viewCount", 0)),
                        "likes": int(statistics.get("likeCount", 0)),
                        "comments": int(statistics.get("commentCount", 0)),
                        "duration": content_details.get("duration", ""),
                        "channel": snippet.get("channelTitle", ""),
                    },
                    "created_at": snippet.get("publishedAt"),
                    "updated_at": snippet.get("publishedAt"),
                }
            )

        return {
            "total_count": len(items),
            "items": items,
            "page_info": data.get("pageInfo", {}),
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            raise HTTPException(
                status_code=403, detail="Invalid YouTube API key or quota exceeded"
            )
        raise HTTPException(
            status_code=e.response.status_code, detail=f"YouTube API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch YouTube trending: {str(e)}"
        )


# Combined trending (GitHub + YouTube)
@router.get("/combined")
async def get_combined_trending(
    youtube_api_key: Optional[str] = Query(None, description="YouTube Data API v3 key"),
    github_language: Optional[str] = Query(None, description="GitHub language filter"),
    github_per_page: int = Query(15, ge=1, le=50),
    youtube_max_results: int = Query(15, ge=1, le=50),
    youtube_region: str = Query("US"),
    youtube_category: Optional[str] = Query("28", description="28=Tech, 27=Education"),
):
    """
    Get combined trending from both GitHub and YouTube
    """
    results = {
        "github": {"items": [], "error": None},
        "youtube": {"items": [], "error": None},
    }

    # Fetch GitHub trending
    try:
        github_data = await get_github_trending(
            language=github_language, since="weekly", per_page=github_per_page
        )
        results["github"]["items"] = github_data.get("items", [])
    except Exception as e:
        results["github"]["error"] = str(e)

    # Fetch YouTube trending (only if API key provided)
    if youtube_api_key:
        try:
            youtube_data = await get_youtube_trending(
                api_key=youtube_api_key,
                region_code=youtube_region,
                category_id=youtube_category,
                max_results=youtube_max_results,
            )
            results["youtube"]["items"] = youtube_data.get("items", [])
        except Exception as e:
            results["youtube"]["error"] = str(e)
    else:
        results["youtube"]["error"] = "No YouTube API key provided"

    # Combine and sort by popularity
    all_items = []

    # Add GitHub items with normalized score
    for item in results["github"]["items"]:
        score = item.get("stats", {}).get("stars", 0)
        all_items.append({**item, "popularity_score": score})

    # Add YouTube items with normalized score
    for item in results["youtube"]["items"]:
        score = item.get("stats", {}).get("views", 0) / 1000  # Normalize views
        all_items.append({**item, "popularity_score": score})

    # Sort by popularity
    all_items.sort(key=lambda x: x.get("popularity_score", 0), reverse=True)

    return {
        "total_count": len(all_items),
        "items": all_items,
        "sources": {
            "github": {
                "count": len(results["github"]["items"]),
                "error": results["github"]["error"],
            },
            "youtube": {
                "count": len(results["youtube"]["items"]),
                "error": results["youtube"]["error"],
            },
        },
    }
