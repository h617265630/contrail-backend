from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class LearningPathFork(Base):
    __tablename__ = "learning_path_forks"

    id = Column(Integer, primary_key=True, index=True)
    source_path_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False, index=True)
    forked_path_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("forked_path_id", name="uq_fork_forked_path"),
    )

    def __repr__(self):
        return f"<LearningPathFork(source={self.source_path_id}, forked={self.forked_path_id}, user={self.user_id})>"
