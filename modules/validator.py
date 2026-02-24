import re
from modules import llm

VALIDATE_PROMPT = """You are a strict validator.
You will ONLY respond with either:
- OK
or
- FIX: <short correction instruction>
"""

def extract_places_used(text: str) -> list[str]:
    m = re.search(r"Places Used:\s*(.*)", text, re.IGNORECASE | re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    lines = block.splitlines()
    places = []
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("-"):
            places.append(ln.lstrip("-").strip())
        if ln.lower().startswith("notes:") or ln.lower().startswith("tips:"):
            break
    return [p for p in places if p]

def count_days(text: str) -> int:
    return len(re.findall(r"^\s*Day\s+\d+\s*[–-]\s*\d{4}-\d{2}-\d{2}\s*$", text, re.MULTILINE))

def validate_itinerary(itinerary_text: str, allowed_place_names: list[str], days: int) -> str:
    allowed_set = {p.strip().lower() for p in allowed_place_names if p}

    dcount = count_days(itinerary_text)
    if dcount != days:
        return f"FIX: Itinerary must contain exactly Day 1 through Day {days} with YYYY-MM-DD (no missing days)."

    used = extract_places_used(itinerary_text)
    if not used:
        return "FIX: Add a final section 'Places Used:' with bullet list of ALL places used (only allowed list)."

    bad = [p for p in used if p.strip().lower() not in allowed_set]
    if bad:
        return "FIX: Replace non-allowed place names in itinerary and Places Used with the closest allowed places."

    return "OK"

def auto_fix_itinerary(itinerary_text: str, allowed_place_names: list[str], days: int) -> str | None:
    """
    Returns corrected itinerary text, or None if it couldn't be fixed safely.
    """
    verdict = validate_itinerary(itinerary_text, allowed_place_names, days)
    if verdict == "OK":
        return itinerary_text

    fix_prompt = f"""
Allowed places (use ONLY these exact names):
{allowed_place_names}

Required days: {days}

Here is the itinerary:
{itinerary_text}

Instruction:
{verdict}

Return ONLY the corrected itinerary text (NOT 'OK', NOT 'FIX:').
"""
    corrected = llm.call_llm(VALIDATE_PROMPT, fix_prompt, num_predict=520).strip()

    # Critical guard: never pass FIX/OK into PDF as itinerary
    if not corrected or corrected.upper() == "OK" or corrected.upper().startswith("FIX:"):
        return None

    # Ensure the corrected result is actually valid
    if validate_itinerary(corrected, allowed_place_names, days) != "OK":
        return None

    return corrected
