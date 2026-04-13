from __future__ import annotations

import json
import re
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.models import DesignBrief, QuestionnaireSubmission, StoneSuitability, StoneBranch


# ---------------------------------------------------------------------------
# Step 1 — assemble the product prompt (shown in the UI text box)
# This is built deterministically from questionnaire answers — no LLM needed.
# The richer this is, the better the LLM output and image-gen prompt will be.
# ---------------------------------------------------------------------------

_METAL_FINISH = {
    "Yellow gold": "warm 18-karat yellow gold with a high-polish mirror finish",
    "White gold": "cool 18-karat white gold with a rhodium-plated mirror finish",
    "Rose gold": "blush 18-karat rose gold with a warm satin-to-mirror finish",
    "Platinum": "950-platinum with a cool, weighty, reflective finish",
}

_SETTING_DETAIL = {
    "Sharp Claw / Prong Set": (
        "sharp talon-style prong / claw setting — four or six pointed prongs that grip "
        "the stone tightly, maximising stone exposure and brilliance"
    ),
    "Rounded Claw / Prong Set": (
        "rounded claw / prong setting — soft rounded tips on four or six prongs, "
        "classic and elegant, stone fully visible from all angles"
    ),
    "Bezel Set": (
        "full bezel setting — a continuous metal collar wraps entirely around the "
        "girdle of the stone, smooth and flush, ultra-protective and modern"
    ),
    "Half Bezel / Partial Frame": (
        "half-bezel / partial frame setting — metal frames two opposing sides of "
        "the stone, leaving the east and west flanks open for a contemporary, "
        "architectural look"
    ),
    "Halo": (
        "halo setting — the centre stone is encircled by a tight pavé or micro-pavé "
        "halo of smaller accent diamonds or matching gemstones, amplifying perceived "
        "size and adding brilliance"
    ),
    "Hidden Halo": (
        "hidden halo setting — a pavé halo sits just below the crown of the centre "
        "stone, invisible from above but glittering from the side profile, giving a "
        "clean top view with a surprise detail"
    ),
}

_WEAR_CONTEXT = {
    "Every day": "designed for daily all-day wear — low profile, durable construction, no sharp edges",
    "Often, but carefully": "designed for frequent but mindful wear — moderate profile, elegant proportions",
    "Special occasions": "designed for special-occasion wear — elevated presence, expressive design, statement piece",
}

_DIRECTION_DETAIL = {
    "Masculine": "bold, strong, architectural lines — substantial weight and presence",
    "Balanced": "gender-neutral proportions — refined, versatile, neither heavy nor delicate",
    "Feminine": "delicate, graceful, softly curved forms — light and romantic",
}


