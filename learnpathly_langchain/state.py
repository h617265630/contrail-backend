from typing import TypedDict

from .schemas import Intent, LearningPathOutput, PlanNode, Resource


class LearningState(TypedDict):
    user_input: str
    intent: Intent
    plan: list[PlanNode]
    resources: dict[str, list[Resource]]
    warnings: list[str]
    final_output: LearningPathOutput
