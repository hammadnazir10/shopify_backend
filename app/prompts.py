from __future__ import annotations

import re
from typing import Optional

from app.models import QuestionnaireSubmission, StoneSuitability, StoneBranch


# ---------------------------------------------------------------------------
# Metal — visual descriptions
# ---------------------------------------------------------------------------

_METAL_FINISH = {
    "Yellow gold": "warm 18-karat yellow gold, high-polish mirror finish, deep amber-gold reflections, classic warm tone",
    "White gold":  "cool 18-karat white gold, rhodium-plated mirror finish, icy silver-white surface, sharp edge definition",
    "Rose gold":   "blush 18-karat rose gold, warm satin-to-mirror finish, soft copper-pink hue, romantic warm reflections",
    "Platinum":    "950-platinum, cool weighty reflective finish, bright silver-white tone, dense and lustrous surface",
}


# ---------------------------------------------------------------------------
# Setting — physical construction descriptions
# ---------------------------------------------------------------------------

_SETTING_DETAIL = {
    "Sharp Claw / Prong Set": (
        "sharp talon-style prong setting, four or six pointed steel-like claws gripping the girdle, "
        "maximum stone exposure, dramatic claw shadows, brilliant light entry from all angles"
    ),
    "Rounded Claw / Prong Set": (
        "rounded claw prong setting, soft dome-tipped four or six prongs, classic elegant grip, "
        "stone fully visible from crown to girdle, smooth claw edges catching light gently"
    ),
    "Bezel Set": (
        "full bezel setting, continuous metal collar wrapped flush around the stone girdle, "
        "smooth seamless metal wall, ultra-modern and protective, clean geometric profile"
    ),
    "Half Bezel / Partial Frame": (
        "half-bezel partial frame setting, metal frames two opposing sides of the stone, "
        "east and west flanks open to light, contemporary architectural look, floating stone effect"
    ),
    "Halo": (
        "halo setting, tight micro-pavé ring of accent stones circling the centre stone, "
        "amplified perceived size, extra brilliance from surrounding diamonds, glittering frame effect"
    ),
    "Hidden Halo": (
        "hidden halo setting, pavé accent ring tucked just below the crown out of top view, "
        "clean minimalist top profile, surprise glitter revealed from side angle, dual-look design"
    ),
}


# ---------------------------------------------------------------------------
# Wear context
# ---------------------------------------------------------------------------

_WEAR_CONTEXT = {
    "Every day": "daily all-day wear, low-profile slim build, durable construction, no sharp snag points, practical elegance",
    "Often, but carefully": "frequent mindful wear, moderate profile, elegant proportions balanced with wearability",
    "Special occasions": "special-occasion statement piece, elevated presence, expressive design, maximum visual impact",
}


# ---------------------------------------------------------------------------
# Style direction
# ---------------------------------------------------------------------------

_DIRECTION_DETAIL = {
    "Masculine": "bold strong architectural lines, substantial weight and band width, confident commanding presence",
    "Balanced":  "gender-neutral refined proportions, versatile neither heavy nor delicate, clean universal elegance",
    "Feminine":  "delicate graceful softly curved forms, featherlight romantic silhouette, intricate fine detail",
}


# ---------------------------------------------------------------------------
# Style family — visual design language per family
# ---------------------------------------------------------------------------

