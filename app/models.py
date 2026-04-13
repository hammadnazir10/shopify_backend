from __future__ import annotations

from enum import Enum
from typing import List, Optional
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
    stone_type: str = Field(..., description="Stone type")
    color: str = Field(..., description="Colour")
    shape: str = Field(..., description="Shape")
    approximate_size: str = Field(..., description="Approximate size or carat weight")


class QuestionnaireSubmission(BaseModel):
    # Q1
    jewelry_type: JewelryType
    jewelry_type_other: Optional[str] = Field(None, description="Free text when jewelry_type is 'Other'")

    # Q2
    style_direction: StyleDirection

    # Q3 — style family chosen from dynamic list
    style_family: str

    # Q4 — stone branch
    stone_branch: StoneBranch

    # Branch 1 — own stone
    own_stone: Optional[OwnStoneDetails] = None

    # Branch 2 — YSS
    yss_reference: Optional[str] = Field(None, description="YSS product link or SKU")

    # Branch 3A — pick by stone
    chosen_stone_name: Optional[str] = None

    # Branch 3B — pick by colour
    chosen_color: Optional[str] = None

    # Q5
    metal: MetalOption

    # Q6
    setting: SettingOption

    # Q7
    wear_frequency: WearFrequency

    # Q8
    final_preferences: Optional[str] = None

    # Q9 — optional inspiration image (URL returned by /upload-image)
    inspiration_image_url: Optional[str] = Field(
        None, description="URL of the uploaded inspiration image (from /api/questionnaire/upload-image)"
    )


# ---------------------------------------------------------------------------
# Ring-specific submission model
# ---------------------------------------------------------------------------

class RingSelectionPayload(BaseModel):
    """Dedicated submission model for ring designs.
    jewelry_type is implicitly Ring — callers do not need to supply it."""

    # Q2
    style_direction: StyleDirection

    # Q3 — ring-specific style families only
    style_family: RingStyleFamily

    # Q4 — stone branch
    stone_branch: StoneBranch

    # Q4 branch 1 — own stone (required when stone_branch = "already_have")
    own_stone: Optional[OwnStoneDetails] = None

    # Q4 branch 2 — YSS (required when stone_branch = "yss_sku")
    yss_reference: Optional[str] = Field(None, description="YSS product link or SKU")

    # Q4a — how to choose (required when stone_branch = "help_choose")
    stone_choice_method: Optional[StoneChoiceMethod] = Field(
        None, description="Pick by stone or Pick by colour — required when stone_branch is 'No, help me choose'"
    )

    # Q4 branch 3A — pick by stone (required when stone_choice_method = "Pick by stone")
    chosen_stone_name: Optional[str] = Field(
        None, description="Stone name — required when stone_choice_method is 'Pick by stone'"
    )

    # Q4 branch 3B — pick by colour (required when stone_choice_method = "Pick by colour")
    chosen_color: Optional[str] = Field(
        None, description="Colour — required when stone_choice_method is 'Pick by colour'"
    )

    # Q5
    metal: MetalOption

    # Q6
    setting: SettingOption

    # Q7
    wear_frequency: WearFrequency

    # Q8
    final_preferences: Optional[str] = None

    # Q9 — optional inspiration image URL (from /api/questionnaire/upload-image)
    inspiration_image_url: Optional[str] = Field(
        None, description="URL of an uploaded inspiration image"
    )

    @model_validator(mode="after")
    def check_branch_fields(self) -> "RingSelectionPayload":
        if self.stone_branch == StoneBranch.already_have:
            if not self.own_stone:
                raise ValueError("own_stone is required when stone_branch is 'Yes, I already have a stone'.")

        elif self.stone_branch == StoneBranch.yss_sku:
            if not self.yss_reference:
                raise ValueError("yss_reference is required when stone_branch is 'I have a YSS stone link or SKU'.")

        elif self.stone_branch == StoneBranch.help_choose:
            if not self.stone_choice_method:
                raise ValueError("stone_choice_method is required when stone_branch is 'No, help me choose'.")
            if self.stone_choice_method == StoneChoiceMethod.by_stone and not self.chosen_stone_name:
                raise ValueError("chosen_stone_name is required when stone_choice_method is 'Pick by stone'.")
            if self.stone_choice_method == StoneChoiceMethod.by_color and not self.chosen_color:
                raise ValueError("chosen_color is required when stone_choice_method is 'Pick by colour'.")

        return self

    def to_questionnaire_submission(self) -> "QuestionnaireSubmission":
        """Convert to the generic QuestionnaireSubmission used by business logic."""
        return QuestionnaireSubmission(
            jewelry_type=JewelryType.ring,
            style_direction=self.style_direction,
            style_family=self.style_family.value,
            stone_branch=self.stone_branch,
            own_stone=self.own_stone,
            yss_reference=self.yss_reference,
            chosen_stone_name=self.chosen_stone_name,
            chosen_color=self.chosen_color,
            metal=self.metal,
            setting=self.setting,
            wear_frequency=self.wear_frequency,
            final_preferences=self.final_preferences,
            inspiration_image_url=self.inspiration_image_url,
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
