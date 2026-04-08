"""
Models package initializer.

Avoid eager imports here to prevent circular-import issues and tooling resolution
problems. Prefer importing concrete models from their module paths where needed,
e.g., `from app.models.user import User` in your code.
"""

__all__ = [
    "User",
    "Category",
    "LearningPath",
    "LearningPathFork",
    "PathItem",
    "UserLearningPath",
]