_STYLE_FAMILY_VISUAL = {
    "Solitaire": (
        "single-stone solitaire design, uninterrupted tapered band, all attention on centre stone, "
        "minimalist elegant profile, timeless clean lines, stone elevated on a slim shank"
    ),
    "Three Stone": (
        "three-stone trilogy design, flanking side stones graduated in size, "
        "balanced symmetrical composition, past-present-future symbolism, trio of glittering focal points"
    ),
    "Halo": (
        "halo design, centre stone surrounded by micro-pavé accent ring, "
        "enhanced perceived size, brilliant light cascade, layered glittering composition"
    ),
    "Bezel": (
        "bezel-set design, metal collar encasing the stone flush, smooth geometric outline, "
        "modern architectural aesthetic, clean protective band"
    ),
    "Signet": (
        "signet ring design, wide flat-top table face, substantial band width, "
        "bold heraldic presence, engraving-ready surface, strong sculptural silhouette"
    ),
    "Cluster": (
        "cluster design, multiple smaller stones arranged to mimic a single large stone, "
        "mosaic of glittering facets, vintage garden-party aesthetic, dense sparkling surface"
    ),
    "Toi et Moi": (
        "toi et moi two-stone design, two distinct stones side by side on a split fork shank, "
        "romantic duality, asymmetric or mirrored composition, intimate symbolic pairing"
    ),
    "Eternity": (
        "full eternity band design, stones set continuously all the way around the band, "
        "unbroken circle of gemstones, infinite loop symbolism, uniform pavé or prong row, "
        "seamless glittering circumference, low-profile stackable band"
    ),
    "Vintage-Inspired": (
        "vintage-inspired design, intricate milgrain border edging, filigree scrollwork gallery, "
        "Art Deco or Edwardian detailing, hand-engraved surface texture, antique romantic character, "
        "ornate craftsmanship referencing early 20th century jewellery"
    ),
    "Contemporary Minimal": (
        "contemporary minimal design, clean geometric lines, deliberate negative space, "
        "architectural simplicity, no superfluous decoration, sculptural modern form"
    ),
}


# ---------------------------------------------------------------------------
# Stone visual profiles — per stone type
# ---------------------------------------------------------------------------

_STONE_VISUAL = {
    "diamond": (
        "colourless to near-colourless diamond, brilliant-cut faceting, "
        "exceptional fire and dispersion, rainbow spectral flashes, "
        "eye-clean clarity, adamantine luster, scintillating brilliance"
    ),
    "sapphire": (
        "sapphire gemstone, vitreous glassy luster, strong saturation, "
        "silk-like needle inclusions giving velvety depth, excellent transparency, "
        "sharp facet reflections, no optical phenomena unless star-cut"
    ),
    "ruby": (
        "ruby gemstone, intense red with fluorescent glow under sunlight, "
        "vitreous luster, strong chromatic saturation, deep colour zoning, "
        "velvety silk needle inclusions, highly valued brilliance"
    ),
    "emerald": (
        "emerald gemstone, rich verdant green, characteristic jardin inclusions giving depth, "
        "vitreous to resinous luster, slightly waxy surface quality, "
        "step-cut faceting typical, garden-like inner landscape"
    ),
    "morganite": (
        "morganite gemstone, soft peachy-pink to blush tone, excellent transparency, "
        "vitreous luster, gentle pastel saturation, warm feminine hue, "
        "typically cushion or oval cut to maximise colour"
    ),
    "aquamarine": (
        "aquamarine gemstone, clear sky-blue to sea-blue tone, excellent transparency, "
        "vitreous glassy luster, clean eye-clear clarity, "
        "cool refreshing hue, typically emerald or oval cut"
    ),
    "tanzanite": (
        "tanzanite gemstone, vivid blue-violet to deep purple-blue, "
        "strong pleochroism showing blue, violet and burgundy at different angles, "
        "vitreous luster, rich colour depth"
    ),
    "opal": (
        "opal gemstone, vivid play-of-colour with rainbow spectral flash, "
        "waxy to vitreous luster, unique shifting colour patterns, "
        "dynamic colour-shift phenomenon visible across the surface"
    ),
    "pearl": (
        "pearl, smooth creamy surface, orient luster with pearlescent iridescence, "
        "warm white to ivory to pink overtone, classic organic gem, "
        "soft diffused light interaction, smooth tactile surface"
    ),
    "tourmaline": (
        "tourmaline gemstone, broad colour range, strong vitreous luster, "
        "excellent transparency, rich colour saturation, "
        "sometimes bicolour or watermelon effect"
    ),
    "garnet": (
        "garnet gemstone, deep rich colour, high refractive index giving strong brilliance, "
        "vitreous to adamantine luster, excellent colour depth, "
        "typically round or cushion cut"
    ),
    "amethyst": (
        "amethyst gemstone, rich purple to violet tone, excellent transparency, "
        "vitreous luster, strong colour saturation, "
        "typical faceted oval or cushion cut"
    ),
    "moonstone": (
        "moonstone gemstone, adularescence phenomenon — blue-white floating inner glow, "
        "translucent to semi-transparent body, soft milky-white base tone, "
        "ethereal floating light effect shifting with viewing angle"
    ),
    "alexandrite": (
        "alexandrite gemstone, dramatic colour-shift from green in daylight to red-purple under incandescent light, "
        "strong pleochroism, vitreous luster, exceptional colour-change phenomenon"
    ),
    "spinel": (
        "spinel gemstone, vivid saturated colour, strong vitreous luster, "
        "excellent transparency and brilliance, no optical phenomena, pure clean hue"
    ),
    "topaz": (
        "topaz gemstone, excellent transparency, vitreous luster, "
        "clean eye-clear clarity, strong colour saturation depending on variety, "
        "typically brilliant or step cut"
    ),
    "citrine": (
        "citrine gemstone, warm golden-yellow to orange-brown tone, "
        "excellent transparency, vitreous luster, cheerful warm colour, "
        "typically faceted oval or cushion cut"
    ),
    "peridot": (
        "peridot gemstone, distinctive lime-green to olive-green tone, "
        "vitreous luster, slight oily appearance, characteristic yellowish-green hue"
    ),
    "zircon": (
        "zircon gemstone, exceptionally high refractive index giving diamond-like fire, "
        "strong dispersion and brilliance, vitreous to adamantine luster, "
        "sharp facet contrast"
    ),
    "tsavorite": (
        "tsavorite garnet gemstone, intense vivid emerald-green, "
        "high refractive index giving exceptional brilliance, "
        "strong clean colour with no jardin inclusions unlike emerald"
    ),
}


