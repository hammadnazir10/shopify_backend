import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.chain import generate_design_brief
from app.logic import (
    assess_stone_by_name,
    get_stone_suitability_for_own_stone,
    resolve_stone_from_yss_reference,
    score_stones_by_color,
)
from app.models import (
    ImageUploadResponse,
    RingDesignResponse,
    RingSelectionPayload,
    StoneBranch,
    StoneSuitability,
)

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
        f"Ring · {submission.style_family} · {submission.metal.value} · "
        f"{submission.style_direction.value}"
    )
    if stone_assessment:
        summary += f" · {stone_assessment.stone_name} ({stone_assessment.fit_label.value})"

    return RingDesignResponse(
        summary=summary,
        image_prompt=brief.image_prompt,
        cautions=brief.cautions,
    )
