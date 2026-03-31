from .schemas import Resource


def rerank_resources(resources: list[Resource], top_k: int = 5) -> list[Resource]:
    sorted_items = sorted(resources, key=lambda x: x.source_score, reverse=True)
    deduped: list[Resource] = []
    seen_urls = set()

    for item in sorted_items:
        if str(item.url) in seen_urls:
            continue
        deduped.append(item)
        seen_urls.add(str(item.url))
        if len(deduped) >= top_k:
            break

    return deduped
