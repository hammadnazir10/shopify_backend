"""Inspiration-image upload pipeline — validate, normalise to PNG, persist locally + S3."""

from __future__ import annotations

import asyncio
import io

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import settings
from app.schemas import ImageUploadResponse
from app.services import reference_image_service
from app.services.s3_service import upload_image as s3_upload


async def process_inspiration_upload(user_id: int, file: UploadFile) -> ImageUploadResponse:
    """Validate, normalise, and persist an uploaded inspiration image."""
    _validate_content_type(file.content_type)
    contents = await file.read()
    _validate_size(len(contents))

    user_dir = reference_image_service.reference_dir(user_id)
    filename = reference_image_service.next_reference_filename(user_id)
    file_path = user_dir / filename

    # Normalise to PNG so downstream code can rely on a single format.
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image.save(file_path, format="PNG")

    s3_key = f"references/user_{user_id}/{filename}"
    image_url = await asyncio.to_thread(s3_upload, s3_key, file_path.read_bytes(), "image/png")

    return ImageUploadResponse(image_url=image_url, filename=filename)


def _validate_content_type(content_type: str | None) -> None:
    if content_type not in settings.allowed_image_mime_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type {content_type!r}. "
                f"Allowed: {sorted(settings.allowed_image_mime_types)}"
            ),
        )


def _validate_size(size_bytes: int) -> None:
    if size_bytes > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.max_upload_bytes // (1024 * 1024)} MB limit.",
        )
