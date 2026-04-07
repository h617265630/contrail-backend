from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CommentUser(BaseModel):
    id: int
    username: str
    display_name: str | None = None
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LearningPathCommentBase(BaseModel):
    content: str


class LearningPathCommentCreate(LearningPathCommentBase):
    pass


class LearningPathCommentResponse(LearningPathCommentBase):
    id: int
    learning_path_id: int
    user_id: int
    created_at: datetime
    user: CommentUser | None = None

    model_config = ConfigDict(from_attributes=True)
