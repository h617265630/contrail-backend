from langgraph.graph import END, START, StateGraph

from .chains import run_generator, run_intent, run_planner
from .retrieval import retrieve_resources
from .state import LearningState
from .validation import validate_output


def _intent_node(state: LearningState) -> dict:
    return {"intent": run_intent(state["user_input"])}


def _planner_node(state: LearningState) -> dict:
    return {"plan": run_planner(state["intent"])}


def _retrieval_node(state: LearningState) -> dict:
    return {"resources": retrieve_resources(state["plan"])}


def _generator_node(state: LearningState) -> dict:
    final_output = run_generator(state["intent"], state["plan"], state["resources"])
    warnings = validate_output(final_output)
    return {"final_output": final_output, "warnings": warnings}


def build_graph():
    workflow = StateGraph(LearningState)
    workflow.add_node("intent", _intent_node)
    workflow.add_node("planner", _planner_node)
    workflow.add_node("retrieval", _retrieval_node)
    workflow.add_node("generator", _generator_node)

    workflow.add_edge(START, "intent")
    workflow.add_edge("intent", "planner")
    workflow.add_edge("planner", "retrieval")
    workflow.add_edge("retrieval", "generator")
    workflow.add_edge("generator", END)

    return workflow.compile()
