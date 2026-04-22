import asyncio
import io
import uuid
from pathlib import Path

from PIL import Image
from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from google import genai
from google.genai import types

from app.services.llm import generate_design_brief
from app.services.s3 import ensure_bucket_exists, upload_image as s3_upload
from app.services.stone import (
    assess_stone_by_name,
    get_stone_suitability_for_own_stone,
    resolve_stone_from_yss_reference,
    score_stones_by_color,
)
from app.config import settings
from app.models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageUploadResponse,
    RingDesignResponse,
    RingSelectionPayload,
    StoneBranch,
    StoneSuitability,
)

_IMAGEN_MODEL      = "gemini-3.1-flash-image-preview"  # text-to-image
_IMAGEN_REF_MODEL  = "gemini-2.5-flash-image"         # multimodal: image-in + image-out
_OUTPUT_SIZE       = (1080, 1080)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/api", tags=["Ring Design"])


def _upscale_to_hd(raw_bytes: bytes) -> bytes:
    """Upscale image bytes to _OUTPUT_SIZE using Lanczos."""
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    if img.size != _OUTPUT_SIZE:
        img = img.resize(_OUTPUT_SIZE, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()


@router.on_event("startup")
async def _ensure_s3_bucket():
    await asyncio.to_thread(ensure_bucket_exists)


# ---------------------------------------------------------------------------
# Q9 — Image upload
# ---------------------------------------------------------------------------

@router.post(
    "/upload-image",
    response_model=ImageUploadResponse,
    summary="Upload an inspiration image (Q9)",
)
async def upload_inspiration_image(file: UploadFile = File(...)):
    """
    Accepts a JPG / PNG / WebP / GIF (max 10 MB).
    Returns the URL to pass as inspiration_image_url in the ring-selection payload.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {sorted(ALLOWED_TYPES)}",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB limit.")

    suffix = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    unique_name = f"uploads/{uuid.uuid4().hex}{suffix}"
    image_url = await asyncio.to_thread(
        s3_upload, unique_name, contents, file.content_type or "image/jpeg"
    )

    return ImageUploadResponse(image_url=image_url, filename=unique_name)


# ---------------------------------------------------------------------------
# Ring selection submission
# ---------------------------------------------------------------------------

@router.post(
    "/ring-selection",
    response_model=RingDesignResponse,
    summary="Submit a ring design questionnaire",
    description=(
        "Accepts ring-specific answers (jewelry_type is implicitly Ring). "
        "Validates stone suitability against ring fit and protection rules, "
        "then returns a design brief with a detailed visual_description "
        "prompt ready for image generation."
    ),
)
async def submit_ring_selection(body: RingSelectionPayload):
    submission = body.to_questionnaire_submission()
    stone_assessment: StoneSuitability | None = None

    if submission.stone_branch == StoneBranch.already_have:
        if submission.own_stone and submission.own_stone.stone_type:
            stone_assessment = get_stone_suitability_for_own_stone(
                stone_type=submission.own_stone.stone_type,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )

    elif submission.stone_branch == StoneBranch.yss_sku:
        if submission.yss_reference:
            resolved = resolve_stone_from_yss_reference(submission.yss_reference)
            if resolved:
                stone_assessment = assess_stone_by_name(
                    stone_name=resolved,
                    jewelry_type=submission.jewelry_type,
                    wear_frequency=submission.wear_frequency,
                )

    elif submission.stone_branch == StoneBranch.help_choose:
        if submission.chosen_stone_name:
            stone_assessment = assess_stone_by_name(
                stone_name=submission.chosen_stone_name,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )
        elif submission.chosen_color:
            ranked = score_stones_by_color(
                color=submission.chosen_color,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )
            if ranked:
                stone_assessment = ranked[0]

    try:
        brief = await generate_design_brief(submission, stone_assessment)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")

    summary = (
        f"Ring · {submission.style_family or 'Custom'} · "
        f"{submission.metal.value if submission.metal else 'Mixed metal'} · "
        f"{submission.style_direction.value if submission.style_direction else (submission.gender_type or 'Unspecified')}"
    )
    if stone_assessment:
        summary += f" · {stone_assessment.stone_name} ({stone_assessment.fit_label.value})"

    return RingDesignResponse(
        summary=summary,
        image_prompt=brief.image_prompt,
        cautions=brief.cautions,
    )


# ---------------------------------------------------------------------------
# Image generation via Gemini Imagen
# ---------------------------------------------------------------------------

@router.post(
    "/generate-image",
    response_model=ImageGenerateResponse,
    summary="Generate an image from a prompt using Gemini Imagen",
    description=(
        "Accepts a prompt (required) and an optional reference image. "
        "Without an image: pure text-to-image generation. "
        "With an image: uses it as a visual reference to guide generation."
    ),
)
async def generate_image(
    prompt: str = Form(..., description="Image generation prompt"),
    image: UploadFile = File(None, description="Optional reference image (JPG / PNG / WebP)"),
):
    if not settings.gemini_api:
        raise HTTPException(
            status_code=503,
            detail="Gemini_API key is not configured. Add it to your .env file.",
        )

    client = genai.Client(api_key=settings.gemini_api)

    if image is not None:
        ref_bytes = await image.read()
        mime = image.content_type or "image/png"
        try:
            gen_response = await asyncio.to_thread(
                client.models.generate_content,
                model=_IMAGEN_REF_MODEL,
                contents=[
                    types.Content(parts=[
                        types.Part(text=f"Using the provided image as a visual reference, generate a new image based on this description: {prompt}"),
                        types.Part(inline_data=types.Blob(mime_type=mime, data=ref_bytes)),
                    ])
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Gemini image-ref error: {exc}")

        image_bytes = None
        for part in gen_response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                break
        if not image_bytes:
            raise HTTPException(status_code=502, detail="Gemini returned no image in response.")
        used_model = _IMAGEN_REF_MODEL

    else:
        try:
            gen_response = await asyncio.to_thread(
                client.models.generate_content,
                model=_IMAGEN_MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Gemini image generation error: {exc}")

        image_bytes = None
        for part in gen_response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                break
        if not image_bytes:
            raise HTTPException(status_code=502, detail="Gemini returned no image in response.")
        used_model = _IMAGEN_MODEL

    image_bytes = _upscale_to_hd(image_bytes)
    filename = f"generated/{uuid.uuid4().hex}.png"
    image_url = await asyncio.to_thread(s3_upload, filename, image_bytes, "image/png")

    return ImageGenerateResponse(
        image_url=image_url,
        model=used_model,
        prompt=prompt,
    )
