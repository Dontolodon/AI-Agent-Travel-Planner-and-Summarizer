import os
from datetime import datetime, timedelta

from modules import (
    llm, pdf_parser, ocr, places, emailer, memory, cityinfo, season,
    validator, place_photos, pdf_export
)

SYSTEM_PROMPT = """You are an AI Travel Operations Agent.
You output clean, human-readable itineraries or summaries.
Never output JSON or code blocks unless explicitly asked.
You must follow formatting rules exactly.
You must not invent place names: use ONLY the allowed place names provided.
"""

def maybe_send_email(to_email: str | None, subject: str, body: str, attachments: list[str] | None = None):
    if to_email and to_email.strip():
        emailer.maybe_send_email(to_email.strip(), subject, body, attachments=attachments)

def _build_dates(start_date: str, days: int) -> list[str]:
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    return [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

def _ensure_places_used(itinerary_text: str, allowed_names: list[str]) -> str:
    if "places used" in itinerary_text.lower():
        return itinerary_text

    found = []
    lower_text = itinerary_text.lower()
    for name in allowed_names:
        if name and name.lower() in lower_text:
            found.append(name)

    block = "\nPlaces Used:\n" + "\n".join([f"- {n}" for n in found]) + "\n"
    return itinerary_text.rstrip() + "\n" + block

# ✅ add back for web_app import
def get_user_history(user_name: str) -> list[dict]:
    return memory.load_trip_history(user_name)

def summarize_file(input_path: str) -> str:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    lower = input_path.lower()
    if lower.endswith(".pdf"):
        raw_text = pdf_parser.extract_pdf_text(input_path)
        source_type = "PDF booking document"
    elif lower.endswith((".png", ".jpg", ".jpeg", ".webp")):
        raw_text = ocr.extract_image_text(input_path)
        source_type = "ticket screenshot or photo"
    else:
        raise ValueError("Unsupported file type. Use PDF or image.")

    user_prompt = f"""
Mode: Summarizer
Input type: {source_type}

Task:
- Extract key travel details only if clearly present (flight, airports, date/time, class, luggage).
- Do NOT guess or invent.
- Output bullet points grouped by: Flights, Hotels, Dates/Times, Luggage, Other.
Raw extracted text:
{raw_text[:8000]}
"""
    return llm.call_llm(SYSTEM_PROMPT, user_prompt, num_predict=320)

def plan_trip(city: str, start_date: str, days: int, user_name: str, vibe: str = "", fast: bool = True):
    info = cityinfo.get_city_info(city)
    if info is None:
        raise ValueError("City not found. Try 'City, Country' (e.g., 'Seoul, South Korea').")

    season_profile = season.build_season_profile(info, start_date)
    base_attractions = places.search_attractions(city, limit=8)
    allowed_names = [x.get("name", "") for x in base_attractions if x.get("name")]
    allowed_block = "\n".join([f"- {n}" for n in allowed_names])

    dates = _build_dates(start_date, days)

    history = memory.load_trip_history(user_name)[-5:]
    history_lines = [f"- {h.get('city')} ({h.get('start_date')}, {h.get('days')} days)" for h in history]
    history_block = "\n".join(history_lines) if history_lines else "(none)"

    # Scale output length with days to reduce truncation
    num_predict = min(2200, 350 + days * 330)

    prompt = f"""
Mode: Planner
User name: {user_name}
User trip history (last 5):
{history_block}

Destination: {city}
Travel dates: {dates}
Season notes: {season_profile["label"]} — {season_profile["notes"]}

User preferences (vibe):
{vibe.strip() if vibe.strip() else "(none)"}

Allowed places (use ONLY these exact names):
{allowed_block}

TASK:
Generate an itinerary for EXACTLY {days} days.

Hard Rules:
- Output MUST contain Day 1 through Day {days}. No missing days.
- Each day MUST have Morning / Afternoon / Evening.
- Use ONLY allowed place names (exact spelling).
- End with:
Places Used:
- <place name>
(list ALL places used)

FORMAT (must match):
Day 1 – YYYY-MM-DD
- Morning: ...
- Afternoon: ...
- Evening: ...
""".strip()

    last = ""
    for _attempt in range(3):
        itinerary = llm.call_llm(SYSTEM_PROMPT, prompt, num_predict=num_predict).strip()
        itinerary = _ensure_places_used(itinerary, allowed_names)

        if validator.validate_itinerary(itinerary, allowed_names, days) == "OK":
            last = itinerary
            break

        fixed = validator.auto_fix_itinerary(itinerary, allowed_names, days=days)
        if fixed:
            last = fixed
            break

        last = itinerary

    if last.strip().upper().startswith("FIX:"):
        raise RuntimeError("LLM output invalid after retries (returned FIX). Try again or reduce days/vibe length.")

    first_line = last.splitlines()[0] if last else ""
    memory.append_trip_history(user_name, city, start_date, days, first_line)

    return last, base_attractions

def export_plan_pdf(city: str, start_date: str, days: int, user_name: str, vibe: str, fast: bool):
    itinerary_text, base_attractions = plan_trip(city, start_date, days, user_name, vibe, fast=fast)

    used = validator.extract_places_used(itinerary_text)
    if not used:
        allowed_names = [x.get("name", "") for x in base_attractions if x.get("name")]
        lower_text = itinerary_text.lower()
        used = [n for n in allowed_names if n and n.lower() in lower_text]

    used_lower = {u.lower() for u in used}
    images = []
    attributions = []

    for item in base_attractions:
        name = item.get("name", "")
        if not name or name.lower() not in used_lower:
            continue

        photos = item.get("photos") or []
        if not photos:
            continue

        photo_ref = photos[0].get("photo_reference")
        if not photo_ref:
            continue

        img_path = place_photos.download_photo(photo_ref, name, max_width=900)
        if img_path:
            images.append((name, img_path))

        ha = photos[0].get("html_attributions") if isinstance(photos[0], dict) else None
        if ha:
            attributions.append(f"{name}: {str(ha)[:300]}")

        if len(images) >= 6:
            break

    safe_city = "".join([c for c in city if c.isalnum() or c in ("_", "-", " ")])[:40].strip().replace(" ", "_")
    filename = f"{safe_city}_{start_date}_{days}d.pdf"
    title = f"{days}-Day Itinerary — {city} (from {start_date})"

    pdf_path = pdf_export.export_itinerary_pdf(filename, title, itinerary_text, images, attributions)
    return pdf_path, itinerary_text
