"""Lightweight schema migrations for legacy installs."""

from sqlalchemy import inspect, text

from app.db.base import engine

_DEFAULT_USER_ROLE = "customer"

_LEGACY_DROP_COLUMNS = (
    "style_family",
    "metal",
    "style_direction",
    "setting",
    "stone_name",
    "stone_color",
    "fit_label",
    "generated_image_local_path",
    "generated_model",
)


def migrate_user_schema() -> None:
    """Bring the users table in line with the current role-based model."""
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    columns = {col["name"] for col in inspector.get_columns("users")}

    with engine.begin() as connection:
        if "role" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20)"))

        connection.execute(
            text(f"UPDATE users SET role = '{_DEFAULT_USER_ROLE}' WHERE role IS NULL")
        )

        if engine.dialect.name == "postgresql":
            connection.execute(
                text(
                    f"ALTER TABLE users ALTER COLUMN role SET DEFAULT '{_DEFAULT_USER_ROLE}'"
                )
            )
            connection.execute(text("ALTER TABLE users ALTER COLUMN role SET NOT NULL"))
            connection.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS ux_users_single_admin "
                    "ON users (role) WHERE role = 'admin'"
                )
            )


def migrate_ring_design_schema() -> None:
    """Bring the ring_designs table in line with the simplified payload schema."""
    inspector = inspect(engine)
    if not inspector.has_table("ring_designs"):
        return

    columns = {col["name"] for col in inspector.get_columns("ring_designs")}

    with engine.begin() as connection:
        if "design_payload" not in columns:
            connection.execute(text("ALTER TABLE ring_designs ADD COLUMN design_payload JSON"))

        for column_name in _LEGACY_DROP_COLUMNS:
            if column_name in columns:
                connection.execute(
                    text(f'ALTER TABLE ring_designs DROP COLUMN IF EXISTS "{column_name}"')
                )
