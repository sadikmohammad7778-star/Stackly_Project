"""add background job retry fields

Revision ID: c5338300f976
Revises: 04bd9ba5ff93
Create Date: 2026-11-04 17:55:37.290747
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c5338300f976"
down_revision: Union[str, Sequence[str], None] = "04bd9ba5ff93"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "background_jobs",
        sa.Column(
            "max_retries",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("3"),
        ),
    )

    op.add_column(
        "background_jobs",
        sa.Column(
            "next_retry_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "background_jobs",
        sa.Column(
            "last_retry_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_background_jobs_status_retry",
        "background_jobs",
        ["status", "next_retry_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_background_jobs_status_retry",
        table_name="background_jobs",
    )

    op.drop_column("background_jobs", "last_retry_at")
    op.drop_column("background_jobs", "next_retry_at")
    op.drop_column("background_jobs", "max_retries")