"""Questionnaire routes — image upload, ring selection, image generation."""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi import Request
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.repositories.design_repository import DesignRepository
from app.repositories.user_repository import UserRepository
from app.schemas.enums import StoneBranch
from app.schemas.questionnaire import RingSelectionPayload
from app.schemas.responses import (
    ImageGenerateResponse,
    ImageUploadResponse,
    RingDesignResponse,
)
from app.schemas.stone import StoneSuitability
from app.services import image_generation_service, upload_service
from app.services.llm_service import generate_design_brief, generate_design_summary
from app.services.stone_service import (
    assess_stone_by_name,
    get_stone_suitability_for_own_stone,
    resolve_stone_from_yss_reference,
    score_stones_by_color,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["Ring Design"])


# ---------------------------------------------------------------------------
# Image upload
# ---------------------------------------------------------------------------

@router.post(
    "/upload-image",
    response_model=ImageUploadResponse,
    summary="Upload an inspiration image",
)
async def upload_inspiration_image(
    file: UploadFile = File(...),
):
    """Validate, normalise and upload an inspiration image directly to S3 (≤ 10 MB).

    Accepts only the image file — no user or customer identifiers required.
    """
    return await upload_service.process_inspiration_upload(file)


# ---------------------------------------------------------------------------
# Ring selection submission
# ---------------------------------------------------------------------------

