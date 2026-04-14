# Ring Selection API — Payload Reference

Base URL: `http://127.0.0.1:8000`

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/upload-image` | Upload an inspiration image (optional, do this first if needed) |
| `POST` | `/api/ring-selection` | Submit ring questionnaire and get image prompt |

---

## POST `/api/ring-selection`

### Response (all branches return the same shape)

```json
{
  "summary": "Ring · Halo · White gold · Feminine · Sapphire (Excellent fit)",
  "image_prompt": "Create an image of ...",
  "cautions": "Avoid exposure to harsh chemicals."
}
```

> Pass `image_prompt` directly to your image generation model.

---

## Branch 1 — I already have a stone

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Feminine",
  "style_family": "Solitaire",
  "stone_branch": "Yes, I already have a stone",
  "own_stone": {
    "stone_type": "Sapphire",
    "color": "Deep blue",
    "shape": "Oval",
    "approximate_size": "2ct"
  },
  "metal": "White gold",
  "setting": "Sharp Claw / Prong Set",
  "wear_frequency": "Every day",
  "final_preferences": "Delicate band, low profile"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Masculine",
  "style_family": "Signet",
  "stone_branch": "Yes, I already have a stone",
  "own_stone": {
    "stone_type": "Ruby",
    "color": "Deep red",
    "shape": "Cushion",
    "approximate_size": "3ct"
  },
  "metal": "Yellow gold",
  "setting": "Bezel Set",
  "wear_frequency": "Special occasions",
  "final_preferences": "Bold, thick band, statement piece"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Balanced",
  "style_family": "Bezel",
  "stone_branch": "Yes, I already have a stone",
  "own_stone": {
    "stone_type": "Emerald",
    "color": "Vivid green",
    "shape": "Rectangle",
    "approximate_size": "1.5ct"
  },
  "metal": "Rose gold",
  "setting": "Bezel Set",
  "wear_frequency": "Often, but carefully",
  "final_preferences": "Art deco feel, geometric lines"
}
```

---

## Branch 2 — I have a YSS stone SKU

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Feminine",
  "style_family": "Three Stone",
  "stone_branch": "I have a YSS stone link or SKU",
  "yss_reference": "YSS-10001",
  "metal": "Platinum",
  "setting": "Rounded Claw / Prong Set",
  "wear_frequency": "Every day",
  "final_preferences": "Classic, timeless, no sharp edges"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Balanced",
  "style_family": "Vintage-Inspired",
  "stone_branch": "I have a YSS stone link or SKU",
  "yss_reference": "YSS-12345",
  "metal": "Yellow gold",
  "setting": "Half Bezel / Partial Frame",
  "wear_frequency": "Often, but carefully",
  "final_preferences": "Milgrain band, vintage feel"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Masculine",
  "style_family": "Contemporary Minimal",
  "stone_branch": "I have a YSS stone link or SKU",
  "yss_reference": "YSS-10002",
  "metal": "Platinum",
  "setting": "Bezel Set",
  "wear_frequency": "Every day",
  "final_preferences": "Flat band, zero embellishment, minimal"
}
```

> **Available YSS SKUs:**
> | SKU | Stone |
> |-----|-------|
> | `YSS-10001` | Diamond |
> | `YSS-10002` | Sapphire |
> | `YSS-10003` | Ruby |
> | `YSS-10004` | Emerald |
> | `YSS-10005` | Tanzanite |
> | `YSS-10006` | Opal |
> | `YSS-12345` | Tourmaline |

---

## Branch 3A — No stone, pick by stone name

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Feminine",
  "style_family": "Halo",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by stone",
  "chosen_stone_name": "Diamond",
  "metal": "Platinum",
  "setting": "Halo",
  "wear_frequency": "Every day",
  "final_preferences": "Classic, brilliant, timeless"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Feminine",
  "style_family": "Toi et Moi",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by stone",
  "chosen_stone_name": "Morganite",
  "metal": "Rose gold",
  "setting": "Rounded Claw / Prong Set",
  "wear_frequency": "Often, but carefully",
  "final_preferences": "Romantic, blush tones, soft curves"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Masculine",
  "style_family": "Signet",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by stone",
  "chosen_stone_name": "Alexandrite",
  "metal": "White gold",
  "setting": "Bezel Set",
  "wear_frequency": "Every day",
  "final_preferences": "Clean lines, flat profile, modern"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Balanced",
  "style_family": "Eternity",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by stone",
  "chosen_stone_name": "Sapphire",
  "metal": "Platinum",
  "setting": "Bezel Set",
  "wear_frequency": "Every day",
  "final_preferences": "Full eternity band, matching stones all around"
}
```