# ---------------------------------------------------------------------------
# Stone colour — visual colour descriptors
# ---------------------------------------------------------------------------

_STONE_COLOR_VISUAL = {
    "pink":      "soft blush-pink to vivid hot-pink saturation, romantic feminine hue, warm peachy-pink undertone",
    "blue":      "cornflower-blue to deep royal-blue, cool vivid saturation, icy clarity",
    "red":       "deep crimson to vivid blood-red, intense saturated red, fiery warm hue",
    "green":     "rich forest-green to vivid emerald-green, cool deep saturation, lush verdant tone",
    "purple":    "deep violet to vivid plum-purple, rich cool saturation, regal hue",
    "yellow":    "warm golden-yellow to vivid canary-yellow, bright sunny saturation",
    "orange":    "warm burnt-orange to vivid mandarin-orange, rich earthy saturation",
    "clear":     "near-colourless to completely transparent, crystal-clear body, white-light brilliance",
    "black":     "deep opaque black, high-polish surface, dramatic light absorption, bold contrast",
    "white":     "milky white to soft ivory tone, translucent glow, pearl-like luminosity",
    "multicolor": "multicolour play-of-colour, shifting spectral hues, dynamic colour movement",
    "gray":      "cool silver-gray tone, subtle neutral saturation, sophisticated muted hue",
    "brown":     "warm cognac to earthy brown tone, rich organic saturation",
}


# ---------------------------------------------------------------------------
# Inspiration keywords → visual design directives
# ---------------------------------------------------------------------------