@router.post(
    "/ring-selection",
    response_model=RingDesignResponse,
    summary="Submit a ring design questionnaire",
)
async def submit_ring_selection(
    body: RingSelectionPayload,
    customer_id: str = Query(..., description="Customer ID from auth"),
    name: str = Query(..., description="Customer name from auth"),
    email: Optional[str] = Query(None, description="Customer email from auth"),
    db: Session = Depends(get_db),
    request: Request = None,
):
    user_repo = UserRepository(db)
    design_repo = DesignRepository(db)

    user = await asyncio.to_thread(user_repo.get_or_create, customer_id, name, email)

    submission = body.to_questionnaire_submission()
    stone_assessment = _assess_stone(submission)

    try:
        brief = await generate_design_brief(submission, stone_assessment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("LLM call failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM error: {exc}",
        ) from exc

    payload_dict = body.model_dump(exclude_none=True)
    # If the incoming payload didn't match the expected camelCase fields,
    # `body` may be empty. In that case, try to read the raw JSON and
    # persist it directly so we don't lose user-submitted data.
    if not payload_dict and request is not None:
        try:
            raw = await request.json()
            if isinstance(raw, dict):
                payload_dict = raw
        except Exception:
            # If reading raw JSON fails, leave payload_dict as empty dict
            pass
    headline = _build_summary(submission, stone_assessment)
    # If submission lacked parsed fields (caused headline to be generic),
    # fall back to deriving the headline from the raw payload dict.
    if (
        (not submission.style_family)
        and (not submission.metal)
        and (not submission.style_direction)
    ):
        headline = _build_summary_from_payload(payload_dict, stone_assessment)
    # Prefer a GPT-generated headline summary from the raw payload
    try:
        gpt_summary = await generate_design_summary(payload_dict)
        full_summary = gpt_summary
    except Exception:
        # Fallback to local summary builder
        payload_summary = _payload_summary(payload_dict)
        full_summary = f"{headline} — {payload_summary}" if payload_summary else headline

    design = await asyncio.to_thread(
        design_repo.create,
        user_id=user.id,
        design_payload=payload_dict,
        summary=full_summary,
        image_prompt=brief.image_prompt,
        cautions=brief.cautions,
        reference_image_path=submission.inspiration_image_url,
    )

    return RingDesignResponse(
        design_id=design.id,
        summary=full_summary,
        image_prompt=brief.image_prompt,
        cautions=brief.cautions,
    )


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

@router.post(
    "/generate-image",
    response_model=ImageGenerateResponse,
    summary="Generate an image from a prompt using Gemini Imagen",
)
async def generate_image(
    design_id: int = Query(..., description="Design ID to link the generated image to"),
    prompt: str = Form(..., description="Image generation prompt"),
    reference_url: Optional[str] = Form(
        None, description="Optional reference image URL — overrides the design's saved reference"
    ),
    db: Session = Depends(get_db),
):
    repo = DesignRepository(db)
    design = await asyncio.to_thread(repo.get, design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design with ID {design_id} not found.",
        )

    reference_bytes = await image_generation_service.resolve_reference_bytes(
        explicit_url=reference_url,
        design_reference_url=design.reference_image_path,
    )

    return await image_generation_service.generate_for_design(
        design_id=design_id,
        prompt=prompt,
        reference_bytes=reference_bytes,
        repo=repo,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _assess_stone(submission) -> Optional[StoneSuitability]:
    """Run the appropriate stone-suitability flow for the submission's branch."""
    if submission.stone_branch == StoneBranch.already_have:
        if submission.own_stone and submission.own_stone.stone_type:
            return get_stone_suitability_for_own_stone(
                stone_type=submission.own_stone.stone_type,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )
        return None

    if submission.stone_branch == StoneBranch.yss_sku and submission.yss_reference:
        resolved = resolve_stone_from_yss_reference(submission.yss_reference)
        if resolved:
            return assess_stone_by_name(
                stone_name=resolved,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )
        return None

    if submission.stone_branch == StoneBranch.help_choose:
        if submission.chosen_stone_name:
            return assess_stone_by_name(
                stone_name=submission.chosen_stone_name,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )
        if submission.chosen_color:
            ranked = score_stones_by_color(
                color=submission.chosen_color,
                jewelry_type=submission.jewelry_type,
                wear_frequency=submission.wear_frequency,
            )
            if ranked:
                return ranked[0]
    return None


def _build_summary(submission, assessment: Optional[StoneSuitability]) -> str:
    metal = submission.metal.value if submission.metal else "Mixed metal"
    style_family = submission.style_family or "Custom"
    direction = (
        submission.style_direction.value
        if submission.style_direction
        else (submission.gender_type or "Unspecified")
    )
    summary = f"Ring · {style_family} · {metal} · {direction}"
    if assessment:
        summary += f" · {assessment.stone_name} ({assessment.fit_label.value})"
    return summary


def _build_summary_from_payload(payload: dict, assessment: Optional[StoneSuitability]) -> str:
    """Build a headline summary from a raw payload dict (snake_case or camelCase).

    This is used when the Pydantic `submission` is empty because the incoming
    JSON used different key names. It looks for common keys in both cases.
    """
    def _get(*keys):
        for k in keys:
            v = payload.get(k)
            if v:
                return v
        return None

    style_family = _get("style_family", "ringStyleFamily", "style") or "Custom"
    metal = _get("metal", "metalType") or "Mixed metal"
    # style_direction may be stored as style_direction or gender_type
    direction = _get("style_direction", "styleDirection", "gender_type", "genderType") or "Unspecified"

    summary = f"Ring · {style_family} · {metal} · {direction}"

    # Stone info
    stone_name = _get("chosen_stone_name", "chosenStoneName", "gemType", "gem_type")
    fit_label = None
    if assessment:
        fit_label = assessment.fit_label.value if hasattr(assessment, "fit_label") else None

    if stone_name:
        summary += f" · {stone_name}"
        if fit_label:
            summary += f" ({fit_label})"

    return summary


_SUMMARY_FIELDS = (
    "jewelleryType",
    "genderType",
    "ringStyleFamily",
    "metalType",
    "prefersetting",
    "gemType",
    "stonecolor",
    "wearFrequency",
    "personalPreferences",
)


def _payload_summary(payload: dict) -> str:
    """Render a human-friendly bullet summary for dashboard display."""
    parts: list[str] = []
    for field in _SUMMARY_FIELDS:
        value = payload.get(field)
        if value:
            parts.append(str(value))
    return " • ".join(parts)
