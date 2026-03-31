from .rerank import rerank_resources
from .schemas import LearningNode, Resource
from .tools import search_github, search_web, search_youtube


def retrieve_resources_for_node(node_title: str) -> list[Resource]:
    raw_items = []
    raw_items.extend(search_youtube(node_title))
    raw_items.extend(search_github(node_title))
    raw_items.extend(search_web(node_title))
    resources = [Resource(**item) for item in raw_items]
    return rerank_resources(resources)


def retrieve_resources(plan: list[LearningNode]) -> dict[str, list[Resource]]:
    return {node.title: retrieve_resources_for_node(node.title) for node in plan}
