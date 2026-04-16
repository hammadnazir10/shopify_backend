import asyncio
import base64
import io
import uuid
from pathlib import Path

from PIL import Image

from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from google import genai
from google.genai import types

from app.chain import generate_design_brief
from app.config import settings
from app.logic import (
    assess_stone_by_name,
    get_stone_suitability_for_own_stone,
    resolve_stone_from_yss_reference,
    score_stones_by_color,
)
from app.models import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageUploadResponse,
    RingDesignResponse,
    RingSelectionPayload,
    StoneBranch,
    StoneSuitability,
)

_IMAGEN_MODEL      = "imagen-4.0-generate-001"       # text-to-image
_IMAGEN_REF_MODEL  = "gemini-2.5-flash-image"        # multimodal: image-in + image-out
_OUTPUT_SIZE       = (1080, 1080)                     # target HD resolution


def _upscale_to_hd(raw_bytes: bytes) -> bytes:
    """Upscale image bytes to _OUTPUT_SIZE using Lanczos (highest quality)."""
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    if img.size != _OUTPUT_SIZE:
        img = img.resize(_OUTPUT_SIZE, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()


UPLOADS_DIR = Path("uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/api", tags=["Ring Design"])


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
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    dest = UPLOADS_DIR / unique_name
    dest.write_bytes(contents)

    return ImageUploadResponse(
        image_url=f"/uploads/{unique_name}",
        filename=unique_name,
    )


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
        stone_assessment = get_stone_suitability_for_own_stone(
            stone_type=submission.own_stone.stone_type,
            jewelry_type=submission.jewelry_type,
            wear_frequency=submission.wear_frequency,
        )
        if not stone_assessment:
            raise HTTPException(
                status_code=404,
                detail=f"Stone '{submission.own_stone.stone_type}' not found in the suitability table.",
            )

    elif submission.stone_branch == StoneBranch.yss_sku:
        resolved = resolve_stone_from_yss_reference(submission.yss_reference)
        if not resolved:
            raise HTTPException(
                status_code=404,
                detail="Could not resolve the YSS reference to a catalogued stone.",
            )
        stone_assessment = assess_stone_by_name(
            stone_name=resolved,
            jewelry_type=submission.jewelry_type,
            wear_frequency=submission.wear_frequency,
        )
        if not stone_assessment:
            raise HTTPException(
                status_code=404,
                detail=f"Resolved stone '{resolved}' not found in the suitability table.",
            )

    elif submission.stone_branch == StoneBranch.help_choose:
        if submission.chosen_stone_name:
            stone_assessment = assess_stone_by_name(
                stone_name=submission.chosen_stone_name,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )
            if not stone_assessment:
                raise HTTPException(
                    status_code=404,
                    detail=f"Stone '{submission.chosen_stone_name}' not found in the suitability table.",
                )
        else:
            ranked = score_stones_by_color(
                color=submission.chosen_color,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )
            if not ranked:
                raise HTTPException(
                    status_code=404,
                    detail=f"No stones found for colour '{submission.chosen_color}'.",
                )
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
# Image generation via Gemini Imagen model
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
        # --- Image-guided generation via Gemini multimodal model ---
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
        # --- Text-to-image generation ---
        try:
            gen_response = await asyncio.to_thread(
                client.models.generate_images,
                model=_IMAGEN_MODEL,
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=1),
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Gemini Imagen error: {exc}")

        generated = gen_response.generated_images
        if not generated:
            raise HTTPException(status_code=502, detail="Gemini returned no images.")
        image_bytes = generated[0].image.image_bytes
        used_model = _IMAGEN_MODEL

    image_bytes = _upscale_to_hd(image_bytes)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    filename = f"{uuid.uuid4().hex}.png"
    (UPLOADS_DIR / filename).write_bytes(image_bytes)

    return ImageGenerateResponse(
        image_url=f"/uploads/{filename}",
        image_base64=image_b64,
        model=used_model,
        prompt=prompt,
    )
