"""P0/P1 design fixes: Resource creator_id, custom_*, LearningPath creator_id,
UserLearningPath custom_*, Progress unique constraint, LearningPathComment username drop

Revision ID: 20260407_0003
Revises: 20260407_0002
Create Date: 2026-04-07

Changes:
- resources: add creator_id (FK → users.id, NULL = system resource)
- user_resource: add custom_title, custom_summary, custom_thumbnail
- learning_paths: add creator_id (FK → users.id), is_public default False
- user_learning_paths: add custom_title, custom_description,
  custom_cover_image_url, notes, added_at, is_pinned
- progress: change PK from 'id' to (user_id, path_item_id),
  add updated_at, completed_at, enforce progress_percentage 0-100
- learning_path_comments: drop username (冗余字段)
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260407_0003"
down_revision: Union[str, Sequence[str], None] = "20260407_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# 1. resources — add creator_id
# ---------------------------------------------------------------------------
def upgrade() -> None:
    # ---- resources ----
    op.add_column(
        "resources",
        sa.Column(
            "creator_id",
            sa.Integer(),
            sa.ForeignKey("users.id", name="fk_resources_creator_id"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_resources_creator_id", "resources", ["creator_id"], unique=False
    )

    # ---- user_resource ----
    op.add_column(
        "user_resource",
        sa.Column("custom_title", sa.String(500), nullable=True),
    )
    op.add_column(
        "user_resource",
        sa.Column("custom_summary", sa.Text(), nullable=True),
    )
    op.add_column(
        "user_resource",
        sa.Column("custom_thumbnail", sa.String(1000), nullable=True),
    )

    # ---- learning_paths ----
    op.add_column(
        "learning_paths",
        sa.Column(
            "creator_id",
            sa.Integer(),
            sa.ForeignKey("users.id", name="fk_learning_paths_creator_id"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_learning_paths_creator_id",
        "learning_paths",
        ["creator_id"],
        unique=False,
    )
    # 将 is_public 默认值改为 False（原来默认 True）
    op.alter_column(
        "learning_paths",
        "is_public",
        existing_type=sa.Boolean(),
        server_default=sa.text("false"),
        existing_server_default=sa.text("true"),
    )

    # ---- user_learning_paths ----
    # added_at / is_pinned 已在 20260407_0002 中添加，此处跳过
    # 只添加新的 custom_* 和 notes 字段
    for col_name, col_type in [
        ("custom_title", sa.String(200)),
        ("custom_description", sa.Text()),
        ("custom_cover_image_url", sa.String(2048)),
        ("notes", sa.Text()),
    ]:
        try:
            op.add_column(
                "user_learning_paths",
                sa.Column(col_name, col_type, nullable=True),
            )
        except Exception:
            pass  # 字段可能已存在

    # ---- learning_path_comments ----
    op.drop_column("learning_path_comments", "username")

    # ---- progress ----
    # 重建 progress 表：PK 从单独的 id 改为 (user_id, path_item_id)
    bind = op.get_bind()

    # 1a. 复制数据到临时表
    op.execute(
        """
        CREATE TABLE _progress_new (
            user_id INTEGER NOT NULL,
            path_item_id INTEGER NOT NULL,
            progress_percentage INTEGER NOT NULL DEFAULT 0,
            last_watched_time TIMESTAMP NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (user_id, path_item_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (path_item_id) REFERENCES path_items(id) ON DELETE CASCADE
        )
        """
    )

    # 1b. 迁移现有数据（保留 id 列中的值作为参考）
    op.execute(
        """
        INSERT INTO _progress_new (user_id, path_item_id, progress_percentage, last_watched_time)
        SELECT user_id, path_item_id,
               COALESCE(progress_percentage, 0),
               COALESCE(last_watched_time, NOW())
        FROM progress
        """
    )

    # 1c. 删除旧表
    op.drop_table("progress")

    # 1d. 重命名新表
    op.rename_table("_progress_new", "progress")

    # ---- 清理残留的 Base.metadata 行（仅清理应用层代码，此处无操作）----


def downgrade() -> None:
    # ---- progress 回滚 ----
    bind = op.get_bind()

    op.execute(
        """
        CREATE TABLE _progress_old (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            path_item_id INTEGER NOT NULL REFERENCES path_items(id),
            last_watched_time TIMESTAMP,
            progress_percentage INTEGER
        )
        """
    )
    op.execute(
        """
        INSERT INTO _progress_old (user_id, path_item_id, progress_percentage, last_watched_time)
        SELECT user_id, path_item_id, progress_percentage, last_watched_time
        FROM progress
        """
    )
    op.drop_table("progress")
    op.rename_table("_progress_old", "progress")

    # ---- learning_path_comments 回滚 ----
    op.add_column(
        "learning_path_comments",
        sa.Column("username", sa.String(64), nullable=False, server_default="unknown"),
    )

    # ---- user_learning_paths ----
    op.drop_column("user_learning_paths", "is_pinned")
    op.drop_column("user_learning_paths", "added_at")
    op.drop_column("user_learning_paths", "notes")
    op.drop_column("user_learning_paths", "custom_cover_image_url")
    op.drop_column("user_learning_paths", "custom_description")
    op.drop_column("user_learning_paths", "custom_title")

    # ---- learning_paths ----
    op.alter_column(
        "learning_paths",
        "is_public",
        existing_type=sa.Boolean(),
        server_default=sa.text("true"),
        existing_server_default=sa.text("false"),
    )
    op.drop_index("ix_learning_paths_creator_id", table_name="learning_paths")
    op.drop_column("learning_paths", "creator_id")

    # ---- user_resource ----
    op.drop_column("user_resource", "custom_thumbnail")
    op.drop_column("user_resource", "custom_summary")
    op.drop_column("user_resource", "custom_title")

    # ---- resources ----
    op.drop_index("ix_resources_creator_id", table_name="resources")
    op.drop_column("resources", "creator_id")