def build_product_prompt(
    submission: QuestionnaireSubmission,
    stone_assessment: Optional[StoneSuitability],
) -> str:
    jewelry = (
        submission.jewelry_type_other
        if submission.jewelry_type.value == "Other" and submission.jewelry_type_other
        else submission.jewelry_type.value
    )

    # --- Stone block ---
    if submission.stone_branch == StoneBranch.already_have and submission.own_stone:
        s = submission.own_stone
        stone_block = (
            f"STONE (customer-supplied):\n"
            f"  Type     : {s.stone_type}\n"
            f"  Colour   : {s.color}\n"
            f"  Shape    : {s.shape}\n"
            f"  Size     : ~{s.approximate_size}\n"
        )
        stone_summary = f"{s.color} {s.stone_type} ({s.shape}, ~{s.approximate_size})"
    elif submission.stone_branch == StoneBranch.yss_sku and submission.yss_reference:
        stone_block = (
            f"STONE (from YSS catalogue):\n"
            f"  YSS Reference : {submission.yss_reference}\n"
        )
        if stone_assessment:
            stone_block += (
                f"  Resolved name : {stone_assessment.stone_name}\n"
                f"  Colour family : {', '.join(stone_assessment.color_families)}\n"
            )
            stone_summary = stone_assessment.stone_name
        else:
            stone_summary = f"YSS stone ({submission.yss_reference})"
    elif stone_assessment:
        stone_block = (
            f"STONE (recommended):\n"
            f"  Name          : {stone_assessment.stone_name}\n"
            f"  Colour family : {', '.join(stone_assessment.color_families)}\n"
            f"  Ring fit      : {stone_assessment.fit_label.value}\n"
            f"  Protection    : {stone_assessment.protection_level}\n"
            f"  Score         : {stone_assessment.score}\n"
        )
        stone_summary = stone_assessment.stone_name
    elif submission.chosen_color:
        stone_block = f"STONE: customer chose colour '{submission.chosen_color}' — best matching gemstone to be selected\n"
        stone_summary = f"{submission.chosen_color} gemstone"
    else:
        stone_block = "STONE: not specified\n"
        stone_summary = "gemstone"

    metal_detail = _METAL_FINISH.get(submission.metal.value, submission.metal.value)
    setting_detail = _SETTING_DETAIL.get(submission.setting.value, submission.setting.value)
    wear_detail = _WEAR_CONTEXT.get(submission.wear_frequency.value, submission.wear_frequency.value)
    direction_detail = _DIRECTION_DETAIL.get(submission.style_direction.value, submission.style_direction.value)

    lines = [
        "=" * 60,
        "JEWELRY DESIGN BRIEF",
        "=" * 60,
        "",
        f"PIECE TYPE     : {jewelry}",
        f"STYLE FAMILY   : {submission.style_family}",
        f"STYLE DIRECTION: {submission.style_direction.value} — {direction_detail}",
        "",
        stone_block,
        f"METAL          : {submission.metal.value} — {metal_detail}",
        f"SETTING        : {submission.setting.value} — {setting_detail}",
        f"WEAR CONTEXT   : {submission.wear_frequency.value} — {wear_detail}",
    ]

    if submission.final_preferences:
        lines += ["", f"CUSTOMER NOTES : {submission.final_preferences}"]

    if submission.inspiration_image_url:
        lines += ["", "INSPIRATION    : Customer has uploaded an inspiration image for visual reference."]

    lines += [
        "",
        "=" * 60,
        "TASK",
        "=" * 60,
        "",
        "Using every detail above, generate the following outputs:",
        "",
        "1. PRODUCT TITLE — luxurious, evocative, max 10 words.",
        "",
        "2. MARKETING DESCRIPTION — 2–3 compelling sentences for a luxury",
        "   jewellery e-commerce listing. Evoke emotion, occasion, and craft.",
        "",
        "3. VISUAL DESCRIPTION — an extremely detailed prompt for an AI image",
        "   generator (Stable Diffusion / Midjourney / DALL-E). This must include:",
        "   • Exact jewelry type and style family name",
        "   • Stone name, precise colour, shape/cut (e.g. oval, cushion, round brilliant),",
        "     approximate carat size, clarity appearance (eye-clean, vivid, included, etc.)",
        "   • Metal type, karat, and surface finish (high-polish, satin, brushed, etc.)",
        "   • Setting style described in physical detail",
        "   • Band / chain / earring wire style and proportions",
        "   • Overall dimensions and weight feel (delicate / substantial)",
        "   • Style direction expressed through specific visual language",
        "   • Lighting setup (e.g. soft diffused studio light, dramatic side lighting,",
        "     macro ring photography, jewellery photography style)",
        "   • Background (e.g. clean white, dark velvet, marble surface, floating)",
        "   • Camera angle and perspective (e.g. 45-degree hero shot, top-down, side profile)",
        "   • Any engraving, milgrain, filigree, or surface texture details",
        "   • Wear context mood (everyday elegance vs statement glamour)",
        f"   Incorporate: {stone_summary} in {submission.metal.value}, {submission.style_family} style.",
        "",
        "4. CUSTOMER LABEL — 3–5 word profile of the ideal wearer.",
        "",
        "5. CARE NOTE — one sentence stone care caution if relevant (else null).",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Step 2 — LLM prompt: takes the product_prompt and returns structured JSON
# ---------------------------------------------------------------------------

_SYSTEM = """\
You are a master luxury jewellery designer, gemologist, and AI image-generation \
prompt engineer with 20 years of experience at top-tier ateliers.

Your task is to read the structured design brief and produce five outputs. \
Respond with JSON only — absolutely no prose outside the JSON object.

The JSON must follow this exact schema:
{{
  "customer_label": "<3–5 word customer profile, e.g. 'Romantic Feminine Minimalist'>",
  "product_title": "<luxurious, evocative product title — max 10 words>",
  "marketing_description": "<2–3 sentence compelling luxury e-commerce description — \
evoke emotion, occasion, and craft>",
  "visual_description": "<comma-separated image generation prompt in Midjourney/Stable Diffusion style — \
NO full sentences, only descriptive tags and phrases separated by commas. \
Must include in this order: \
(1) subject — e.g. 'close-up of a solitaire engagement ring'; \
(2) stone — name, exact colour, cut, carat, clarity; \
(3) metal — karat, type, finish; \
(4) setting — physical prong/bezel detail; \
(5) band — shape, thickness, texture; \
(6) style mood — e.g. 'delicate feminine romantic', 'bold architectural masculine'; \
(7) lighting — e.g. 'soft diffused studio light', 'dramatic side lighting', 'macro ring photography'; \
(8) background — e.g. 'clean white background', 'dark velvet surface', 'floating on marble'; \
(9) camera — e.g. '45-degree hero angle', 'top-down view', 'side profile macro'; \
(10) quality tags — 'photorealistic', 'jewelry photography', '8K', 'ultra-detailed', 'sharp focus', 'ray tracing'>",
  "cautions": "<one concise stone care sentence if the stone warrants it, otherwise null>"
}}

Rules:
- visual_description must be comma-separated tags and short phrases ONLY — \
no full sentences, no verbs like "featuring" or "crafted", no narrative. \
Write it exactly like a Midjourney prompt. Minimum 80 comma-separated descriptors/phrases.
- Never use placeholder text. Every field must be filled with real, specific content \
drawn directly from the brief.
- Maintain a consistent luxury tone across all fields.
"""

_HUMAN = "{product_prompt}"

_prompt = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM),
    ("human", _HUMAN),
])


def _build_chain():
    llm = ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key,
        temperature=0.7,
    )
    return _prompt | llm | StrOutputParser()


def _parse_response(raw: str) -> DesignBrief:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    data = json.loads(cleaned)
    return DesignBrief(
        customer_label=data["customer_label"],
        product_title=data["product_title"],
        marketing_description=data["marketing_description"],
        visual_description=data["visual_description"],
        cautions=data.get("cautions"),
    )


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

async def generate_design_brief(
    submission: QuestionnaireSubmission,
    stone_assessment: Optional[StoneSuitability],
) -> DesignBrief:
    """
    1. Builds a rich, structured product prompt from questionnaire answers.
    2. Sends it to OpenAI — returns title, marketing copy, and a detailed
       visual_description ready to pass to an image-generation model.
    Raises ValueError if OPENAI_API_KEY is not configured.
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")

    product_prompt = build_product_prompt(submission, stone_assessment)
    chain = _build_chain()
    raw = await chain.ainvoke({"product_prompt": product_prompt})
    return _parse_response(raw)
