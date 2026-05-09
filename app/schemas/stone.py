"""Stone-related schemas: own-stone details, fit labels, suitability."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OwnStoneDetails(BaseModel):
    stone_type: Optional[str] = Field(None, description="Stone type")
    color: Optional[str] = Field(None, description="Colour")
    shape: Optional[str] = Field(None, description="Shape")
    approximate_size: Optional[str] = Field(None, description="Approximate size or carat weight")


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
