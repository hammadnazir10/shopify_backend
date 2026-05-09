"""Visual-descriptor lookups used to translate questionnaire answers
into rich, prompt-engineered design language."""

# ---------------------------------------------------------------------------
# Metals
# ---------------------------------------------------------------------------

METAL_FINISH = {
    "Yellow gold": (
        "warm 18-karat yellow gold, high-polish mirror finish, deep amber-gold "
        "reflections, classic warm tone"
    ),
    "White gold": (
        "cool 18-karat white gold, rhodium-plated mirror finish, icy silver-white "
        "surface, sharp edge definition"
    ),
    "Rose gold": (
        "blush 18-karat rose gold, warm satin-to-mirror finish, soft copper-pink "
        "hue, romantic warm reflections"
    ),
    "Platinum": (
        "950 platinum, cool weighty reflective finish, bright silver-white tone, "
        "dense and lustrous surface"
    ),
}

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

SETTING_DETAIL = {
    "Sharp Claw / Prong Set": (
        "sharp talon-style prong setting, four or six pointed steel-like claws "
        "gripping the girdle, maximum stone exposure, dramatic claw shadows, "
        "brilliant light entry from all angles"
    ),
    "Rounded Claw / Prong Set": (
        "rounded claw prong setting, soft dome-tipped four or six prongs, classic "
        "elegant grip, stone fully visible from crown to girdle, smooth claw edges "
        "catching light gently"
    ),
    "Bezel Set": (
        "full bezel setting, continuous metal collar wrapped flush around the stone "
        "girdle, smooth seamless metal wall, ultra-modern and protective, clean "
        "geometric profile"
    ),
    "Half Bezel / Partial Frame": (
        "half-bezel partial frame setting, metal frames two opposing sides of the "
        "stone, east and west flanks open to light, contemporary architectural look, "
        "floating stone effect"
    ),
    "Halo": (
        "halo setting, tight micro-pavé ring of accent stones circling the centre "
        "stone, amplified perceived size, extra brilliance from surrounding diamonds, "
        "glittering frame effect"
    ),
    "Hidden Halo": (
        "hidden halo setting, pavé accent ring tucked just below the crown out of "
        "top view, clean minimalist top profile, surprise glitter revealed from side "
        "angle, dual-look design"
    ),
}

# ---------------------------------------------------------------------------
# Wear context
# ---------------------------------------------------------------------------

WEAR_CONTEXT = {
    "Every day": (
        "daily all-day wear, low-profile slim build, durable construction, no sharp "
        "snag points, practical elegance"
    ),
    "Often, but carefully": (
        "frequent mindful wear, moderate profile, elegant proportions balanced with "
        "wearability"
    ),
    "Special occasions": (
        "special-occasion statement piece, elevated presence, expressive design, "
        "maximum visual impact"
    ),
}

# ---------------------------------------------------------------------------
# Style direction
# ---------------------------------------------------------------------------

DIRECTION_DETAIL = {
    "Masculine": (
        "bold strong architectural lines, substantial weight and band width, "
        "confident commanding presence"
    ),
    "Balanced": (
        "gender-neutral refined proportions, versatile neither heavy nor delicate, "
        "clean universal elegance"
    ),
    "Feminine": (
        "delicate graceful softly curved forms, featherlight romantic silhouette, "
        "intricate fine detail"
    ),
}

# ---------------------------------------------------------------------------
# Style families
# ---------------------------------------------------------------------------