_KEYWORD_VISUAL = {
    "minimal":        "clean uncluttered composition, deliberate negative space, no superfluous ornament, refined restraint",
    "minimalist":     "clean uncluttered composition, deliberate negative space, no superfluous ornament, refined restraint",
    "vintage":        "antique patina feel, milgrain bead edging, filigree scrollwork, Art Deco angular geometry or Edwardian florets",
    "vintage_feel":   "subtle antique character, delicate milgrain border, softly ornate gallery detail, heirloom quality craftsmanship",
    "romantic":       "soft curved lines, floral motif accents, dreamy feminine silhouette, warm intimate mood",
    "bold":           "substantial band width, dramatic stone presence, strong visual weight, high-contrast composition",
    "modern":         "geometric angular lines, architectural negative space, contemporary sculptural form",
    "classic":        "timeless proportions, traditional four-prong solitaire silhouette, enduring elegant design",
    "luxury":         "ultra-fine pavé grain, polished mirror surfaces, impeccable craftsmanship, premium material finish",
    "delicate":       "fine slim band, featherlight proportions, intricate fine detail, graceful narrow profile",
    "nature":         "organic flowing curves, leaf or floral motif, botanical sculptural form, nature-inspired silhouette",
    "geometric":      "angular precise faceting, sharp edge definition, mathematical symmetry, hard-line architectural form",
    "celestial":      "star and crescent motifs, ethereal cosmic feel, scattered pavé like a night sky, dreamy otherworldly mood",
    "edgy":           "asymmetric composition, unconventional angular form, dark dramatic mood, avant-garde silhouette",
    "bohemian":       "organic free-form design, earthy tone palette, textured hammered metal surface, handcrafted artisanal feel",
    "art_deco":       "geometric Art Deco symmetry, stepped baguette accent stones, platinum-era architectural precision, 1920s glamour",
    "floral":         "floral petal-shaped prongs, botanical scrollwork gallery, flower-head cluster composition, garden-party aesthetic",
}


# ---------------------------------------------------------------------------
# LLM system prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a world-class luxury jewellery designer and a professional AI image-generation prompt engineer \
specialising in hyper-detailed cinematic jewellery photography.

Read the design brief carefully. Respond with valid JSON only — absolutely no prose or markdown outside the JSON.

Required JSON schema:
{{
  "image_prompt": "<full image generation prompt following all rules below>",
  "cautions": "<one concise stone care sentence if the stone needs special handling, otherwise null>"
}}

=== RULES FOR image_prompt ===

Start with exactly: "Create an image of"

Then follow with a long comma-separated sequence of visual descriptors, tags, and photography terms.
NO full sentences. NO verbs like "featuring", "showcasing", or "crafted with".
Every descriptor must add concrete visual information — words like "beautiful" or "nice" are forbidden.

MANDATORY SECTIONS (include all, in this order):

1. JEWELLERY IDENTITY
   Piece type, style family name, design era/occasion, wearing context
   Example: "a full eternity band ring, continuous pavé sapphire setting, stackable bridal design, feminine everyday luxury"

2. STONE
   Full gemstone name + colour with saturation qualifier (vivid / deep / pastel / icy / rich),
   cut style (round brilliant / oval / cushion / emerald-cut / pear), estimated carat range,
   clarity appearance (eye-clean / slight silk inclusions / velvety depth),
   luster type (vitreous / adamantine / pearlescent / waxy),
   light behaviour (strong dispersion / rainbow flashes / subsurface glow / silk sheen),
   any optical phenomenon (adularescence / colour-shift / chatoyancy / asterism / pleochroism)

3. METAL
   Karat and alloy, exact surface finish (high-polish mirror / satin / brushed / hammered / oxidised),
   warmth/coolness of tone, visible micro-reflections, edge definition quality

4. SETTING CONSTRUCTION
   Exact prong count and shape, claw geometry, bezel wall height, pavé grain density,
   micro-pavé pattern, gallery design, under-gallery detail, side profile silhouette

