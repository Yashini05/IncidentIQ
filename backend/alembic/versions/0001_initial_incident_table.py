"""Initial incident table.

Revision ID: 0001_initial_incident_table
Revises:
Create Date: 2026-07-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_incident_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column("incident_id", sa.String(length=32), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("timestamp", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=True),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("affected_services", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("prediction", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("incidents")
