"""Questionnaire routes — image upload, ring selection, image generation."""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.repositories import DesignRepository, UserRepository
from app.schemas import (
    ImageGenerateResponse,
    ImageUploadResponse,
    RingDesignResponse,
    RingSelectionPayload,
    StoneBranch,
    StoneSuitability,
)
from app.services import image_generation_service, upload_service
from app.services.llm_service import generate_design_brief
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
    user_id: int = Query(..., description="User ID"),
):
    """Validate, normalise and persist an inspiration image (≤ 10 MB)."""
    return await upload_service.process_inspiration_upload(user_id, file)


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
    except Exception as exc:  # surface as bad-gateway from the LLM
        logger.exception("LLM call failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM error: {exc}",
        ) from exc

    summary = _build_summary(submission, stone_assessment)

    design = await asyncio.to_thread(
        design_repo.create,
        user_id=user.id,
        design_payload=body.model_dump(mode="json", exclude_none=True),
        summary=summary,
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
    reference_url: Optional[str] = Form(None, description="Optional reference image URL"),
    db: Session = Depends(get_db),
):
    repo = DesignRepository(db)
    design = await asyncio.to_thread(repo.get, design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design with ID {design_id} not found.",
        )

    reference_bytes, _ = await image_generation_service.resolve_reference(
        design_user_id=design.user_id,
        design_id=design_id,
        repo=repo,
        reference_url=reference_url,
    )

    return await image_generation_service.generate_for_design(
        design_id=design_id,
        user_id=design.user_id,
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
