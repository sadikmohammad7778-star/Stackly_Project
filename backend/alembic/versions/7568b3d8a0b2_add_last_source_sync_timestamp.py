from alembic import op
import sqlalchemy as sa

revision = "7568b3d8a0b2"
down_revision = "c5338300f976"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "integrations",
        sa.Column(
            "last_source_sync_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )


def downgrade():
    op.drop_column(
        "integrations",
        "last_source_sync_at"
    )