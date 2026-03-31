from typing import TypedDict

from .schemas import Intent, LearningNode, LearningPathOutput, Resource, TutorialContext


class LearningState(TypedDict):
    user_input: str
    intent: Intent
    tutorial_context: TutorialContext
    plan: list[LearningNode]
    resources: dict[str, list[Resource]]
    warnings: list[str]
    final_output: LearningPathOutput