STYLE_FAMILY_VISUAL = {
    "Solitaire": (
        "single-stone solitaire design, uninterrupted tapered band, all attention "
        "on centre stone, minimalist elegant profile, timeless clean lines, stone "
        "elevated on a slim shank"
    ),
    "Three Stone": (
        "three-stone trilogy design, flanking side stones graduated in size, "
        "balanced symmetrical composition, past-present-future symbolism, trio of "
        "glittering focal points"
    ),
    "Halo": (
        "halo design, centre stone surrounded by micro-pavé accent ring, enhanced "
        "perceived size, brilliant light cascade, layered glittering composition"
    ),
    "Bezel": (
        "bezel-set design, metal collar encasing the stone flush, smooth geometric "
        "outline, modern architectural aesthetic, clean protective band"
    ),
    "Signet": (
        "signet ring design, wide flat-top table face, substantial band width, bold "
        "heraldic presence, engraving-ready surface, strong sculptural silhouette"
    ),
    "Cluster": (
        "cluster design, multiple smaller stones arranged to mimic a single large "
        "stone, mosaic of glittering facets, vintage garden-party aesthetic, dense "
        "sparkling surface"
    ),
    "Toi et Moi": (
        "toi et moi two-stone design, two distinct stones side by side on a split "
        "fork shank, romantic duality, asymmetric or mirrored composition, intimate "
        "symbolic pairing"
    ),
    "Eternity": (
        "full eternity band design, stones set continuously all the way around the "
        "band, unbroken circle of gemstones, infinite loop symbolism, uniform pavé "
        "or prong row, seamless glittering circumference, low-profile stackable band"
    ),
    "Vintage-Inspired": (
        "vintage-inspired design, intricate milgrain border edging, filigree "
        "scrollwork gallery, Art Deco or Edwardian detailing, hand-engraved surface "
        "texture, antique romantic character, ornate craftsmanship referencing early "
        "20th century jewellery"
    ),
    "Contemporary Minimal": (
        "contemporary minimal design, clean geometric lines, deliberate negative "
        "space, architectural simplicity, no superfluous decoration, sculptural "
        "modern form"
    ),
}

# ---------------------------------------------------------------------------
# Stones
# ---------------------------------------------------------------------------

STONE_VISUAL = {
    "diamond": (
        "colourless to near-colourless diamond, brilliant-cut faceting, exceptional "
        "fire and dispersion, rainbow spectral flashes, eye-clean clarity, adamantine "
        "luster, scintillating brilliance"
    ),
    "sapphire": (
        "sapphire gemstone, vitreous glassy luster, strong saturation, silk-like "
        "needle inclusions giving velvety depth, excellent transparency, sharp facet "
        "reflections, no optical phenomena unless star-cut"
    ),
    "ruby": (
        "ruby gemstone, intense red with fluorescent glow under sunlight, vitreous "
        "luster, strong chromatic saturation, deep colour zoning, velvety silk needle "
        "inclusions, highly valued brilliance"
    ),
    "emerald": (
        "emerald gemstone, rich verdant green, characteristic jardin inclusions giving "
        "depth, vitreous to resinous luster, slightly waxy surface quality, step-cut "
        "faceting typical, garden-like inner landscape"
    ),
    "morganite": (
        "morganite gemstone, soft peachy-pink to blush tone, excellent transparency, "
        "vitreous luster, gentle pastel saturation, warm feminine hue, typically "
        "cushion or oval cut to maximise colour"
    ),
    "aquamarine": (
        "aquamarine gemstone, clear sky-blue to sea-blue tone, excellent transparency, "
        "vitreous glassy luster, clean eye-clear clarity, cool refreshing hue, "
        "typically emerald or oval cut"
    ),
    "tanzanite": (
        "tanzanite gemstone, vivid blue-violet to deep purple-blue, strong pleochroism "
        "showing blue, violet and burgundy at different angles, vitreous luster, rich "
        "colour depth"
    ),
    "opal": (
        "opal gemstone, vivid play-of-colour with rainbow spectral flash, waxy to "
        "vitreous luster, unique shifting colour patterns, dynamic colour-shift "
        "phenomenon visible across the surface"
    ),
    "pearl": (
        "pearl, smooth creamy surface, orient luster with pearlescent iridescence, "
        "warm white to ivory to pink overtone, classic organic gem, soft diffused "
        "light interaction, smooth tactile surface"
    ),
    "tourmaline": (
        "tourmaline gemstone, broad colour range, strong vitreous luster, excellent "
        "transparency, rich colour saturation, sometimes bicolour or watermelon effect"
    ),
    "garnet": (
        "garnet gemstone, deep rich colour, high refractive index giving strong "
        "brilliance, vitreous to adamantine luster, excellent colour depth, typically "
        "round or cushion cut"
    ),
    "amethyst": (
        "amethyst gemstone, rich purple to violet tone, excellent transparency, "
        "vitreous luster, strong colour saturation, typical faceted oval or cushion cut"
    ),
    "moonstone": (
        "moonstone gemstone, adularescence phenomenon — blue-white floating inner "
        "glow, translucent to semi-transparent body, soft milky-white base tone, "
        "ethereal floating light effect shifting with viewing angle"
    ),
    "alexandrite": (
        "alexandrite gemstone, dramatic colour-shift from green in daylight to "
        "red-purple under incandescent light, strong pleochroism, vitreous luster, "
        "exceptional colour-change phenomenon"
    ),
    "spinel": (
        "spinel gemstone, vivid saturated colour, strong vitreous luster, excellent "
        "transparency and brilliance, no optical phenomena, pure clean hue"
    ),
    "topaz": (
        "topaz gemstone, excellent transparency, vitreous luster, clean eye-clear "
        "clarity, strong colour saturation depending on variety, typically brilliant "
        "or step cut"
    ),
    "citrine": (
        "citrine gemstone, warm golden-yellow to orange-brown tone, excellent "
        "transparency, vitreous luster, cheerful warm colour, typically faceted oval "
        "or cushion cut"
    ),
    "peridot": (
        "peridot gemstone, distinctive lime-green to olive-green tone, vitreous "
        "luster, slight oily appearance, characteristic yellowish-green hue"
    ),
    "zircon": (
        "zircon gemstone, exceptionally high refractive index giving diamond-like "
        "fire, strong dispersion and brilliance, vitreous to adamantine luster, sharp "
        "facet contrast"
    ),
    "tsavorite": (
        "tsavorite garnet gemstone, intense vivid emerald-green, high refractive "
        "index giving exceptional brilliance, strong clean colour with no jardin "
        "inclusions unlike emerald"
    ),
}

