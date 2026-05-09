"""Stone selection logic — scoring, suitability, and YSS reference resolution."""

from __future__ import annotations

import re
from typing import List, Optional

from app.data import (
    ALL_COLORS,
    ALL_STONE_NAMES,
    STONE_BY_NAME,
    STONE_TABLE,
    YSS_STONE_CATALOG,
)
from app.schemas import (
    FIT_TO_LABEL,
    JewelryType,
    StoneSuitability,
    WearFrequency,
)

# ---------------------------------------------------------------------------
# Scoring constants
# ---------------------------------------------------------------------------

COLOR_PRIMARY_SCORE = 40
COLOR_SECONDARY_SCORE = 20

FIT_SCORES = {
    "strong": {"ring": 35, "earring": 25, "pendant": 25, "bracelet": 20},
    "good": {"ring": 20, "earring": 14, "pendant": 14, "bracelet": 11},
    "conditional": {"ring": 8, "earring": 6, "pendant": 6, "bracelet": 5},
    "avoid": {"ring": 0, "earring": 0, "pendant": 0, "bracelet": 0},
}

WEAR_PROTECTION_BONUS = {
    WearFrequency.every_day: {"low": 20, "medium": 8, "high": 0},
    WearFrequency.often_carefully: {"low": 12, "medium": 6, "high": 2},
    WearFrequency.special_occasions: {"low": 6, "medium": 4, "high": 2},
}

_JEWELRY_TYPE_KEY = {
    JewelryType.ring: "ring",
    JewelryType.necklace_pendant: "pendant",
    JewelryType.bracelet: "bracelet",
    JewelryType.earrings: "earring",
    JewelryType.other: "ring",
}

_COLOR_LOOKUP = {c.lower(): c for c in ALL_COLORS}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fit_and_protection(stone: dict, jtype_key: str):
    return stone.get(f"{jtype_key}_fit", "conditional"), stone.get("ring_protection", "medium")


def _build_suitability(stone: dict, jtype_key: str, score: int = 0) -> StoneSuitability:
    fit, protection = _fit_and_protection(stone, jtype_key)
    return StoneSuitability(
        stone_name=stone["name"],
        color_families=stone["color_families"],
        fit_label=FIT_TO_LABEL[fit],
        protection_level=protection,
        score=score,
    )


def _normalize_color(color: str) -> Optional[str]:
    return _COLOR_LOOKUP.get(color.strip().lower())


def _wear_bonus(wear: Optional[WearFrequency], protection: str) -> int:
    return WEAR_PROTECTION_BONUS[wear][protection] if wear else 0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_stones_by_color(
    color: str,
    jewelry_type: JewelryType,
    wear_frequency: Optional[WearFrequency] = None,
) -> List[StoneSuitability]:
    """Return all stones matching the chosen colour, ranked by suitability."""
    normalized = _normalize_color(color)
    if not normalized:
        return []

    jtype_key = _JEWELRY_TYPE_KEY[jewelry_type]
    results: List[StoneSuitability] = []

    for stone in STONE_TABLE:
        colors = stone["color_families"]
        if normalized not in colors:
            continue

        color_score = COLOR_PRIMARY_SCORE if colors[0] == normalized else COLOR_SECONDARY_SCORE
        fit, protection = _fit_and_protection(stone, jtype_key)
        score = color_score + FIT_SCORES[fit][jtype_key] + _wear_bonus(wear_frequency, protection)
        results.append(_build_suitability(stone, jtype_key, score=score))

    results.sort(key=lambda s: s.score, reverse=True)
    return results


def assess_stone_by_name(
    stone_name: str,
    jewelry_type: JewelryType,
    wear_frequency: Optional[WearFrequency] = None,
) -> Optional[StoneSuitability]:
    """Return suitability info for a specific stone + jewelry type."""
    stone = STONE_BY_NAME.get(stone_name.lower())
    if not stone:
        return None

    jtype_key = _JEWELRY_TYPE_KEY[jewelry_type]
    fit, protection = _fit_and_protection(stone, jtype_key)
    score = FIT_SCORES[fit][jtype_key] + _wear_bonus(wear_frequency, protection)
    return _build_suitability(stone, jtype_key, score=score)


def get_stone_suitability_for_own_stone(
    stone_type: str,
    jewelry_type: JewelryType,
    wear_frequency: Optional[WearFrequency] = None,
) -> Optional[StoneSuitability]:
    """Suitability assessment for customers who already own a stone."""
    return assess_stone_by_name(stone_type, jewelry_type, wear_frequency)


def resolve_stone_from_yss_reference(reference: str) -> Optional[str]:
    """Resolve a YSS link or SKU to a catalogued stone name."""
    ref = reference.strip()
    if not ref:
        return None

    upper_ref = ref.upper()
    if upper_ref in YSS_STONE_CATALOG:
        return YSS_STONE_CATALOG[upper_ref]

    sku_match = re.search(r"YSS[-_]?(\d{3,})", upper_ref)
    if sku_match:
        canonical_sku = f"YSS-{sku_match.group(1)}"
        if canonical_sku in YSS_STONE_CATALOG:
            return YSS_STONE_CATALOG[canonical_sku]

    for sku, stone_name in YSS_STONE_CATALOG.items():
        if sku in upper_ref:
            return stone_name

    ref_lower = ref.lower()
    for stone_name in ALL_STONE_NAMES:
        if stone_name.lower() in ref_lower:
            return stone_name

    return None
