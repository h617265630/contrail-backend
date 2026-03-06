"""link resource + user_resource association

Revision ID: 20260111_0001
Revises: 
Create Date: 2026-01-11

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260111_0001"
down_revision = None
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1) Extend enum type in Postgres
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE resourcetype ADD VALUE IF NOT EXISTS 'link'")

    # 2) Add timestamps on resources (if missing)
    if inspector.has_table("resources"):
        with op.batch_alter_table("resources") as batch:
            if not _has_column(inspector, "resources", "created_at"):
                batch.add_column(
                    sa.Column(
                        "created_at",
                        sa.DateTime(),
                        nullable=False,
                        server_default=sa.text("now()"),
                    )
                )
            if not _has_column(inspector, "resources", "updated_at"):
                batch.add_column(
                    sa.Column(
                        "updated_at",
                        sa.DateTime(),
                        nullable=False,
                        server_default=sa.text("now()"),
                    )
                )

    # 3) link_resources table
    if not inspector.has_table("link_resources"):
        op.create_table(
            "link_resources",
            sa.Column("id", sa.Integer(), sa.ForeignKey("resources.id"), primary_key=True),
            sa.Column("url", sa.String(length=1000), nullable=False),
            sa.Column("source", sa.String(length=200), nullable=True),
            sa.Column("category", sa.String(length=100), nullable=True),
            sa.Column("thumbnail_url", sa.String(length=1000), nullable=True),
            sa.UniqueConstraint("url", name="uq_link_resources_url"),
        )
        op.create_index("ix_link_resources_url", "link_resources", ["url"], unique=True)

    # 4) user_resource association table
    if not inspector.has_table("user_resource"):
        op.create_table(
            "user_resource",
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
            sa.Column("resource_id", sa.Integer(), sa.ForeignKey("resources.id"), primary_key=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
            sa.UniqueConstraint("user_id", "resource_id", name="uq_user_resource"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("user_resource"):
        op.drop_table("user_resource")

    if inspector.has_table("link_resources"):
        op.drop_index("ix_link_resources_url", table_name="link_resources")
        op.drop_table("link_resources")

    # columns
    if inspector.has_table("resources"):
        with op.batch_alter_table("resources") as batch:
            if _has_column(inspector, "resources", "updated_at"):
                batch.drop_column("updated_at")
            if _has_column(inspector, "resources", "created_at"):
                batch.drop_column("created_at")

    # NOTE: Postgres enum value removal is not safely reversible.