5. BAND / SHANK
   Cross-section profile (comfort-fit round / flat / knife-edge / split-shank / twisted),
   tapering detail from shoulder to back, band width in mm,
   any milgrain border, filigree pattern, engraving, or surface texture

6. ACCENT & ORNAMENTAL DETAILS
   Side stones, shoulder pavé, hidden halo under-detail, engraving motifs,
   negative space cutouts, decorative gallery rails, scrollwork, milgrain, filigree

7. STYLE MOOD
   3–5 specific mood/aesthetic words + visual metaphors
   Example: "ethereal romantic luminosity, soft feminine grace, whisper-light delicacy"

8. SCALE & PROPORTION
   Approximate band width in mm, stone face-up diameter, overall weight feel (featherlight / moderate / substantial),
   finger coverage and visual footprint

9. LIGHTING
   Exact studio lighting setup: soft diffused octabox / dramatic raking side light / backlit stone glow,
   catch-light placement on prong tips, specular highlight streak on polished metal,
   subsurface light scatter inside gemstone, shadow depth and direction

10. BACKGROUND & SURFACE
    Specific surface with texture and colour:
    Example: "polished white Carrara marble surface", "aged charcoal velvet pad", "pure white seamless sweep",
    "frosted glass shelf", "deep blush satin ribbon", "dark navy linen"

11. CAMERA & LENS
    Exact angle: 45-degree three-quarter hero shot / top-down flat lay / side-profile macro /
    three-quarter elevated perspective,
    lens: 90mm macro / 100mm macro / 50mm, aperture f/2.8 shallow DOF,
    tack-sharp stone facets, bokeh background, zero perspective distortion

12. POST-PROCESSING
    Colour grade mood: warm luxury editorial / neutral clean editorial / cool e-commerce white /
    dramatic high-contrast fine-art, retouching level (flawless commercial / natural editorial)

13. TECHNICAL QUALITY
    photorealistic, professional jewellery photography, 8K resolution, ultra-detailed,
    tack-sharp focus, ray tracing, global illumination, HDR, subsurface scattering in gemstone,
    award-winning commercial jewellery image

=== INSPIRATION INTEGRATION ===
If the brief includes INSPIRATION KEYWORDS, translate each keyword directly into \
specific visual design language — milgrain for "vintage_feel", clean negative space for "minimal", etc. \
These keywords must visibly influence the setting detail, band texture, and mood descriptors.

