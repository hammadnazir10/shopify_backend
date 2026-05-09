import asyncio
import io
import uuid
from pathlib import Path

from PIL import Image
import requests
from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Query
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
    ImageGenerateResponse,
    ImageUploadResponse,
    RingDesignResponse,
    RingSelectionPayload,
    StoneBranch,
    StoneSuitability,
)
from app.database import (
    get_or_create_user, 
    create_ring_design, 
    update_design_image,
    update_reference_image_path,
    get_design,
    generate_payload_summary,
)

_IMAGEN_MODEL      = "imagen-4.0-generate-001"          # text-to-image
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


def _reference_dir(user_id: int) -> Path:
    return Path(settings.temp_folder) / f"user_{user_id}"


def _next_reference_filename(user_id: int) -> str:
    user_temp_dir = _reference_dir(user_id)
    existing_indexes = []
    for existing_file in user_temp_dir.glob("reference_*.png"):
        try:
            existing_indexes.append(int(existing_file.stem.split("_")[-1]))
        except ValueError:
            continue
    next_index = max(existing_indexes, default=0) + 1
    return f"reference_{next_index}.png"


def _latest_reference_file(user_id: int) -> Path | None:
    user_temp_dir = _reference_dir(user_id)
    candidates = []
    for existing_file in user_temp_dir.glob("reference_*.png"):
        try:
            index = int(existing_file.stem.split("_")[-1])
        except ValueError:
            continue
        candidates.append((index, existing_file))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


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
async def upload_inspiration_image(
    file: UploadFile = File(...),
    user_id: int = Query(..., description="User ID"),
):
    """
    Accepts a JPG / PNG / WebP / GIF (max 10 MB).
    Saves to a numbered user-scoped temp folder and uploads to S3.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {sorted(ALLOWED_TYPES)}",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB limit.")

    # Create temp folder structure: temp/user_{user_id}/
    user_temp_dir = _reference_dir(user_id)
    user_temp_dir.mkdir(parents=True, exist_ok=True)

    filename = _next_reference_filename(user_id)
    file_path = user_temp_dir / filename

    # Normalize the uploaded image to PNG so generation always reads the same path.
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    image.save(file_path, format="PNG")

    s3_key = f"references/user_{user_id}/{filename}"
    image_url = await asyncio.to_thread(s3_upload, s3_key, file_path.read_bytes(), "image/png")

    return ImageUploadResponse(
        image_url=image_url,
        filename=filename,
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
        "prompt ready for image generation. "
        "Automatically stores customer information in database on first submission."
    ),
)
async def submit_ring_selection(
    body: RingSelectionPayload,
    customer_id: str = Query(..., description="Customer ID from auth"),
    name: str = Query(..., description="Customer name from auth"),
    email: str = Query(None, description="Customer email from auth"),
):
    # Get or create user
    user = await asyncio.to_thread(get_or_create_user, customer_id, name, email)
    
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
    
    # Generate detailed payload summary for dashboard
    payload_summary = generate_payload_summary(body.model_dump(mode="json", exclude_none=True))

    # Store design in database
    design = await asyncio.to_thread(
        create_ring_design,
        user_id=user.id,
        design_payload=body.model_dump(mode="json", exclude_none=True),
        summary=f"{summary} — {payload_summary}",
        image_prompt=brief.image_prompt,
        cautions=brief.cautions,
    )

    return RingDesignResponse(
        design_id=design.id,
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
        "Accepts a prompt (required) and design_id to link the image. "
        "Uses the stored user reference image when available, otherwise falls back to prompt-only generation. "
        "Without an image: pure text-to-image generation. "
        "With an image: uses it as a visual reference to guide generation. "
        "Saves generated image to temp/generated/design_{design_id}.png and S3."
    ),
)
async def generate_image(
    design_id: int = Query(..., description="Design ID to link the generated image to"),
    prompt: str = Form(..., description="Image generation prompt"),
    reference_url: str | None = Form(None, description="Optional reference image URL to use for generation"),
):
    if not settings.gemini_api:
        raise HTTPException(
            status_code=503,
            detail="Gemini_API key is not configured. Add it to your .env file.",
        )

    # Verify design exists
    design = await asyncio.to_thread(get_design, design_id)
    if not design:
        raise HTTPException(status_code=404, detail=f"Design with ID {design_id} not found.")

    client = genai.Client(api_key=settings.gemini_api)

    # Determine reference bytes and URL to use (priority: provided reference_url, latest user upload, None)
    reference_bytes = None
    used_reference_url = None

    if reference_url:
        # Try to fetch the provided URL
        try:
            resp = await asyncio.to_thread(requests.get, reference_url, timeout=10)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch reference URL: {reference_url}")
            reference_bytes = resp.content
            used_reference_url = reference_url
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Error fetching reference URL: {exc}")

    if reference_bytes is None:
        # Try latest user-uploaded local reference file
        reference_path = _latest_reference_file(design.user_id)
        if reference_path is not None:
            reference_bytes = await asyncio.to_thread(reference_path.read_bytes)
            # ensure reference is available on S3 and record that URL
            s3_key = f"references/user_{design.user_id}/{reference_path.name}"
            used_reference_url = await asyncio.to_thread(s3_upload, s3_key, reference_bytes, "image/png")
            await asyncio.to_thread(update_reference_image_path, design_id, used_reference_url)

    if reference_bytes is not None:
        # Use image-in + prompt model
        try:
            gen_response = await asyncio.to_thread(
                client.models.generate_content,
                model=_IMAGEN_REF_MODEL,
                contents=[
                    types.Content(parts=[
                        types.Part(text=f"Using the provided image as a visual reference, generate a new ring image based on this description: {prompt}"),
                        types.Part(inline_data=types.Blob(mime_type="image/png", data=reference_bytes)),
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
    else:
        # Fallback to prompt-only image generation
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

    image_bytes = _upscale_to_hd(image_bytes)
    
    # Save to local generated folder: temp/generated/user_{user_id}/design_{design_id}.png
    generated_dir = Path(settings.temp_folder) / "generated" / f"user_{design.user_id}"
    generated_dir.mkdir(parents=True, exist_ok=True)
    local_path = generated_dir / f"design_{design_id}.png"
    
    with open(local_path, "wb") as f:
        f.write(image_bytes)
    
    # Also upload to S3
    filename = f"generated/{uuid.uuid4().hex}.png"
    image_url = await asyncio.to_thread(s3_upload, filename, image_bytes, "image/png")

    # Update design with generated image URL and local path
    await asyncio.to_thread(update_design_image, design_id, image_url)

    return ImageGenerateResponse(
        image_url=image_url,
        prompt=prompt,
    )
