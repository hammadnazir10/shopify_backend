"""Convert a questionnaire submission into a structured design brief
ready to be sent to the LLM as the human message."""

from __future__ import annotations

import re
from typing import List, Optional

from app.prompts.descriptors import (
    DIRECTION_DETAIL,
    KEYWORD_VISUAL,
    METAL_FINISH,
    PHOTOGRAPHY_REQUIREMENTS,
    SETTING_DETAIL,
    STONE_COLOR_VISUAL,
    STONE_VISUAL,
    STYLE_FAMILY_VISUAL,
    WEAR_CONTEXT,
)
from app.schemas.enums import StoneBranch
from app.schemas.questionnaire import QuestionnaireSubmission
from app.schemas.stone import StoneSuitability

_DIVIDER = "=" * 64
_INSPIRATION_TAIL_RE = re.compile(r"\n*inspiration keywords\s*:.*$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_inspiration_tail(text: str) -> str:
    """Remove the trailing 'Inspiration Keywords: ...' segment that the frontend appends."""
    return _INSPIRATION_TAIL_RE.sub("", text).strip()


def _keyword_visuals(keywords: List[str]) -> str:
    """Translate inspiration keywords into visual directives the LLM can render."""
    out: List[str] = []
    for kw in keywords:
        key = kw.lower().replace(" ", "_").replace("-", "_")
        directive = KEYWORD_VISUAL.get(key)
        out.append(f"{kw} → {directive}" if directive else kw)
    return "; ".join(out)


def _resolve_jewelry_label(submission: QuestionnaireSubmission) -> str:
    if submission.jewelry_type.value == "Other" and submission.jewelry_type_other:
        return submission.jewelry_type_other
    return submission.jewelry_type.value


# ---------------------------------------------------------------------------
# Stone block
# ---------------------------------------------------------------------------

def _stone_block_for_own_stone(submission: QuestionnaireSubmission) -> tuple[str, str]:
    s = submission.own_stone
    stone_name = s.stone_type or "gemstone"
    stone_visual = STONE_VISUAL.get((stone_name or "").lower(), "")
    color_visual = STONE_COLOR_VISUAL.get((s.color or "").lower(), s.color or "")

    lines = [
        "STONE (customer-supplied):",
        f"  Type        : {stone_name}",
        f"  Colour      : {s.color or 'not specified'}"
        + (f" — {color_visual}" if color_visual and s.color else ""),
        f"  Shape / Cut : {s.shape or 'not specified'}",
        f"  Approx size : {s.approximate_size or 'not specified'}",
    ]
    if stone_visual:
        lines.append(f"  Visual notes: {stone_visual}")

    color_part = f"{s.color} " if s.color else ""
    shape_part = f", {s.shape} cut" if s.shape else ""
    size_part = f", ~{s.approximate_size}" if s.approximate_size else ""
    summary = f"{color_part}{stone_name}{shape_part}{size_part}"

    return "\n".join(lines), summary


def _stone_block_for_yss(
    submission: QuestionnaireSubmission, assessment: Optional[StoneSuitability]
) -> tuple[str, str]:
    stone_name = assessment.stone_name if assessment else "gemstone"
    stone_visual = STONE_VISUAL.get(stone_name.lower(), "")

    lines = [
        "STONE (from YSS catalogue):",
        f"  YSS Reference : {submission.yss_reference}",
    ]
    if assessment:
        lines += [
            f"  Stone name    : {assessment.stone_name}",
            f"  Colour family : {', '.join(assessment.color_families)}",
            f"  Ring fit      : {assessment.fit_label.value}",
        ]
    if stone_visual:
        lines.append(f"  Visual notes  : {stone_visual}")

    return "\n".join(lines), stone_name


def _stone_block_for_assessment(
    submission: QuestionnaireSubmission, assessment: StoneSuitability
) -> tuple[str, str]:
    stone_name = assessment.stone_name
    stone_visual = STONE_VISUAL.get(stone_name.lower(), "")
    color_families = assessment.color_families

    chosen_color_key = (submission.chosen_color or "").lower()
    color_visual = STONE_COLOR_VISUAL.get(chosen_color_key, "")
    if not color_visual and color_families:
        color_visual = STONE_COLOR_VISUAL.get(
            color_families[0].lower(), color_families[0]
        )

    displayed_color = submission.chosen_color or (color_families[0] if color_families else "")

    lines = [
        "STONE (selected based on customer preferences):",
        f"  Name          : {stone_name}",
        f"  Colour        : {displayed_color}"
        + (f" — {color_visual}" if color_visual else ""),
        f"  Colour family : {', '.join(color_families)}",
        f"  Ring fit      : {assessment.fit_label.value}",
        f"  Durability    : {assessment.protection_level} protection required",
    ]
    if stone_visual:
        lines.append(f"  Visual notes  : {stone_visual}")

    summary = f"{displayed_color} {stone_name}".strip() if displayed_color else stone_name
    return "\n".join(lines), summary


def _stone_block_for_color_only(submission: QuestionnaireSubmission) -> tuple[str, str]:
    color_visual = STONE_COLOR_VISUAL.get(submission.chosen_color.lower(), "")
    lines = [
        "STONE:",
        f"  Customer colour preference : {submission.chosen_color}"
        + (f" — {color_visual}" if color_visual else ""),
        "  Select the best matching gemstone for this colour.",
    ]
    return "\n".join(lines), f"{submission.chosen_color} gemstone"


def _build_stone_block(
    submission: QuestionnaireSubmission, assessment: Optional[StoneSuitability]
) -> tuple[str, str]:
    if submission.stone_branch == StoneBranch.already_have and submission.own_stone:
        return _stone_block_for_own_stone(submission)
    if submission.stone_branch == StoneBranch.yss_sku and submission.yss_reference:
        return _stone_block_for_yss(submission, assessment)
    if assessment:
        return _stone_block_for_assessment(submission, assessment)
    if submission.chosen_color:
        return _stone_block_for_color_only(submission)
    return "STONE: not specified — select an appropriate gemstone.", "gemstone"


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------

def build_product_prompt(
    submission: QuestionnaireSubmission,
    stone_assessment: Optional[StoneSuitability],
) -> str:
    """Return a fully-structured design brief string for the LLM."""

    jewelry_label = _resolve_jewelry_label(submission)
    style_family_label = submission.style_family or "not specified"
    style_family_visual = STYLE_FAMILY_VISUAL.get(style_family_label, "")

    metal_val = submission.metal.value if submission.metal else None
    setting_val = submission.setting.value if submission.setting else None
    wear_val = submission.wear_frequency.value if submission.wear_frequency else None
    direction_val = submission.style_direction.value if submission.style_direction else None

    metal_detail = METAL_FINISH.get(metal_val, metal_val or "not specified")
    setting_detail = SETTING_DETAIL.get(setting_val, setting_val or "not specified")
    wear_detail = WEAR_CONTEXT.get(wear_val, wear_val or "not specified")
    direction_detail = DIRECTION_DETAIL.get(direction_val, direction_val or "not specified")
    direction_label = direction_val or submission.gender_type or "not specified"

    stone_block, stone_summary = _build_stone_block(submission, stone_assessment)

    # ------------------------------------------------------------------
    # Assemble brief
    # ------------------------------------------------------------------
    lines: List[str] = [
        _DIVIDER,
        "JEWELLERY DESIGN BRIEF",
        _DIVIDER,
        "",
        f"PIECE TYPE       : {jewelry_label}",
        f"STYLE FAMILY     : {style_family_label}",
    ]
    if style_family_visual:
        lines.append(f"  Visual design  : {style_family_visual}")

    lines.append(f"STYLE DIRECTION  : {direction_label} — {direction_detail}")

    if submission.style:
        lines.append(f"STYLE NOTES      : {submission.style}")
    if submission.size_type:
        lines.append(f"RING SIZE TYPE   : {submission.size_type}")

    lines += [
        "",
        stone_block.rstrip(),
        "",
        f"METAL            : {metal_val or 'not specified'} — {metal_detail}",
        f"SETTING          : {setting_val or 'not specified'} — {setting_detail}",
        f"WEAR CONTEXT     : {wear_val or 'not specified'} — {wear_detail}",
    ]

    if submission.final_preferences:
        lines += ["", f"CUSTOMER NOTES   : {submission.final_preferences}"]

    if submission.additional_details:
        cleaned = _strip_inspiration_tail(submission.additional_details)
        if cleaned:
            lines += ["", f"ADDITIONAL NOTES : {cleaned}"]

    if submission.additional_style:
        lines += ["", f"STYLE NOTES (extra) : {submission.additional_style}"]

    if submission.inspiration_keywords:
        directives = _keyword_visuals(submission.inspiration_keywords)
        lines += [
            "",
            f"INSPIRATION KEYWORDS : {', '.join(submission.inspiration_keywords)}",
            f"VISUAL DIRECTIVES    : {directives}",
            "→ These keywords MUST be reflected in the setting texture, band detail, and mood language of the image prompt.",
        ]

    if submission.inspiration_image_url:
        lines += [
            "",
            "REFERENCE IMAGE  : Customer has uploaded an inspiration image. Match its overall visual mood and aesthetic closely.",
        ]

    # ------------------------------------------------------------------
    # Photography requirements per piece type
    # ------------------------------------------------------------------
    jewelry_type_val = submission.jewelry_type.value
    photo_reqs = PHOTOGRAPHY_REQUIREMENTS.get(jewelry_type_val)
    if photo_reqs:
        lines += [
            "",
            f"{jewelry_type_val.upper()} PHOTOGRAPHY REQUIREMENTS (MANDATORY):",
            *(f"  - {item}" for item in photo_reqs),
        ]

    # ------------------------------------------------------------------
    # Task instructions
    # ------------------------------------------------------------------
    piece_description = (
        f"{stone_summary} set in {metal_val or 'the specified metal'}, "
        f"{style_family_label} style {jewelry_label.lower()}."
    )
    critical_note = (
        f"   CRITICAL: Follow the {jewelry_type_val.upper()} PHOTOGRAPHY REQUIREMENTS above exactly."
        if photo_reqs
        else ""
    )
    lines += [
        "",
        _DIVIDER,
        "YOUR TASK",
        _DIVIDER,
        "",
        "Generate a single JSON object with two keys:",
        "",
        '1. "image_prompt"',
        f"   Create an extremely detailed image generation prompt for: {piece_description}",
        "   The prompt must visually render ALL design details from this brief.",
        "   Apply every VISUAL DIRECTIVE from the inspiration keywords above.",
        *([critical_note] if critical_note else []),
        "   Follow ALL rules in the system prompt exactly.",
        "",
        '2. "cautions"',
        "   One sentence of stone care advice if the stone requires special handling, otherwise null.",
    ]

    return "\n".join(lines)
