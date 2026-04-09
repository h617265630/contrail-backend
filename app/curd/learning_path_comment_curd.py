from sqlalchemy.orm import Session
from app.models.learning_path_comment import LearningPathComment
from app.models.rbac.user import User
from typing import List

def create_comment(db: Session, learning_path_id: int, user: User, content: str) -> LearningPathComment:
    if not content or not content.strip():
        raise ValueError("Comment content cannot be empty")
    comment = LearningPathComment(
        learning_path_id=learning_path_id,
        user_id=user.id,
        username=user.username,
        content=content.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def list_comments(db: Session, learning_path_id: int) -> List[LearningPathComment]:
    return db.query(LearningPathComment).filter(LearningPathComment.learning_path_id == learning_path_id).order_by(LearningPathComment.created_at.desc()).all()
