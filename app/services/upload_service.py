"""Inspiration-image upload — validate, normalise to PNG, upload directly to S3.

No files are written to local disk; everything stays in memory and goes to S3.
"""

from __future__ import annotations

import asyncio
import io
import uuid

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import settings
from app.schemas.responses import ImageUploadResponse
from app.services.s3_service import upload_image as s3_upload


async def process_inspiration_upload(file: UploadFile) -> ImageUploadResponse:
    """Validate, normalise, and upload an inspiration image to S3.

    This variant stores uploads without a user association under
    `references/unidentified/` so the endpoint can accept only a file.
    """
    _validate_content_type(file.content_type)
    contents = await file.read()
    _validate_size(len(contents))

    png_bytes = _normalise_to_png(contents)
    filename = f"{uuid.uuid4().hex}.png"
    s3_key = f"references/unidentified/{filename}"

    image_url = await asyncio.to_thread(s3_upload, s3_key, png_bytes, "image/png")
    return ImageUploadResponse(image_url=image_url, filename=filename)


def _normalise_to_png(raw: bytes) -> bytes:
    """Convert any supported image into RGB PNG bytes in-memory."""
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


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
