"""Questionnaire request schemas — internal model + camelCase frontend payload."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.enums import (
    JewelryType,
    MetalOption,
    RingStyleFamily,
    SettingOption,
    StoneBranch,
    StoneChoiceMethod,
    StyleDirection,
    WearFrequency,
)
from app.schemas.stone import OwnStoneDetails

# ---------------------------------------------------------------------------
# Slug → enum maps (frontend sends kebab-case; we also accept display values)
# ---------------------------------------------------------------------------

_JEWELRY_MAP: Dict[str, JewelryType] = {
    "ring": JewelryType.ring,
    "Ring": JewelryType.ring,
    "necklace": JewelryType.necklace_pendant,
    "pendant": JewelryType.necklace_pendant,
    "Necklace / Pendant": JewelryType.necklace_pendant,
    "bracelet": JewelryType.bracelet,
    "Bracelet": JewelryType.bracelet,
    "earrings": JewelryType.earrings,
    "Earrings": JewelryType.earrings,
    "other": JewelryType.other,
    "Other": JewelryType.other,
}

_GENDER_TO_DIRECTION: Dict[str, StyleDirection] = {
    "female": StyleDirection.feminine,
    "feminine": StyleDirection.feminine,
    "Feminine": StyleDirection.feminine,
    "male": StyleDirection.masculine,
    "masculine": StyleDirection.masculine,
    "Masculine": StyleDirection.masculine,
    "unisex": StyleDirection.balanced,
    "balanced": StyleDirection.balanced,
    "Balanced": StyleDirection.balanced,
}

_STONE_BRANCH_MAP: Dict[str, StoneBranch] = {
    "choose": StoneBranch.help_choose,
    "No, help me choose": StoneBranch.help_choose,
    "own": StoneBranch.already_have,
    "Yes, I already have a stone": StoneBranch.already_have,
    "yss": StoneBranch.yss_sku,
    "I have a YSS stone link or SKU": StoneBranch.yss_sku,
}

_PICK_MAP: Dict[str, StoneChoiceMethod] = {
    "color": StoneChoiceMethod.by_color,
    "colour": StoneChoiceMethod.by_color,
    "Pick by colour": StoneChoiceMethod.by_color,
    "stone": StoneChoiceMethod.by_stone,
    "Pick by stone": StoneChoiceMethod.by_stone,
}

_METAL_MAP: Dict[str, MetalOption] = {
    "rose-gold": MetalOption.rose_gold,
    "Rose gold": MetalOption.rose_gold,
    "yellow-gold": MetalOption.yellow_gold,
    "Yellow gold": MetalOption.yellow_gold,
    "white-gold": MetalOption.white_gold,
    "White gold": MetalOption.white_gold,
    "platinum": MetalOption.platinum,
    "Platinum": MetalOption.platinum,
}

_SETTING_MAP: Dict[str, SettingOption] = {
    "rounded-claw": SettingOption.rounded_claw,
    "Rounded Claw / Prong Set": SettingOption.rounded_claw,
    "sharp-claw": SettingOption.sharp_claw,
    "Sharp Claw / Prong Set": SettingOption.sharp_claw,
    "bezel": SettingOption.bezel,
    "Bezel Set": SettingOption.bezel,
    "half-bezel": SettingOption.half_bezel,
    "Half Bezel / Partial Frame": SettingOption.half_bezel,
    "halo": SettingOption.halo,
    "Halo": SettingOption.halo,
    "hidden-halo": SettingOption.hidden_halo,
    "Hidden Halo": SettingOption.hidden_halo,
}


# ---------------------------------------------------------------------------
# Internal canonical submission
# ---------------------------------------------------------------------------

class QuestionnaireSubmission(BaseModel):
    jewelry_type: JewelryType
    jewelry_type_other: Optional[str] = None

    style_direction: Optional[StyleDirection] = None
    gender_type: Optional[str] = None

    style: Optional[str] = None
    style_family: Optional[str] = None

    stone_branch: Optional[StoneBranch] = None
    own_stone: Optional[OwnStoneDetails] = None
    yss_reference: Optional[str] = None
    chosen_stone_name: Optional[str] = None
    chosen_color: Optional[str] = None

    metal: Optional[MetalOption] = None
    setting: Optional[SettingOption] = None
    size_type: Optional[str] = None
    wear_frequency: Optional[WearFrequency] = None

    final_preferences: Optional[str] = None
    additional_details: Optional[str] = None
    additional_style: Optional[str] = None
    inspiration_keywords: Optional[List[str]] = None
    inspiration_image_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Frontend camelCase payload
# ---------------------------------------------------------------------------

class RingSelectionPayload(BaseModel):
    """Submission payload sent by the frontend (camelCase)."""

    jewelleryType: Optional[str] = Field(None, description="Jewelry type slug, e.g. 'ring'")
    genderType: Optional[str] = Field(None, description="Gender target: female / male / unisex")
    style: Optional[str] = None
    ringStyleFamily: Optional[str] = None
    metalType: Optional[str] = None
    sizeType: Optional[str] = None
    stone: Optional[str] = Field(None, description="Stone branch: 'choose' | 'own' | 'yss'")
    gemType: Optional[str] = None
    stonecolor: Optional[str] = None
    prefersetting: Optional[str] = None
    pick: Optional[str] = Field(None, description="'color' | 'stone'")
    wearFrequency: Optional[str] = None
    personalPreferences: Optional[str] = None
    additionalDetails: Optional[str] = None
    additionalStyle: Optional[str] = None
    inspirationKeywords: Optional[List[str]] = None
    chosenColor: Optional[str] = None
    imagePreview: Optional[str] = None
    yssReference: Optional[str] = None
    ownStone: Optional[OwnStoneDetails] = None

    def to_questionnaire_submission(self) -> QuestionnaireSubmission:
        """Translate the frontend payload into the canonical submission model."""
        style_family = _safe_enum(RingStyleFamily, self.ringStyleFamily)
        wear_frequency = _safe_enum(WearFrequency, self.wearFrequency)
        color = self.stonecolor or self.chosenColor or None

        return QuestionnaireSubmission(
            jewelry_type=_JEWELRY_MAP.get(self.jewelleryType or "", JewelryType.ring),
            gender_type=self.genderType,
            style_direction=_GENDER_TO_DIRECTION.get(self.genderType or ""),
            style=self.style or None,
            style_family=style_family.value if style_family else None,
            stone_branch=_STONE_BRANCH_MAP.get(self.stone or "") if self.stone else None,
            own_stone=self.ownStone,
            yss_reference=self.yssReference or None,
            chosen_stone_name=self.gemType or None,
            chosen_color=color,
            metal=_METAL_MAP.get(self.metalType or ""),
            setting=_SETTING_MAP.get(self.prefersetting or ""),
            size_type=self.sizeType or None,
            wear_frequency=wear_frequency,
            final_preferences=self.personalPreferences or None,
            additional_details=self.additionalDetails or None,
            additional_style=self.additionalStyle or None,
            inspiration_keywords=self.inspirationKeywords or None,
            inspiration_image_url=self.imagePreview or None,
        )


def _safe_enum(enum_cls, raw):
    """Return the enum member matching `raw` exactly, or None."""
    if not raw:
        return None
    try:
        return enum_cls(raw)
    except ValueError:
        return None