Minimum 130 comma-separated descriptors total. Be obsessively specific and concrete.
"""

HUMAN_PROMPT = "{product_prompt}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_additional_details(text: str) -> str:
    """Strip the trailing 'Inspiration Keywords: ...' line that the frontend appends."""
    cleaned = re.sub(r"\n*inspiration keywords\s*:.*$", "", text, flags=re.IGNORECASE).strip()
    return cleaned or ""


def _keyword_visuals(keywords: list[str]) -> str:
    """Translate inspiration keywords to visual directives."""
    directives = []
    for kw in keywords:
        key = kw.lower().replace(" ", "_").replace("-", "_")
        directive = _KEYWORD_VISUAL.get(key)
        if directive:
            directives.append(f"{kw} → {directive}")
        else:
            directives.append(kw)
    return "; ".join(directives)


# ---------------------------------------------------------------------------
# Brief builder — converts questionnaire answers into a structured design brief
# ---------------------------------------------------------------------------

def build_product_prompt(
    submission: QuestionnaireSubmission,
    stone_assessment: Optional[StoneSuitability],
) -> str:
    jewelry = (
        submission.jewelry_type_other
        if submission.jewelry_type.value == "Other" and submission.jewelry_type_other
        else submission.jewelry_type.value
    )

    # ------------------------------------------------------------------
    # Stone block — rich visual description
    # ------------------------------------------------------------------
    if submission.stone_branch == StoneBranch.already_have and submission.own_stone:
        s = submission.own_stone
        stone_name = s.stone_type or "gemstone"
        stone_visual = _STONE_VISUAL.get((stone_name or "").lower(), "")
        color_visual = _STONE_COLOR_VISUAL.get((s.color or "").lower(), s.color or "")
        stone_block = (
            f"STONE (customer-supplied):\n"
            f"  Type        : {stone_name}\n"
            f"  Colour      : {s.color or 'not specified'}{f' — {color_visual}' if color_visual and s.color else ''}\n"
            f"  Shape / Cut : {s.shape or 'not specified'}\n"
            f"  Approx size : {s.approximate_size or 'not specified'}\n"
        )
        if stone_visual:
            stone_block += f"  Visual notes: {stone_visual}\n"
        color_part = f"{s.color} " if s.color else ""
        shape_part = f", {s.shape} cut" if s.shape else ""
        size_part = f", ~{s.approximate_size}" if s.approximate_size else ""
        stone_summary = f"{color_part}{stone_name}{shape_part}{size_part}"

    elif submission.stone_branch == StoneBranch.yss_sku and submission.yss_reference:
        stone_name = stone_assessment.stone_name if stone_assessment else "gemstone"
        stone_visual = _STONE_VISUAL.get(stone_name.lower(), "")
        stone_block = (
            f"STONE (from YSS catalogue):\n"
            f"  YSS Reference : {submission.yss_reference}\n"
        )
        if stone_assessment:
            color_families = ', '.join(stone_assessment.color_families)
            stone_block += (
                f"  Stone name    : {stone_assessment.stone_name}\n"
                f"  Colour family : {color_families}\n"
                f"  Ring fit      : {stone_assessment.fit_label.value}\n"
            )
        if stone_visual:
            stone_block += f"  Visual notes  : {stone_visual}\n"
        stone_summary = stone_name

    elif stone_assessment:
        stone_name = stone_assessment.stone_name
        stone_visual = _STONE_VISUAL.get(stone_name.lower(), "")
        color_families = stone_assessment.color_families

        # Resolve color description: use chosen_color if present, else first color family
        chosen_color_key = (submission.chosen_color or "").lower()
        color_visual = _STONE_COLOR_VISUAL.get(chosen_color_key, "")
        if not color_visual and color_families:
            color_visual = _STONE_COLOR_VISUAL.get(color_families[0].lower(), color_families[0])

        displayed_color = submission.chosen_color or (color_families[0] if color_families else "")

        stone_block = (
            f"STONE (selected based on customer preferences):\n"
            f"  Name          : {stone_name}\n"
            f"  Colour        : {displayed_color}{f' — {color_visual}' if color_visual else ''}\n"
            f"  Colour family : {', '.join(color_families)}\n"
            f"  Ring fit      : {stone_assessment.fit_label.value}\n"
            f"  Durability    : {stone_assessment.protection_level} protection required\n"
        )
        if stone_visual:
            stone_block += f"  Visual notes  : {stone_visual}\n"
        stone_summary = f"{displayed_color} {stone_name}" if displayed_color else stone_name

    elif submission.chosen_color:
        color_visual = _STONE_COLOR_VISUAL.get(submission.chosen_color.lower(), "")
        stone_block = (
            f"STONE:\n"
            f"  Customer colour preference : {submission.chosen_color}"
            f"{f' — {color_visual}' if color_visual else ''}\n"
            f"  Select the best matching gemstone for this colour.\n"
        )
        stone_summary = f"{submission.chosen_color} gemstone"

    else:
        stone_block = "STONE: not specified — select an appropriate gemstone.\n"
        stone_summary = "gemstone"

    # ------------------------------------------------------------------
    # Style family visual
    # ------------------------------------------------------------------
    style_family_label = submission.style_family or "not specified"
    style_family_visual = _STYLE_FAMILY_VISUAL.get(style_family_label, "")

    # ------------------------------------------------------------------
    # Other resolved fields
    # ------------------------------------------------------------------
    metal_val    = submission.metal.value if submission.metal else None
    setting_val  = submission.setting.value if submission.setting else None
    wear_val     = submission.wear_frequency.value if submission.wear_frequency else None
    direction_val = submission.style_direction.value if submission.style_direction else None

    metal_detail    = _METAL_FINISH.get(metal_val, metal_val or "not specified")
    setting_detail  = _SETTING_DETAIL.get(setting_val, setting_val or "not specified")
    wear_detail     = _WEAR_CONTEXT.get(wear_val, wear_val or "not specified")
    direction_detail = _DIRECTION_DETAIL.get(direction_val, direction_val or "not specified")
    direction_label  = direction_val or submission.gender_type or "not specified"

    # ------------------------------------------------------------------
    # Assemble brief
    # ------------------------------------------------------------------
    lines = [
        "=" * 64,
        "JEWELLERY DESIGN BRIEF",
        "=" * 64,
        "",
        f"PIECE TYPE       : {jewelry}",
        f"STYLE FAMILY     : {style_family_label}",
    ]

    if style_family_visual:
        lines += [f"  Visual design  : {style_family_visual}"]

    lines += [
        f"STYLE DIRECTION  : {direction_label} — {direction_detail}",
    ]

    if submission.style:
        lines += [f"STYLE NOTES      : {submission.style}"]

    if submission.size_type:
        lines += [f"RING SIZE TYPE   : {submission.size_type}"]

    lines += [
        "",
        stone_block.rstrip(),
        "",
        f"METAL            : {metal_val or 'not specified'} — {metal_detail}",
        f"SETTING          : {setting_val or 'not specified'} — {setting_detail}",
        f"WEAR CONTEXT     : {wear_val or 'not specified'} — {wear_detail}",
    ]

    # ------------------------------------------------------------------
    # Customer notes (clean up duplicated keyword lines from frontend)
    # ------------------------------------------------------------------
    if submission.final_preferences:
        lines += ["", f"CUSTOMER NOTES   : {submission.final_preferences}"]

    if submission.additional_details:
        cleaned = _clean_additional_details(submission.additional_details)
        if cleaned:
            lines += ["", f"ADDITIONAL NOTES : {cleaned}"]

    if submission.additional_style:
        lines += ["", f"STYLE NOTES (extra) : {submission.additional_style}"]

    # ------------------------------------------------------------------
    # Inspiration keywords — translated to visual directives
    # ------------------------------------------------------------------
    if submission.inspiration_keywords:
        visual_directives = _keyword_visuals(submission.inspiration_keywords)
        lines += [
            "",
            f"INSPIRATION KEYWORDS : {', '.join(submission.inspiration_keywords)}",
            f"VISUAL DIRECTIVES    : {visual_directives}",
            "→ These keywords MUST be reflected in the setting texture, band detail, and mood language of the image prompt.",
        ]

    if submission.inspiration_image_url:
        lines += ["", "REFERENCE IMAGE  : Customer has uploaded an inspiration image. Match its overall visual mood and aesthetic closely."]

    # ------------------------------------------------------------------
    # Task instructions
    # ------------------------------------------------------------------
    lines += [
        "",
        "=" * 64,
        "YOUR TASK",
        "=" * 64,
        "",
        "Generate a single JSON object with two keys:",
        "",
        f'1. "image_prompt"',
        f"   Create an extremely detailed image generation prompt for: "
        f"{stone_summary} set in {metal_val or 'the specified metal'}, "
        f"{style_family_label} style ring.",
        f"   The prompt must visually render ALL design details from this brief.",
        f"   Apply every VISUAL DIRECTIVE from the inspiration keywords above.",
        f"   Follow ALL rules in the system prompt exactly.",
        "",
        f'2. "cautions"',
        f"   One sentence of stone care advice if the stone requires special handling, otherwise null.",
    ]

    return "\n".join(lines)