# ---------------------------------------------------------------------------
# Stone colours
# ---------------------------------------------------------------------------

STONE_COLOR_VISUAL = {
    "pink": "soft blush-pink to vivid hot-pink saturation, romantic feminine hue, warm peachy-pink undertone",
    "blue": "cornflower-blue to deep royal-blue, cool vivid saturation, icy clarity",
    "red": "deep crimson to vivid blood-red, intense saturated red, fiery warm hue",
    "green": "rich forest-green to vivid emerald-green, cool deep saturation, lush verdant tone",
    "purple": "deep violet to vivid plum-purple, rich cool saturation, regal hue",
    "yellow": "warm golden-yellow to vivid canary-yellow, bright sunny saturation",
    "orange": "warm burnt-orange to vivid mandarin-orange, rich earthy saturation",
    "clear": "near-colourless to completely transparent, crystal-clear body, white-light brilliance",
    "black": "deep opaque black, high-polish surface, dramatic light absorption, bold contrast",
    "white": "milky white to soft ivory tone, translucent glow, pearl-like luminosity",
    "multicolor": "multicolour play-of-colour, shifting spectral hues, dynamic colour movement",
    "gray": "cool silver-gray tone, subtle neutral saturation, sophisticated muted hue",
    "brown": "warm cognac to earthy brown tone, rich organic saturation",
}

# ---------------------------------------------------------------------------
# Inspiration keyword → visual translation
# ---------------------------------------------------------------------------

