from langgraph.graph import END, START, StateGraph

from .chains import run_generator, run_intent, run_tutorial_research
from .retrieval import retrieve_resources
from .state import LearningState
from .validation import validate_output


def _intent_node(state: LearningState) -> dict:
    return {"intent": run_intent(state["user_input"])}


def _planning_node(state: LearningState) -> dict:
    """合并 tutorial_research 和 planner：一次调用返回完整结构"""
    tutorial_context, plan = run_tutorial_research(state["intent"])
    return {
        "tutorial_context": tutorial_context,
        "plan": plan,
    }


def _retrieval_node(state: LearningState) -> dict:
    return {"resources": retrieve_resources(state["plan"])}


def _generator_node(state: LearningState) -> dict:
    final_output = run_generator(state["intent"], state["plan"], state["resources"], state["tutorial_context"])
    warnings = validate_output(final_output)
    return {"final_output": final_output, "warnings": warnings}


def build_graph():
    workflow = StateGraph(LearningState)
    workflow.add_node("intent", _intent_node)
    workflow.add_node("planning", _planning_node)  # 合并后的规划节点
    workflow.add_node("retrieval", _retrieval_node)
    workflow.add_node("generator", _generator_node)

    workflow.add_edge(START, "intent")
    workflow.add_edge("intent", "planning")
    workflow.add_edge("planning", "retrieval")
    workflow.add_edge("retrieval", "generator")
    workflow.add_edge("generator", END)

    return workflow.compile()
