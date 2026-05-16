"""Add role column to users.

Revision ID: 20260516_add_user_role
Revises:
Create Date: 2026-05-16 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260516_add_user_role"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("users")}

    if "role" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "role",
                sa.String(length=20),
                nullable=False,
                server_default=sa.text("'customer'"),
            ),
        )

    op.execute("UPDATE users SET role = 'customer' WHERE role IS NULL")

    index_names = {idx["name"] for idx in inspector.get_indexes("users")}
    if "ux_users_single_admin" not in index_names:
        op.create_index(
            "ux_users_single_admin",
            "users",
            ["role"],
            unique=True,
            postgresql_where=sa.text("role = 'admin'"),
        )


def downgrade() -> None:
    op.drop_index("ux_users_single_admin", table_name="users")
    op.drop_column("users", "role")
