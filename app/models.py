from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class JewelryType(str, Enum):
    ring = "Ring"
    necklace_pendant = "Necklace / Pendant"
    bracelet = "Bracelet"
    earrings = "Earrings"
    other = "Other"


class RingStyleFamily(str, Enum):
    solitaire = "Solitaire"
    three_stone = "Three Stone"
    halo = "Halo"
    bezel = "Bezel"
    signet = "Signet"
    cluster = "Cluster"
    toi_et_moi = "Toi et Moi"
    eternity = "Eternity"
    vintage_inspired = "Vintage-Inspired"
    contemporary_minimal = "Contemporary Minimal"


class StyleDirection(str, Enum):
    masculine = "Masculine"
    balanced = "Balanced"
    feminine = "Feminine"


class StoneBranch(str, Enum):
    already_have = "Yes, I already have a stone"
    yss_sku = "I have a YSS stone link or SKU"
    help_choose = "No, help me choose"


class StoneChoiceMethod(str, Enum):
    by_stone = "Pick by stone"
    by_color = "Pick by colour"


class MetalOption(str, Enum):
    yellow_gold = "Yellow gold"
    white_gold = "White gold"
    rose_gold = "Rose gold"
    platinum = "Platinum"


class SettingOption(str, Enum):
    sharp_claw = "Sharp Claw / Prong Set"
    rounded_claw = "Rounded Claw / Prong Set"
    bezel = "Bezel Set"
    half_bezel = "Half Bezel / Partial Frame"
    halo = "Halo"
    hidden_halo = "Hidden Halo"


class WearFrequency(str, Enum):
    every_day = "Every day"
    often_carefully = "Often, but carefully"
    special_occasions = "Special occasions"


# ---------------------------------------------------------------------------
# Payload value → enum maps (support both kebab-case slugs and display values)
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
# Stone scoring / fit models
# ---------------------------------------------------------------------------

class FitLabel(str, Enum):
    excellent = "Excellent fit"
    great = "Great fit"
    protective_setting = "Works well with a more protective setting"
    careful_wear = "Better for careful wear"


FIT_TO_LABEL = {
    "strong": FitLabel.excellent,
    "good": FitLabel.great,
    "conditional": FitLabel.protective_setting,
    "avoid": FitLabel.careful_wear,
}


class StoneSuitability(BaseModel):
    stone_name: str
    color_families: List[str]
    fit_label: FitLabel
    protection_level: str  # low | medium | high
    score: int = 0


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class OwnStoneDetails(BaseModel):
    stone_type: Optional[str] = Field(None, description="Stone type")
    color: Optional[str] = Field(None, description="Colour")
    shape: Optional[str] = Field(None, description="Shape")
    approximate_size: Optional[str] = Field(None, description="Approximate size or carat weight")


class QuestionnaireSubmission(BaseModel):
    # Q1
    jewelry_type: JewelryType
    jewelry_type_other: Optional[str] = Field(None, description="Free text when jewelry_type is 'Other'")

    # Q2 — gender/style direction
    style_direction: Optional[StyleDirection] = None
    gender_type: Optional[str] = None          # raw value from payload (e.g. "female")

    # General style descriptor
    style: Optional[str] = None

    # Q3 — style family chosen from dynamic list
    style_family: Optional[str] = None

    # Q4 — stone branch
    stone_branch: Optional[StoneBranch] = None

    # Branch 1 — own stone
    own_stone: Optional[OwnStoneDetails] = None

    # Branch 2 — YSS
    yss_reference: Optional[str] = Field(None, description="YSS product link or SKU")

    # Branch 3A — pick by stone
    chosen_stone_name: Optional[str] = None

    # Branch 3B — pick by colour
    chosen_color: Optional[str] = None

    # Q5
    metal: Optional[MetalOption] = None

    # Q6
    setting: Optional[SettingOption] = None

    # Ring size
    size_type: Optional[str] = None

    # Q7
    wear_frequency: Optional[WearFrequency] = None

    # Q8
    final_preferences: Optional[str] = None

    # Additional details (may include inspiration keywords narrative)
    additional_details: Optional[str] = None

    # Additional style notes
    additional_style: Optional[str] = None

    # Parsed inspiration keywords list
    inspiration_keywords: Optional[List[str]] = None

    # Q9 — optional inspiration image (URL returned by /upload-image)
    inspiration_image_url: Optional[str] = Field(
        None, description="URL of the uploaded inspiration image (from /api/questionnaire/upload-image)"
    )


# ---------------------------------------------------------------------------
# Ring-specific submission model (camelCase payload)
# ---------------------------------------------------------------------------

