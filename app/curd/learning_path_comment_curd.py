from sqlalchemy.orm import Session, joinedload
from app.models.learning_path_comment import LearningPathComment
from app.models.rbac.user import User
from typing import List

def create_comment(db: Session, learning_path_id: int, user: User, content: str) -> LearningPathComment:
    comment = LearningPathComment(
        learning_path_id=learning_path_id,
        user_id=user.id,
        content=content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    # 手动挂载 relationship，确保序列化时能读到 user
    comment.user = user
    return comment

def list_comments(db: Session, learning_path_id: int) -> List[LearningPathComment]:
    return (
        db.query(LearningPathComment)
        .options(joinedload(LearningPathComment.user))
        .filter(LearningPathComment.learning_path_id == learning_path_id)
        .order_by(LearningPathComment.created_at.desc())
        .all()
    )
