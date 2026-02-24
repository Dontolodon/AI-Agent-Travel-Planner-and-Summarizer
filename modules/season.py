TROPICAL_COUNTRIES = {
    "Indonesia", "Philippines", "Singapore", "Malaysia", "Thailand", "Vietnam", "Cambodia", "Laos", "Brunei",
}

def classify_climate(country: str, lat: float) -> str:
    if country in TROPICAL_COUNTRIES:
        return "tropical-monsoon"
    if abs(lat) < 23.5:
        return "tropical-generic"
    return "temperate-4-season"

def season_label_for_temperate(hemisphere: str, month: int) -> str:
    if hemisphere == "Northern":
        if month in (12, 1, 2): return "Winter"
        if month in (3, 4, 5): return "Spring"
        if month in (6, 7, 8): return "Summer"
        return "Autumn"
    else:
        if month in (12, 1, 2): return "Summer"
        if month in (3, 4, 5): return "Autumn"
        if month in (6, 7, 8): return "Winter"
        return "Spring"

def season_label_for_tropical_monsoon(country: str, month: int) -> str:
    if country == "Indonesia":
        return "Rainy season" if month in (11, 12, 1, 2, 3) else "Dry season"
    if country == "Philippines":
        if month in (12, 1, 2): return "Cool dry season"
        if month in (3, 4, 5): return "Hot dry season"
        return "Rainy season"
    return "Rainy season" if month in (11, 12, 1, 2, 3) else "Dry season"

def season_label_for_tropical_generic(month: int) -> str:
    return "Warm humid season" if month in (6, 7, 8, 9) else "Hot humid season"

def build_season_profile(city_info: dict, start_date: str) -> dict:
    country = city_info["country"]
    lat = city_info["latitude"]
    hemisphere = city_info["hemisphere"]
    month = int(start_date.split("-")[1])

    climate_type = classify_climate(country, lat)

    if climate_type == "temperate-4-season":
        label = season_label_for_temperate(hemisphere, month)
        notes = {
            "Winter": "Cold/short daylight: prefer indoor + short outdoor highlights.",
            "Summer": "Warm/hot: use mornings/evenings; avoid midday heat; hydrate.",
            "Spring": "Mild: great for parks and walking routes.",
            "Autumn": "Cooler: mix indoor/outdoor; possible autumn colors.",
        }[label]
    elif climate_type == "tropical-monsoon":
        label = season_label_for_tropical_monsoon(country, month)
        if "Rainy" in label:
            notes = "Humid with frequent rain: plan indoor-heavy with flexible backups."
        elif "Cool dry" in label:
            notes = "Relatively cooler/drier: great for outdoor sightseeing."
        elif "Hot dry" in label:
            notes = "Hot and sunny: avoid midday heat; shade breaks."
        else:
            notes = "Warm tropical: mix outdoor with indoor rest."
    else:
        label = season_label_for_tropical_generic(month)
        notes = "Warm/humid: mix outdoor with indoor rest."

    return {
        "climate_type": climate_type,
        "label": label,
        "hemisphere": hemisphere,
        "country": country,
        "notes": notes,
    }
