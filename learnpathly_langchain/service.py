from .graph import build_graph
from .schemas import LearningPathResponse

_graph = build_graph()


def generate_learning_path(query: str) -> LearningPathResponse:
    result = _graph.invoke(
        {
            "user_input": query,
            "intent": None,
            "tutorial_context": None,
            "plan": [],
            "resources": {},
            "warnings": [],
            "final_output": None,
        }
    )

    return LearningPathResponse(data=result["final_output"], warnings=result.get("warnings", []))