KEYWORD_VISUAL = {
    "minimal": "clean uncluttered composition, deliberate negative space, no superfluous ornament, refined restraint",
    "minimalist": "clean uncluttered composition, deliberate negative space, no superfluous ornament, refined restraint",
    "vintage": "antique patina feel, milgrain bead edging, filigree scrollwork, Art Deco angular geometry or Edwardian florets",
    "vintage_feel": "subtle antique character, delicate milgrain border, softly ornate gallery detail, heirloom quality craftsmanship",
    "romantic": "soft curved lines, floral motif accents, dreamy feminine silhouette, warm intimate mood",
    "bold": "substantial band width, dramatic stone presence, strong visual weight, high-contrast composition",
    "modern": "geometric angular lines, architectural negative space, contemporary sculptural form",
    "classic": "timeless proportions, traditional four-prong solitaire silhouette, enduring elegant design",
    "luxury": "ultra-fine pavé grain, polished mirror surfaces, impeccable craftsmanship, premium material finish",
    "delicate": "fine slim band, featherlight proportions, intricate fine detail, graceful narrow profile",
    "nature": "organic flowing curves, leaf or floral motif, botanical sculptural form, nature-inspired silhouette",
    "geometric": "angular precise faceting, sharp edge definition, mathematical symmetry, hard-line architectural form",
    "celestial": "star and crescent motifs, ethereal cosmic feel, scattered pavé like a night sky, dreamy otherworldly mood",
    "edgy": "asymmetric composition, unconventional angular form, dark dramatic mood, avant-garde silhouette",
    "bohemian": "organic free-form design, earthy tone palette, textured hammered metal surface, handcrafted artisanal feel",
    "art_deco": "geometric Art Deco symmetry, stepped baguette accent stones, platinum-era architectural precision, 1920s glamour",
    "floral": "floral petal-shaped prongs, botanical scrollwork gallery, flower-head cluster composition, garden-party aesthetic",
}

# ---------------------------------------------------------------------------
# Photography requirements per jewelry type
# ---------------------------------------------------------------------------

PHOTOGRAPHY_REQUIREMENTS = {
    "Ring": [
        "Show the ring upright, band resting on a flat surface or elevated on a clear acrylic stand",
        "Camera angle: 45-degree three-quarter hero shot showing both the face and the band profile",
        "The stone and setting must be the dominant focal point, tack-sharp",
        "Interior of the band may be slightly visible to show craftsmanship",
        "Never show the ring lying flat or top-down only",
        "Single ring centred in frame with elegant negative space around it",
    ],
    "Bracelet": [
        "Show the bracelet in an open oval or slightly curved form, as if resting on a wrist",
        "Camera angle: slight elevated 3/4 angle to show both the face and the curve of the bracelet",
        "The clasp or closure should be visible but not the focal point",
        "Full length of the bracelet must be visible — never cropped",
        "If chain or link style: individual links must be distinguishable and sharp",
        "If bangle style: circular silhouette shown with depth, not flat-on",
        "Placed on a clean surface or floating with soft shadow beneath",
    ],
    "Earrings": [
        "Show BOTH earrings hanging vertically, suspended from a thin wire/hook visible at the top",
        "Earrings must face the viewer front-on, dangling downward naturally under gravity",
        "The ear wire, post, or hook must be visible at the very top of each piece",
        "Full drop length of the earring must be visible from top finding to lowest point",
        "Camera angle: straight-on front view OR very slight 3/4 angle, never top-down, never flat lay",
        "If drop/chandelier/halo/cluster style: show the full articulated hang and movement",
        "If stud style: show the stud face-on with slight elevation to reveal setting depth",
        "Pair presented side-by-side with a natural gap between them",
    ],
    "Necklace / Pendant": [
        "Show the necklace/pendant hanging vertically, chain draped in a natural U-curve",
        "The pendant must be the focal point, centred and hanging at the lowest point of the chain",
        "Camera angle: straight-on front view showing the full chain length and pendant",
        "Chain links or rope texture must be visible and sharp",
        "Full length from clasp to pendant tip must be visible — never cropped",
        "If layered or multi-strand: each strand clearly separated and distinguishable",
        "Hanging against a clean background or draped over a soft surface for depth",
    ],
}
