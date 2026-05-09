"""Local temp-folder management for user-uploaded inspiration / reference images."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.core.config import settings


def reference_dir(user_id: int) -> Path:
    """Return the per-user directory for inspiration images, creating it if needed."""
    path = settings.temp_path / f"user_{user_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def generated_dir(user_id: int) -> Path:
    """Return the per-user directory for generated images."""
    path = settings.temp_path / "generated" / f"user_{user_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _existing_indexes(directory: Path) -> list[int]:
    indexes: list[int] = []
    for file in directory.glob("reference_*.png"):
        try:
            indexes.append(int(file.stem.split("_")[-1]))
        except ValueError:
            continue
    return indexes


def next_reference_filename(user_id: int) -> str:
    """Return the next available `reference_N.png` filename for the user."""
    next_index = max(_existing_indexes(reference_dir(user_id)), default=0) + 1
    return f"reference_{next_index}.png"


def latest_reference_file(user_id: int) -> Optional[Path]:
    """Return the most recent reference file for the user, if any."""
    directory = reference_dir(user_id)
    candidates: list[tuple[int, Path]] = []
    for file in directory.glob("reference_*.png"):
        try:
            candidates.append((int(file.stem.split("_")[-1]), file))
        except ValueError:
            continue
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]
