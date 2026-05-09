"""Lightweight schema migrations for legacy installs."""

from sqlalchemy import inspect, text

from app.db.base import engine

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
