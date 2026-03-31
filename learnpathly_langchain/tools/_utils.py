def mock_resource(rtype: str, title: str, url: str, description: str, score: float) -> dict:
    return {
        "type": rtype,
        "title": title,
        "url": url,
        "description": description,
        "source_score": score,
        "why_recommended": "与当前学习节点高度相关，且可直接用于实操。",
    }


def safe_get(data: dict, *keys, default=None):
    value = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value
