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

    metal_detail = _METAL_FINISH.get(submission.metal.value, submission.metal.value) if submission.metal else "not specified"
    setting_detail = _SETTING_DETAIL.get(submission.setting.value, submission.setting.value) if submission.setting else "not specified"
    wear_detail = _WEAR_CONTEXT.get(submission.wear_frequency.value, submission.wear_frequency.value) if submission.wear_frequency else "not specified"
    direction_detail = _DIRECTION_DETAIL.get(submission.style_direction.value, submission.style_direction.value) if submission.style_direction else "not specified"
    direction_label = submission.style_direction.value if submission.style_direction else (submission.gender_type or "not specified")

    lines = [
        "=" * 60,
        "JEWELRY DESIGN BRIEF",
        "=" * 60,
        "",
        f"PIECE TYPE     : {jewelry}",
        f"STYLE FAMILY   : {submission.style_family or 'not specified'}",
        f"STYLE DIRECTION: {direction_label} — {direction_detail}",
    ]

    if submission.style:
        lines += [f"STYLE NOTES    : {submission.style}"]

    if submission.size_type:
        lines += [f"SIZE TYPE      : {submission.size_type}"]

    lines += [
        "",
        stone_block,
        f"METAL          : {submission.metal.value if submission.metal else 'not specified'} — {metal_detail}",
        f"SETTING        : {submission.setting.value if submission.setting else 'not specified'} — {setting_detail}",
        f"WEAR CONTEXT   : {submission.wear_frequency.value if submission.wear_frequency else 'not specified'} — {wear_detail}",
    ]

    if submission.final_preferences:
        lines += ["", f"CUSTOMER NOTES : {submission.final_preferences}"]

    if submission.additional_details:
        lines += ["", f"ADDITIONAL DETAILS : {submission.additional_details}"]

    if submission.additional_style:
        lines += ["", f"ADDITIONAL STYLE   : {submission.additional_style}"]

    if submission.inspiration_keywords:
        lines += ["", f"INSPIRATION KEYWORDS : {', '.join(submission.inspiration_keywords)}"]

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
        f"   Incorporate: {stone_summary} in {submission.metal.value if submission.metal else 'selected metal'}, {submission.style_family or 'custom'} style.",
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
You are a world-renowned luxury jewellery designer and an elite AI image-generation prompt engineer \
who specialises in hyper-detailed, cinematic jewellery photography prompts.

Read the design brief carefully and respond with JSON only — no prose outside the JSON.

The JSON must follow this exact schema:
{{
  "image_prompt": "<the full image generation prompt — see rules below>",
  "cautions": "<one concise stone care sentence if relevant, otherwise null>"
}}

Rules for image_prompt:
- Start with exactly: "Create an image of"
- Follow immediately with a rich, comma-separated list of descriptive tags, visual phrases, and \
  technical photography terms — NO full sentences, NO verbs like "featuring" or "crafted".
- You MUST include ALL of the following categories, in this order, with multiple descriptors each:

    1. JEWELLERY IDENTITY — piece type, style family name, occasion context
       e.g. "a vintage-inspired solitaire engagement ring, Art Deco style, heirloom quality"

    2. STONE — full gemstone name, precise colour with saturation (vivid / deep / pastel / icy),
       cut style (oval brilliant / cushion / round brilliant / pear / emerald cut, etc.),
       estimated carat weight, clarity appearance (eye-clean, slight inclusions, vivid saturation),
       light behaviour (strong dispersion, glassy luster, velvety depth, silk-like sheen),
       any optical phenomenon (chatoyancy, asterism, colour-shift, adularescence)

    3. METAL — karat and alloy, exact surface finish (high-polish mirror, satin, brushed, hammered,
       oxidised), warmth / coolness of tone, visible reflections, edge definition

    4. SETTING — precise construction detail: number of prongs and their shape, bezel wall height,
       pave density, micro-pave grain pattern, claw geometry, profile from the side, gallery design

    5. BAND / SHANK / CHAIN / WIRE — cross-section shape (comfort-fit round, flat, knife-edge,
       twisted, split-shank), tapering, thickness at shoulder vs back, any milgrain border,
       filigree, engraving, or surface pattern; for necklaces: chain style and link size

    6. ACCENT DETAILS — side stones, halo, pavé shoulders, hidden gallery diamonds, engraving
       motifs, cutout negative space, decorative gallery rails, scroll work

    7. STYLE MOOD & EMOTION — two to four evocative mood words plus visual metaphors
       e.g. "celestial, romantic, ethereal luminosity", "bold architectural geometry, confident glamour"

    8. SCALE & PROPORTION — overall ring diameter or pendant drop length, band width in mm,
       centre-stone face-up size relative to finger, weight feel (featherlight / substantial)

    9. LIGHTING — exact lighting setup with directionality: soft diffused studio octabox,
       dramatic raking side light, backlit glow through the stone, catch-light on prong tips,
       specular highlight on polished metal, subsurface scatter in gemstone, golden hour warmth

   10. BACKGROUND & SURFACE — specific background description with texture and colour:
       e.g. "pure white seamless studio sweep", "aged black velvet pad", "polished white Carrara
       marble surface", "deep navy satin ribbon", "frosted glass shelf floating mid-air"

   11. CAMERA & COMPOSITION — exact angle and focal detail: 45-degree hero three-quarter shot,
       top-down flat lay, side-profile macro, 90mm macro lens, shallow depth of field f/2.8,
       bokeh background, tack-sharp stone facets, perspective distortion-free

   12. POST-PROCESSING STYLE — colour grading mood: neutral editorial, warm luxury editorial,
       cool clean e-commerce, dramatic high-contrast fine-art

   13. TECHNICAL QUALITY TAGS — photorealistic, professional jewellery photography, 8K resolution,
       ultra-detailed, sharp focus, ray tracing, global illumination, HDR, award-winning commercial

- Minimum 120 comma-separated descriptors in total. Be obsessively specific — vague words like
  "beautiful" or "nice" are forbidden. Every descriptor must add concrete visual information.
- The finished prompt must read like a professional brief handed to a top-tier commercial
  jewellery photographer and a CGI rendering artist simultaneously.
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
        image_prompt=data["image_prompt"],
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