> **Available stone names:** Diamond · Sapphire · Ruby · Spinel · Emerald · Aquamarine · Morganite · Tourmaline · Garnet · Tsavorite · Alexandrite · Tanzanite · Topaz · Amethyst · Citrine · Peridot · Zircon · Opal · Pearl · Moonstone

---

## Branch 3B — No stone, pick by colour

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Feminine",
  "style_family": "Cluster",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by colour",
  "chosen_color": "Pink",
  "metal": "Rose gold",
  "setting": "Halo",
  "wear_frequency": "Special occasions",
  "final_preferences": "Floral cluster, delicate, romantic"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Masculine",
  "style_family": "Signet",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by colour",
  "chosen_color": "Blue",
  "metal": "Platinum",
  "setting": "Bezel Set",
  "wear_frequency": "Every day",
  "final_preferences": "Minimal, geometric, no embellishment"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Balanced",
  "style_family": "Solitaire",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by colour",
  "chosen_color": "Green",
  "metal": "Yellow gold",
  "setting": "Half Bezel / Partial Frame",
  "wear_frequency": "Often, but carefully",
  "final_preferences": "Nature-inspired, organic feel"
}
```

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Feminine",
  "style_family": "Vintage-Inspired",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by colour",
  "chosen_color": "Purple",
  "metal": "White gold",
  "setting": "Hidden Halo",
  "wear_frequency": "Special occasions",
  "final_preferences": "Victorian style, filigree details, ornate band"
}
```

> **Available colours:** Black · Blue · Brown · Clear · Gray · Green · Multicolor · Orange · Pink · Purple · Red · Yellow

---

## With inspiration image (any branch)

**Step 1** — upload the image first:

```
POST /api/upload-image
Content-Type: multipart/form-data
file: <your image file>
```

Response:
```json
{
  "image_url": "/uploads/abc123def456.jpg",
  "filename": "abc123def456.jpg"
}
```

**Step 2** — include the URL in your ring-selection payload:

```json
{
  "jewelry_type": "Ring",
  "style_direction": "Feminine",
  "style_family": "Vintage-Inspired",
  "stone_branch": "No, help me choose",
  "stone_choice_method": "Pick by stone",
  "chosen_stone_name": "Morganite",
  "metal": "Rose gold",
  "setting": "Hidden Halo",
  "wear_frequency": "Special occasions",
  "final_preferences": "Floral details, filigree band",
  "inspiration_image_url": "/uploads/abc123def456.jpg"
}
```

---

## Full enum reference

| Field | Valid values |
|-------|-------------|
| `jewelry_type` | `Ring` `Necklace / Pendant` `Bracelet` `Earrings` `Other` *(optional, defaults to Ring)* |
| `style_direction` | `Masculine` `Balanced` `Feminine` |
| `style_family` | `Solitaire` `Three Stone` `Halo` `Bezel` `Signet` `Cluster` `Toi et Moi` `Eternity` `Vintage-Inspired` `Contemporary Minimal` |
| `stone_branch` | `Yes, I already have a stone` `No, help me choose` `I have a YSS stone link or SKU` |
| `stone_choice_method` | `Pick by stone` `Pick by colour` *(only when stone_branch = No, help me choose)* |
| `metal` | `Yellow gold` `White gold` `Rose gold` `Platinum` |
| `setting` | `Sharp Claw / Prong Set` `Rounded Claw / Prong Set` `Bezel Set` `Half Bezel / Partial Frame` `Halo` `Hidden Halo` |
| `wear_frequency` | `Every day` `Often, but carefully` `Special occasions` |
| `final_preferences` | Any free text (optional) |
| `inspiration_image_url` | URL from `/api/upload-image` (optional) |

---

## Validation rules

| Condition | Required field |
|-----------|---------------|
| `stone_branch` = `Yes, I already have a stone` | `own_stone` object |
| `stone_branch` = `I have a YSS stone link or SKU` | `yss_reference` string |
| `stone_branch` = `No, help me choose` | `stone_choice_method` |
| `stone_choice_method` = `Pick by stone` | `chosen_stone_name` |
| `stone_choice_method` = `Pick by colour` | `chosen_color` |
