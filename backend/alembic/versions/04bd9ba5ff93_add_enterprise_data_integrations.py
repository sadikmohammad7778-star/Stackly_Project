from alembic import op
import sqlalchemy as sa

revision = "04bd9ba5ff93"
down_revision = "b54c882f9e13"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "integrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("connection_config", sa.JSON(), nullable=False),
        sa.Column("encrypted_credentials", sa.Text(), nullable=True),
        sa.Column("target_module", sa.String(50), nullable=False),
        sa.Column("sync_strategy", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_integrations_company_source",
        "integrations",
        ["company_id", "source_type"]
    )

    op.create_index(
        "ix_integrations_company_status",
        "integrations",
        ["company_id", "status"]
    )

    op.create_index(
        "ix_integrations_id",
        "integrations",
        ["id"]
    )

    op.create_table(
        "integration_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("integration_id", sa.Integer(), nullable=False),
        sa.Column("source_field", sa.String(150), nullable=False),
        sa.Column("target_field", sa.String(150), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("transformation_config", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["integration_id"], ["integrations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "integration_id",
            "source_field",
            name="uq_integration_source_field"
        )
    )

    op.create_index(
        "ix_integration_mappings_id",
        "integration_mappings",
        ["id"]
    )

    op.create_index(
        "ix_integration_mappings_integration",
        "integration_mappings",
        ["integration_id"]
    )

    op.create_table(
        "integration_schedules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("integration_id", sa.Integer(), nullable=False),
        sa.Column("frequency", sa.String(30), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=True),
        sa.Column("scheduled_time", sa.Time(), nullable=True),
        sa.Column("timezone", sa.String(100), nullable=False),
        sa.Column("cron_expression", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_status", sa.String(30), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "frequency IN ('daily', 'weekly', 'custom')",
            name="ck_integration_schedule_frequency"
        ),
        sa.CheckConstraint(
            "day_of_week IS NULL OR (day_of_week >= 0 AND day_of_week <= 6)",
            name="ck_integration_schedule_day"
        ),
        sa.ForeignKeyConstraint(["integration_id"], ["integrations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("integration_id")
    )

    op.create_index(
        "ix_integration_schedules_id",
        "integration_schedules",
        ["id"]
    )

    op.create_index(
        "ix_integration_schedules_next_run",
        "integration_schedules",
        ["next_run_at"]
    )

    op.create_table(
        "integration_syncs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("integration_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("triggered_by", sa.Integer(), nullable=True),
        sa.Column("trigger_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("total_records", sa.Integer(), nullable=False),
        sa.Column("processed_records", sa.Integer(), nullable=False),
        sa.Column("inserted_records", sa.Integer(), nullable=False),
        sa.Column("updated_records", sa.Integer(), nullable=False),
        sa.Column("skipped_records", sa.Integer(), nullable=False),
        sa.Column("failed_records", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("execution_metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'completed_with_errors', 'failed', 'cancelled')",
            name="ck_integration_sync_status"
        ),
        sa.CheckConstraint(
            "trigger_type IN ('manual', 'scheduled', 'retry', 'initial', 'incremental')",
            name="ck_integration_sync_trigger_type"
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["integration_id"], ["integrations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["triggered_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_integration_syncs_id",
        "integration_syncs",
        ["id"]
    )

    op.create_index(
        "ix_integration_syncs_company_status",
        "integration_syncs",
        ["company_id", "status"]
    )

    op.create_index(
        "ix_integration_syncs_integration_created",
        "integration_syncs",
        ["integration_id", "created_at"]
    )

    op.create_table(
        "integration_sync_errors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sync_id", sa.Integer(), nullable=False),
        sa.Column("source_record_id", sa.String(150), nullable=True),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("error_category", sa.String(100), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("source_data", sa.JSON(), nullable=True),
        sa.Column("retry_status", sa.String(30), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("is_retryable", sa.Boolean(), nullable=False),
        sa.Column("last_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["sync_id"], ["integration_syncs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_integration_sync_errors_id",
        "integration_sync_errors",
        ["id"]
    )

    op.create_index(
        "ix_integration_sync_errors_retry",
        "integration_sync_errors",
        ["retry_status", "is_retryable"]
    )

    op.create_index(
        "ix_integration_sync_errors_sync",
        "integration_sync_errors",
        ["sync_id"]
    )


def downgrade():

    op.drop_index(
        "ix_integration_sync_errors_sync",
        table_name="integration_sync_errors"
    )

    op.drop_index(
        "ix_integration_sync_errors_retry",
        table_name="integration_sync_errors"
    )

    op.drop_index(
        "ix_integration_sync_errors_id",
        table_name="integration_sync_errors"
    )

    op.drop_table("integration_sync_errors")

    op.drop_index(
        "ix_integration_syncs_integration_created",
        table_name="integration_syncs"
    )

    op.drop_index(
        "ix_integration_syncs_company_status",
        table_name="integration_syncs"
    )

    op.drop_index(
        "ix_integration_syncs_id",
        table_name="integration_syncs"
    )

    op.drop_table("integration_syncs")

    op.drop_index(
        "ix_integration_schedules_next_run",
        table_name="integration_schedules"
    )

    op.drop_index(
        "ix_integration_schedules_id",
        table_name="integration_schedules"
    )

    op.drop_table("integration_schedules")

    op.drop_index(
        "ix_integration_mappings_integration",
        table_name="integration_mappings"
    )

    op.drop_index(
        "ix_integration_mappings_id",
        table_name="integration_mappings"
    )

    op.drop_table("integration_mappings")

    op.drop_index(
        "ix_integrations_company_status",
        table_name="integrations"
    )

    op.drop_index(
        "ix_integrations_company_source",
        table_name="integrations"
    )

    op.drop_index(
        "ix_integrations_id",
        table_name="integrations"
    )

    op.drop_table("integrations")