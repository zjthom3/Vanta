"""add application notes

Revision ID: 28c3770a1299
Revises: f376bcb09ca6
Create Date: 2025-10-29 19:45:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "28c3770a1299"
down_revision = "f376bcb09ca6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "application_notes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("application_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("body", sa.String(), nullable=True),
        sa.Column("attachment_url", sa.String(), nullable=True),
        sa.Column("attachment_name", sa.String(), nullable=True),
        sa.Column("attachment_content_type", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_application_notes_application_id"),
        "application_notes",
        ["application_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_application_notes_user_id"),
        "application_notes",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_application_notes_user_id"), table_name="application_notes")
    op.drop_index(op.f("ix_application_notes_application_id"), table_name="application_notes")
    op.drop_table("application_notes")