class RingSelectionPayload(BaseModel):
    """Dedicated submission model for ring designs — accepts camelCase payload."""

    # Q1 — jewelry type (e.g. "ring")
    jewelleryType: Optional[str] = Field(None, description="Jewelry type slug, e.g. 'ring'")

    # Gender target — maps to StyleDirection (e.g. "female" → Feminine)
    genderType: Optional[str] = Field(None, description="Gender target: female / male / unisex")

    # General style descriptor (free text)
    style: Optional[str] = Field(None, description="General style preference (free text)")

    # Q3 — ring style family (e.g. "Eternity")
    ringStyleFamily: Optional[str] = Field(None, description="Ring style family name")

    # Q5 — metal type slug (e.g. "rose-gold")
    metalType: Optional[str] = Field(None, description="Metal type slug, e.g. 'rose-gold'")

    # Ring size type
    sizeType: Optional[str] = Field(None, description="Ring size type")

    # Q4 — stone branch slug: "choose" | "own" | "yss"
    stone: Optional[str] = Field(None, description="Stone option: 'choose' | 'own' | 'yss'")

    # Gemstone name / type (used when pick="stone" or stone="choose")
    gemType: Optional[str] = Field(None, description="Gemstone type or name, e.g. 'sapphire'")

    # Stone colour (used when pick="color")
    stonecolor: Optional[str] = Field(None, description="Stone colour, e.g. 'pink'")

    # Q6 — preferred setting slug (e.g. "rounded-claw")
    prefersetting: Optional[str] = Field(None, description="Setting style slug, e.g. 'rounded-claw'")

    # Stone selection method: "color" | "stone"
    pick: Optional[str] = Field(None, description="Stone selection method: 'color' | 'stone'")

    # Q7 — wear frequency (display value, e.g. "Often, but carefully")
    wearFrequency: Optional[str] = Field(None, description="Wear frequency")

    # Q8 — personal preferences (free text)
    personalPreferences: Optional[str] = Field(None, description="Personal preferences")

    # Additional details / notes (may contain inspiration keyword narrative)
    additionalDetails: Optional[str] = Field(None, description="Additional details and notes")

    # Additional style notes
    additionalStyle: Optional[str] = Field(None, description="Additional style notes")

    # Parsed inspiration keywords
    inspirationKeywords: Optional[List[str]] = Field(None, description="Inspiration keyword list")

    # Chosen colour (explicit, used alongside pick="color")
    chosenColor: Optional[str] = Field(None, description="Chosen colour for stone selection")

    # Q9 — uploaded inspiration image URL (from /api/upload-image)
    imagePreview: Optional[str] = Field(None, description="Uploaded inspiration image URL")

    # Q4 branch 2 — YSS reference
    yssReference: Optional[str] = Field(None, description="YSS product link or SKU")

    # Q4 branch 1 — own stone details
    ownStone: Optional[OwnStoneDetails] = Field(None, description="Own stone details")

    # ------------------------------------------------------------------
    # Private helpers for resolving slug → enum
    # ------------------------------------------------------------------

    def _resolve_stone_branch(self) -> Optional[StoneBranch]:
        return _STONE_BRANCH_MAP.get(self.stone or "") if self.stone else None

    def _resolve_pick_method(self) -> Optional[StoneChoiceMethod]:
        return _PICK_MAP.get(self.pick or "") if self.pick else None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def check_branch_fields(self) -> "RingSelectionPayload":
        branch = self._resolve_stone_branch()

        if branch == StoneBranch.already_have:
            if not self.ownStone:
                raise ValueError("ownStone is required when stone is 'own'.")

        elif branch == StoneBranch.yss_sku:
            if not self.yssReference:
                raise ValueError("yssReference is required when stone is 'yss'.")

        elif branch == StoneBranch.help_choose:
            pick = self._resolve_pick_method()
            if not pick:
                raise ValueError("pick is required when stone is 'choose' (use 'color' or 'stone').")
            if pick == StoneChoiceMethod.by_stone and not self.gemType:
                raise ValueError("gemType is required when pick is 'stone'.")
            if pick == StoneChoiceMethod.by_color and not (self.stonecolor or self.chosenColor):
                raise ValueError("stonecolor or chosenColor is required when pick is 'color'.")

        return self

    # ------------------------------------------------------------------
    # Conversion to internal model
    # ------------------------------------------------------------------

    def to_questionnaire_submission(self) -> "QuestionnaireSubmission":
        """Map camelCase payload to the internal QuestionnaireSubmission."""

        # Resolve style family
        style_family: Optional[RingStyleFamily] = None
        if self.ringStyleFamily:
            try:
                style_family = RingStyleFamily(self.ringStyleFamily)
            except ValueError:
                style_family = None

        # Resolve wear frequency (display value matches enum directly)
        wear_frequency: Optional[WearFrequency] = None
        if self.wearFrequency:
            try:
                wear_frequency = WearFrequency(self.wearFrequency)
            except ValueError:
                wear_frequency = None

        # Effective colour: stonecolor takes precedence, chosenColor as fallback
        color = self.stonecolor or self.chosenColor or None

        return QuestionnaireSubmission(
            jewelry_type=_JEWELRY_MAP.get(self.jewelleryType or "", JewelryType.ring),
            gender_type=self.genderType,
            style_direction=_GENDER_TO_DIRECTION.get(self.genderType or ""),
            style=self.style or None,
            style_family=style_family.value if style_family else None,
            stone_branch=self._resolve_stone_branch(),
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


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class DesignBrief(BaseModel):
    image_prompt: str
    cautions: Optional[str] = None


class ImageUploadResponse(BaseModel):
    image_url: str
    filename: str


class RingDesignResponse(BaseModel):
    summary: str
    image_prompt: str
    cautions: Optional[str] = None


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., description="The image generation prompt to send to the Banana nano model")


class ImageGenerateResponse(BaseModel):
    image_url: Optional[str] = Field(None, description="URL of the generated image, if returned by the model")
    image_base64: Optional[str] = Field(None, description="Base64-encoded image data, if returned by the model")
    model: str = Field(default="nano", description="Model used for generation")
    prompt: str = Field(..., description="The prompt that was submitted")
