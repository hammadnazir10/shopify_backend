import re
from typing import List, Optional

from app.data import ALL_COLORS, ALL_STONE_NAMES, STONE_TABLE, STONE_BY_NAME, YSS_STONE_CATALOG
from app.models import (
    FitLabel,
    FIT_TO_LABEL,
    JewelryType,
    StoneSuitability,
    WearFrequency,
)

# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------

COLOR_PRIMARY_SCORE = 40
COLOR_SECONDARY_SCORE = 20

FIT_SCORES = {
    "strong": {"ring": 35, "earring": 25, "pendant": 25, "bracelet": 20},
    "good":   {"ring": 20, "earring": 14, "pendant": 14, "bracelet": 11},
    "conditional": {"ring": 8, "earring": 6, "pendant": 6, "bracelet": 5},
    "avoid":  {"ring": 0, "earring": 0, "pendant": 0, "bracelet": 0},
}

# Bonus for wear frequency × protection level (lower protection = more suitable for daily wear)
WEAR_PROTECTION_BONUS = {
    WearFrequency.every_day:        {"low": 20, "medium": 8,  "high": 0},
    WearFrequency.often_carefully:  {"low": 12, "medium": 6,  "high": 2},
    WearFrequency.special_occasions: {"low": 6,  "medium": 4,  "high": 2},
}

COLOR_LOOKUP = {c.lower(): c for c in ALL_COLORS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _jewelry_type_key(jewelry_type: JewelryType) -> str:
    """Map JewelryType enum to the fit column key used in STONE_TABLE."""
    mapping = {
        JewelryType.ring: "ring",
        JewelryType.necklace_pendant: "pendant",
        JewelryType.bracelet: "bracelet",
        JewelryType.earrings: "earring",
        JewelryType.other: "ring",  # conservative default
    }
    return mapping[jewelry_type]


def _get_fit_and_protection(stone: dict, jtype_key: str):
    fit = stone.get(f"{jtype_key}_fit", "conditional")
    # Protection is currently only stored for rings; use it across all types
    # as it reflects overall stone fragility
    protection = stone.get("ring_protection", "medium")
    return fit, protection


def _build_suitability(stone: dict, jtype_key: str, score: int = 0) -> StoneSuitability:
    fit, protection = _get_fit_and_protection(stone, jtype_key)
    return StoneSuitability(
        stone_name=stone["name"],
        color_families=stone["color_families"],
        fit_label=FIT_TO_LABEL[fit],
        protection_level=protection,
        score=score,
    )


def _normalize_color(color: str) -> Optional[str]:
    return COLOR_LOOKUP.get(color.strip().lower())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_stones_by_color(
    color: str,
    jewelry_type: JewelryType,
    wear_frequency: Optional[WearFrequency] = None,
) -> List[StoneSuitability]:
    """
    Return all stones that include the chosen colour, ranked by suitability score.
    """
    normalized_color = _normalize_color(color)
    if not normalized_color:
        return []

    jtype_key = _jewelry_type_key(jewelry_type)
    results: List[StoneSuitability] = []

    for stone in STONE_TABLE:
        colors = stone["color_families"]
        if normalized_color not in colors:
            continue

        # Colour score: primary (first listed) vs secondary
        color_score = COLOR_PRIMARY_SCORE if colors[0] == normalized_color else COLOR_SECONDARY_SCORE

        # Fit score
        fit, protection = _get_fit_and_protection(stone, jtype_key)
        fit_score = FIT_SCORES[fit][jtype_key]

        # Wear/protection bonus
        wear_bonus = 0
        if wear_frequency:
            wear_bonus = WEAR_PROTECTION_BONUS[wear_frequency][protection]

        total = color_score + fit_score + wear_bonus

        results.append(_build_suitability(stone, jtype_key, score=total))

    results.sort(key=lambda s: s.score, reverse=True)
    return results


def assess_stone_by_name(
    stone_name: str,
    jewelry_type: JewelryType,
    wear_frequency: Optional[WearFrequency] = None,
) -> Optional[StoneSuitability]:
    """
    Return suitability info for a specific stone + jewelry type combination.
    Returns None if the stone name is not found.
    """
    stone = STONE_BY_NAME.get(stone_name.lower())
    if not stone:
        return None

    jtype_key = _jewelry_type_key(jewelry_type)
    fit, protection = _get_fit_and_protection(stone, jtype_key)
    fit_score = FIT_SCORES[fit][jtype_key]

    wear_bonus = 0
    if wear_frequency:
        wear_bonus = WEAR_PROTECTION_BONUS[wear_frequency][protection]

    return _build_suitability(stone, jtype_key, score=fit_score + wear_bonus)


def get_stone_suitability_for_own_stone(
    stone_type: str,
    jewelry_type: JewelryType,
    wear_frequency: Optional[WearFrequency] = None,
) -> Optional[StoneSuitability]:
    """Stone assessment for customers who already own a stone."""
    return assess_stone_by_name(stone_type, jewelry_type, wear_frequency)


def resolve_stone_from_yss_reference(reference: str) -> Optional[str]:
    """Resolve a YSS product link or SKU to a catalogued stone name."""
    ref = reference.strip()
    if not ref:
        return None

    # 1) Direct SKU match
    upper_ref = ref.upper()
    if upper_ref in YSS_STONE_CATALOG:
        return YSS_STONE_CATALOG[upper_ref]

    # 2) Extract canonical SKU from text/URL, e.g. YSS12345 or yss-12345
    sku_match = re.search(r"YSS[-_]?(\d{3,})", upper_ref)
    if sku_match:
        canonical_sku = f"YSS-{sku_match.group(1)}"
        if canonical_sku in YSS_STONE_CATALOG:
            return YSS_STONE_CATALOG[canonical_sku]

    # 3) Match known SKU embedded in links
    for sku, stone_name in YSS_STONE_CATALOG.items():
        if sku in upper_ref:
            return stone_name

    # 4) Fallback: infer by stone name mention in the reference
    ref_lower = ref.lower()
    for stone_name in ALL_STONE_NAMES:
        if stone_name.lower() in ref_lower:
            return stone_name

    return None


def get_scoring_rules() -> dict[str, int]:
    """Expose scoring constants used by colour and fit ranking."""
    return {
        "primary_colour_match": COLOR_PRIMARY_SCORE,
        "secondary_colour_match": COLOR_SECONDARY_SCORE,
        "ring_fit_strong": FIT_SCORES["strong"]["ring"],
        "ring_fit_good": FIT_SCORES["good"]["ring"],
        "ring_fit_conditional": FIT_SCORES["conditional"]["ring"],
        "earring_fit_strong": FIT_SCORES["strong"]["earring"],
        "pendant_fit_strong": FIT_SCORES["strong"]["pendant"],
        "bracelet_fit_strong": FIT_SCORES["strong"]["bracelet"],
        "daily_wear_low_protection": WEAR_PROTECTION_BONUS[WearFrequency.every_day]["low"],
        "daily_wear_medium_protection": WEAR_PROTECTION_BONUS[WearFrequency.every_day]["medium"],
        "daily_wear_high_protection": WEAR_PROTECTION_BONUS[WearFrequency.every_day]["high"],
    }
