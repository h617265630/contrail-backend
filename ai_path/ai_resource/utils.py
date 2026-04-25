"""
Utility functions for ai_resource search tools.
"""


def mock_resource(rtype: str, title: str, url: str, description: str, score: float) -> dict:
    """Create a mock resource dictionary for fallback responses."""
    # Generate thumbnail for GitHub URLs
    thumbnail = ""
    if "github.com" in url:
        parts = [p for p in url.replace("https://github.com/", "").split("/") if p]
        if len(parts) >= 2:
            thumbnail = f"https://opengraph.githubassets.com/1/{parts[0]}/{parts[1]}"
    return {
        "type": rtype,
        "title": title,
        "url": url,
        "description": description,
        "source_score": score,
        "thumbnail": thumbnail,
        "why_recommended": "与当前学习节点高度相关，且可直接用于实操。",
    }


def safe_get(data: dict, *keys, default=None):
    """Safely get nested values from a dictionary."""
    value = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value
