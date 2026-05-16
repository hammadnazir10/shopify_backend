"""Enumerations used by the questionnaire and design schemas."""

from enum import Enum


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


class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"
