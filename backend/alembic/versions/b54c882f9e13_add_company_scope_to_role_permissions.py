from alembic import op
import sqlalchemy as sa


revision = "b54c882f9e13"
down_revision = "2bc591a0d0e6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "role_permissions",
        sa.Column("company_id", sa.Integer(), nullable=True),
    )

    op.create_foreign_key(
        "fk_role_permissions_company_id",
        "role_permissions",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        """
        UPDATE role_permissions
        SET company_id = 3
        WHERE company_id IS NULL
        """
    )

    op.alter_column(
        "role_permissions",
        "company_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_constraint(
        "uq_role_permissions_role_permission",
        "role_permissions",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_company_role_permission",
        "role_permissions",
        ["company_id", "role", "permission_id"],
    )

    op.create_index(
        "ix_role_permissions_company_role",
        "role_permissions",
        ["company_id", "role"],
    )


def downgrade():
    op.drop_index(
        "ix_role_permissions_company_role",
        table_name="role_permissions",
    )

    op.drop_constraint(
        "uq_company_role_permission",
        "role_permissions",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_role_permissions_role_permission",
        "role_permissions",
        ["role", "permission_id"],
    )

    op.drop_constraint(
        "fk_role_permissions_company_id",
        "role_permissions",
        type_="foreignkey",
    )

    op.drop_column("role_permissions", "company_id")