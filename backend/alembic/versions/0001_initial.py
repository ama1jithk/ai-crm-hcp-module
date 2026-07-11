"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-11
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "hcps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("specialty", sa.String(150)),
        sa.Column("institution", sa.String(200)),
        sa.Column("email", sa.String(150)),
        sa.Column("phone", sa.String(50)),
        sa.Column("territory", sa.String(100)),
        sa.Column("preferred_products", sa.JSON),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "interactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("hcp_id", sa.String(36), sa.ForeignKey("hcps.id"), nullable=False),
        sa.Column("rep_name", sa.String(150), nullable=False),
        sa.Column("channel", sa.String(20)),
        sa.Column("interaction_type", sa.String(20)),
        sa.Column("interaction_date", sa.DateTime),
        sa.Column("raw_text", sa.Text),
        sa.Column("summary", sa.Text),
        sa.Column("topics_discussed", sa.JSON),
        sa.Column("products_discussed", sa.JSON),
        sa.Column("sentiment", sa.String(50)),
        sa.Column("samples_provided", sa.JSON),
        sa.Column("follow_up_required", sa.Boolean),
        sa.Column("follow_up_notes", sa.Text),
        sa.Column("attachments", sa.JSON),
        sa.Column("is_edited", sa.Boolean),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_table(
        "follow_ups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("interaction_id", sa.String(36), sa.ForeignKey("interactions.id"), nullable=False),
        sa.Column("hcp_id", sa.String(36), sa.ForeignKey("hcps.id"), nullable=False),
        sa.Column("due_date", sa.DateTime, nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("status", sa.String(50)),
        sa.Column("created_at", sa.DateTime),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("tool_name", sa.String(100)),
        sa.Column("tool_payload", sa.JSON),
        sa.Column("created_at", sa.DateTime),
    )


def downgrade():
    op.drop_table("chat_messages")
    op.drop_table("follow_ups")
    op.drop_table("interactions")
    op.drop_table("hcps")
