from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Q3 — Style families per jewelry type
# ---------------------------------------------------------------------------

STYLE_FAMILIES: Dict[str, List[str]] = {
    "Ring": [
        "Solitaire", "Three Stone", "Halo", "Bezel", "Signet", "Cluster",
        "Toi et Moi", "Eternity", "Vintage-Inspired", "Contemporary Minimal",
    ],
    "Necklace / Pendant": [
        "Solitaire Pendant", "Halo Pendant", "Drop Pendant", "Cluster Pendant",
        "Bezel Pendant", "Bar Pendant", "Locket-Style", "Symbolic / Motif",
        "Vintage-Inspired", "Contemporary Minimal",
    ],
    "Bracelet": [
        "Tennis Bracelet", "Chain Bracelet", "Bangle", "Cuff", "Charm Bracelet",
        "Station Bracelet", "Link Bracelet", "Gemstone Line Bracelet",
        "Bezel-Set Bracelet", "Contemporary Minimal",
    ],
    "Earrings": [
        "Studs", "Drops", "Hoops", "Huggies", "Halo Earrings", "Cluster Earrings",
        "Pear Drop Earrings", "Chandeliers", "Bezel-Set Earrings", "Contemporary Minimal",
    ],
    "Other": [],
}

# ---------------------------------------------------------------------------
# YSS stone catalogue (sample mappings for reference/SKU resolution)
# ---------------------------------------------------------------------------

YSS_STONE_CATALOG: Dict[str, str] = {
    "YSS-12345": "Tourmaline",
    "YSS-10001": "Diamond",
    "YSS-10002": "Sapphire",
    "YSS-10003": "Ruby",
    "YSS-10004": "Emerald",
    "YSS-10005": "Tanzanite",
    "YSS-10006": "Opal",
}

# ---------------------------------------------------------------------------
# Stone suitability table
# Fit values: "strong" | "good" | "conditional" | "avoid"
# Protection values: "low" | "medium" | "high"
# ---------------------------------------------------------------------------

STONE_TABLE: List[Dict[str, Any]] = [
    {
        "name": "Diamond",
        "color_families": ["Clear", "Yellow", "Pink", "Blue", "Black", "Brown", "Gray"],
        "ring_fit": "strong", "ring_protection": "low",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "strong",
    },
    {
        "name": "Sapphire",
        "color_families": ["Blue", "Pink", "Yellow", "Green", "Clear", "Purple", "Orange", "Gray", "Black", "Multicolor"],
        "ring_fit": "strong", "ring_protection": "low",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "strong",
    },
    {
        "name": "Ruby",
        "color_families": ["Red", "Pink"],
        "ring_fit": "strong", "ring_protection": "low",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Spinel",
        "color_families": ["Red", "Pink", "Blue", "Purple", "Gray", "Black", "Orange"],
        "ring_fit": "strong", "ring_protection": "low",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Emerald",
        "color_families": ["Green"],
        "ring_fit": "conditional", "ring_protection": "high",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Aquamarine",
        "color_families": ["Blue", "Green"],
        "ring_fit": "good", "ring_protection": "medium",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Morganite",
        "color_families": ["Pink", "Orange"],
        "ring_fit": "good", "ring_protection": "medium",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Tourmaline",
        "color_families": ["Green", "Pink", "Blue", "Red", "Black", "Yellow", "Brown", "Purple", "Multicolor"],
        "ring_fit": "conditional", "ring_protection": "high",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Garnet",
        "color_families": ["Red", "Green", "Orange", "Pink", "Purple", "Brown", "Yellow", "Black"],
        "ring_fit": "conditional", "ring_protection": "high",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Tsavorite",
        "color_families": ["Green"],
        "ring_fit": "conditional", "ring_protection": "high",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Alexandrite",
        "color_families": ["Green", "Red", "Purple", "Multicolor"],
        "ring_fit": "strong", "ring_protection": "low",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "strong",
    },
    {
        "name": "Tanzanite",
        "color_families": ["Blue", "Purple"],
        "ring_fit": "avoid", "ring_protection": "high",
        "earring_fit": "good", "pendant_fit": "strong", "bracelet_fit": "conditional",
    },
    {
        "name": "Topaz",
        "color_families": ["Blue", "Clear", "Pink", "Yellow", "Brown"],
        "ring_fit": "good", "ring_protection": "medium",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Amethyst",
        "color_families": ["Purple"],
        "ring_fit": "conditional", "ring_protection": "high",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Citrine",
        "color_families": ["Yellow", "Orange", "Brown"],
        "ring_fit": "conditional", "ring_protection": "high",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Peridot",
        "color_families": ["Green", "Yellow"],
        "ring_fit": "conditional", "ring_protection": "high",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Zircon",
        "color_families": ["Blue", "Clear", "Brown", "Pink", "Yellow", "Orange"],
        "ring_fit": "conditional", "ring_protection": "high",
        "earring_fit": "strong", "pendant_fit": "strong", "bracelet_fit": "good",
    },
    {
        "name": "Opal",
        "color_families": ["Clear", "Black", "Multicolor", "Blue", "Pink", "Gray"],
        "ring_fit": "avoid", "ring_protection": "high",
        "earring_fit": "good", "pendant_fit": "strong", "bracelet_fit": "conditional",
    },
    {
        "name": "Pearl",
        "color_families": ["Clear", "Pink", "Gray", "Black", "Yellow"],
        "ring_fit": "avoid", "ring_protection": "high",
        "earring_fit": "good", "pendant_fit": "strong", "bracelet_fit": "conditional",
    },
    {
        "name": "Moonstone",
        "color_families": ["Clear", "Pink", "Gray", "Multicolor"],
        "ring_fit": "avoid", "ring_protection": "high",
        "earring_fit": "good", "pendant_fit": "strong", "bracelet_fit": "conditional",
    },
]

# Quick lookup by name (case-insensitive key)
STONE_BY_NAME: Dict[str, Dict[str, Any]] = {s["name"].lower(): s for s in STONE_TABLE}

# All unique colors across the table
ALL_COLORS: List[str] = sorted({
    color
    for stone in STONE_TABLE
    for color in stone["color_families"]
})

# All stone names
ALL_STONE_NAMES: List[str] = [s["name"] for s in STONE_TABLE]
