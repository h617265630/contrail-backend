from pydantic import BaseModel
from datetime import datetime

class LearningPathCommentBase(BaseModel):
    content: str

class LearningPathCommentCreate(LearningPathCommentBase):
    pass

class LearningPathCommentResponse(LearningPathCommentBase):
    id: int
    learning_path_id: int
    user_id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True
